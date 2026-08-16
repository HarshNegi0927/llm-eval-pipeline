"""Prints every failing case from the most recent eval run, with enough
detail to diagnose WHY it failed — wrong category, weak summary score
(judge < 4), or both. The pass/fail line during a run only tells you THAT
something failed; this is where you see why.

Usage:
    python scripts/show_failures.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.run_store import get_latest_run

if __name__ == "__main__":
    run = get_latest_run()
    if run is None:
        print("No saved runs found — run scripts/run_eval.py first.")
        sys.exit(0)

    failed = [r for r in run.results if not r.passed]
    print(
        f"Run {run.summary.run_id} ({run.summary.prompt_version}) — "
        f"{len(failed)} failing case(s) of {run.summary.total_cases}\n"
    )

    for r in failed:
        if r.error:
            print(f"[{r.test_case_id}] ERROR: {r.error}\n")
            continue

        cat_flag = "category OK" if r.category_match else "category MISMATCH"
        print(
            f"[{r.test_case_id}] {cat_flag} "
            f"(expected={r.expected_category}, got={r.actual_category})  "
            f"|  summary_score={r.summary_score}/5"
        )
        print(f"  Input:            {r.input}")
        print(f"  Expected summary: {r.expected_summary}")
        print(f"  Actual summary:   {r.actual_summary}")
        print()
