"""CI entry point: runs eval for one or more prompt versions, writes a
markdown summary (posted as a PR comment by the workflow), and exits
non-zero if ANY run shows a CRITICAL regression — which fails the GitHub
Actions check and blocks merge if it's set as a required check.

Reuses every piece already built and tested in Phases 3-4 (run_eval_async,
compare_runs, check_drift, generate_html_report, send_slack_alert) — this
file is pure orchestration for the CI context, no new eval logic.

Usage:
    python scripts/ci_run_eval.py v2 v3
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


async def run_one(prompt_version: str) -> tuple[str, bool]:
    """Returns (markdown_summary, is_critical)."""
    previous_run = get_latest_run()
    run = await run_eval_async(prompt_version)
    save_run(run)
    s = run.summary

    lines = [f"### `{prompt_version}` — {s.passed}/{s.total_cases} passed ({s.pass_rate:.1%})"]
    for cat, acc in sorted(s.category_accuracy.items()):
        lines.append(f"- {cat}: {acc:.1%}")

    comparison = None
    is_critical = False
    if previous_run is not None and previous_run.summary.run_id != s.run_id:
        comparison = compare_runs(previous_run, run)
        is_critical = comparison.severity == "critical"
        lines.append(
            f"\n**vs `{previous_run.summary.prompt_version}`** "
            f"({previous_run.summary.run_id}): {comparison.pass_rate_delta:+.1%} "
            f"— **{comparison.severity.upper()}**"
        )
        if comparison.regressions:
            lines.append(f"\n🔻 **{len(comparison.regressions)} regression(s):**")
            for d in comparison.regressions:
                lines.append(f"  - `{d.test_case_id}`: {d.old_category} → {d.new_category}")
        if comparison.improvements:
            lines.append(f"\n🔺 {len(comparison.improvements)} improvement(s)")
    else:
        lines.append("\n_No previous run to compare against — this is a baseline._")

    history = list_runs()
    drift_warning = check_drift(history)
    if drift_warning:
        lines.append(f"\n🐌 {drift_warning}")

    report_html = generate_html_report(run, previous_run, comparison, history, drift_warning)
    report_path = save_report(report_html, s.run_id)
    lines.append(f"\n📄 Report artifact: `{report_path.name}`")

    send_slack_alert(run, comparison, report_path, drift_warning)

    return "\n".join(lines), is_critical


async def main(versions: list[str]) -> None:
    summary_path = Path("ci_summary.md")

    if not versions:
        print("No prompt files changed in this PR — nothing to evaluate.")
        summary_path.write_text("No prompt files changed in this PR.", encoding="utf-8")
        sys.exit(0)

    summaries = []
    any_critical = False
    for v in versions:
        print(f"\n=== Evaluating prompt version '{v}' ===")
        summary, is_critical = await run_one(v)
        print(summary)
        summaries.append(summary)
        any_critical = any_critical or is_critical

    summary_path.write_text("\n\n---\n\n".join(summaries), encoding="utf-8")

    if any_critical:
        print("\n🚨 CRITICAL regression detected in at least one prompt version — failing the check.")
        sys.exit(1)

    print("\n✅ No critical regressions.")
    sys.exit(0)


if __name__ == "__main__":
    versions = sys.argv[1:]
    asyncio.run(main(versions))
