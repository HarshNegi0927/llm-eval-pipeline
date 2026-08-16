"""Run the golden dataset against a prompt version, save the run, diff
against the most recent prior run, generate an HTML report, check for slow
drift across history, and (if configured) send a Slack alert.

Usage:
    python scripts/run_eval.py v1
    python scripts/run_eval.py v2

Needs a real GROQ_API_KEY in .env — this makes real API calls (2 per test
case: classify + judge, so ~170 calls for the 85-case dataset). If you hit
rate-limit errors on a free tier, check src/rate_limiter.py's settings.
Slack alerting is optional — set SLACK_WEBHOOK_URL in .env to enable it.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.comparison import check_drift, compare_runs
from src.eval_engine import run_eval_async
from src.report import generate_html_report, save_report
from src.run_store import get_latest_run, list_runs, save_run
from src.slack_alert import send_slack_alert


async def main(prompt_version: str) -> None:
    print(f"Running eval for prompt version '{prompt_version}' against the golden dataset...")
    print(
        "Rate-limited to Groq's free tier (30 req/min, 6,000 tokens/min) — "
        "an 85-case run makes ~170 calls, so this legitimately takes several "
        "minutes. Progress prints below as each case finishes. Don't Ctrl+C; "
        "gaps between lines are the rate limiter waiting, not a hang.\n"
    )
    previous_run = get_latest_run()  # most recent run overall, before this one

    run = await run_eval_async(prompt_version)
    save_run(run)

    s = run.summary
    print(f"\nRun {s.run_id} saved")
    print(f"Prompt: {s.prompt_version}  |  Model: {s.model}")
    print(f"Pass rate: {s.passed}/{s.total_cases} ({s.pass_rate:.1%})")
    print("Category accuracy:")
    for cat, acc in sorted(s.category_accuracy.items()):
        print(f"  {cat:<10} {acc:.1%}")
    print(f"Avg summary score: {s.avg_summary_score:.2f}/5")
    print(f"Avg latency: {s.avg_latency_ms:.0f}ms")
    print(f"Tokens used: {s.total_input_tokens} in / {s.total_output_tokens} out")
    if s.error_count:
        print(f"⚠️  {s.error_count} case(s) errored (bad JSON / validation failure)")

    comparison = None
    if previous_run is not None and previous_run.summary.run_id != s.run_id:
        comparison = compare_runs(previous_run, run)
        print(
            f"\n--- Diff vs run {previous_run.summary.run_id} "
            f"(prompt {previous_run.summary.prompt_version}) ---"
        )
        print(f"Pass rate delta: {comparison.pass_rate_delta:+.1%}")
        print(f"Severity: {comparison.severity.upper()}")

        if comparison.regressions:
            print(f"\n{len(comparison.regressions)} REGRESSION(S):")
            for d in comparison.regressions:
                print(f"  - {d.test_case_id}: was passing, now failing ({d.old_category} -> {d.new_category})")

        if comparison.improvements:
            print(f"\n{len(comparison.improvements)} improvement(s):")
            for d in comparison.improvements:
                print(f"  - {d.test_case_id}: now passing ({d.old_category} -> {d.new_category})")
    else:
        print("\nNo previous run to compare against — this is your baseline.")

    # Drift check runs over ALL history, independent of the single-run diff above.
    history = list_runs()
    drift_warning = check_drift(history)
    if drift_warning:
        print(f"\n🐌 {drift_warning}")

    report_html = generate_html_report(run, previous_run, comparison, history, drift_warning)
    report_path = save_report(report_html, s.run_id)
    print(f"\nHTML report: {report_path}")

    sent = send_slack_alert(run, comparison, report_path, drift_warning)
    if sent:
        print("Slack alert sent.")
    else:
        print("Slack alert skipped (no SLACK_WEBHOOK_URL set in .env).")


if __name__ == "__main__":
    version = sys.argv[1] if len(sys.argv) > 1 else "v1"
    asyncio.run(main(version))