"""Human review helper for the golden dataset.

Run this, read every case, and fix anything wrong directly in the JSON file
(expected_category, expected_summary, difficulty — whatever's off). This
script does not modify the dataset; it's a reading aid + a coverage check.

Usage:
    python scripts/review_dataset.py
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.golden_dataset import load_golden_dataset

if __name__ == "__main__":
    dataset = load_golden_dataset("v1")
    cases = dataset.test_cases

    print(f"Golden dataset v1 — {len(cases)} test cases\n")

    for tc in cases:
        print(f"[{tc.id}] ({tc.expected_category} / {tc.difficulty})")
        print(f"  Input:    {tc.input}")
        print(f"  Expected: {tc.expected_summary}")
        if tc.notes:
            print(f"  Notes:    {tc.notes}")
        print()

    cat_counts = Counter(tc.expected_category for tc in cases)
    diff_counts = Counter(tc.difficulty for tc in cases)
    verified_count = sum(1 for tc in cases if tc.human_verified)

    print("=" * 50)
    print("Category distribution:", dict(cat_counts))
    print("Difficulty distribution:", dict(diff_counts))
    print(f"Human-verified so far: {verified_count}/{len(cases)}")
    if verified_count < len(cases):
        print(
            "⚠️  Not all cases are human_verified yet. Read each one above, "
            "fix anything wrong in golden_dataset/v1.json, then set "
            "\"human_verified\": true on the ones you've confirmed."
        )
