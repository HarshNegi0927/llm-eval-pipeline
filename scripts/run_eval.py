"""Run the golden dataset against a prompt version, save the run, and diff
against the most recent prior run (if any).

Usage:
    python scripts/run_eval.py v1
    python scripts/run_eval.py v2

Needs a real GROQ_API_KEY in .env — this makes real API calls (2 per test
case: classify + judge, so ~170 calls for the 85-case dataset). If you hit
rate-limit errors on a free tier, lower MAX_CONCURRENT_REQUESTS in
src/eval_engine.py.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.comparison import compare_runs
from src.eval_engine import run_eval_async
from src.run_store import get_latest_run, save_run


async def main(prompt_version: str) -> None:
    print(f"Running eval for prompt version '{prompt_version}' against the golden dataset...")
    previous_run = get_latest_run()  # most recent run overall, before this one

    run = await run_eval_async(prompt_version)
    saved_path = save_run(run)

    s = run.summary
    print(f"\nRun {s.run_id} saved to {saved_path}")
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

    if previous_run is None or previous_run.summary.run_id == s.run_id:
        print("\nNo previous run to compare against — this is your baseline.")
        return

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


if __name__ == "__main__":
    version = sys.argv[1] if len(sys.argv) > 1 else "v1"
    asyncio.run(main(version))
