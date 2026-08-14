"""Structural tests for the golden dataset.

These don't test model quality — they test that the dataset itself is
well-formed: unique IDs, no duplicate inputs, reasonable category/difficulty
coverage. Catches copy-paste mistakes before they corrupt eval runs.
"""
from collections import Counter

from src.golden_dataset import load_golden_dataset


def test_dataset_loads_and_has_minimum_size():
    dataset = load_golden_dataset("v1")
    assert len(dataset.test_cases) >= 50


def test_all_ids_are_unique():
    dataset = load_golden_dataset("v1")
    ids = [tc.id for tc in dataset.test_cases]
    assert len(ids) == len(set(ids)), "Duplicate test case IDs found"


def test_no_duplicate_inputs():
    dataset = load_golden_dataset("v1")
    inputs = [tc.input.strip().lower() for tc in dataset.test_cases]
    assert len(inputs) == len(set(inputs)), "Duplicate email inputs found"


def test_all_four_categories_represented():
    dataset = load_golden_dataset("v1")
    categories = {tc.expected_category for tc in dataset.test_cases}
    assert categories == {"billing", "technical", "account", "general"}


def test_edge_cases_exist():
    """The golden dataset must include deliberately hard cases, not just easy ones."""
    dataset = load_golden_dataset("v1")
    difficulty_counts = Counter(tc.difficulty for tc in dataset.test_cases)
    assert difficulty_counts["edge"] >= 5, "Need more deliberately hard/edge cases"


def test_every_case_has_a_non_empty_expected_summary():
    dataset = load_golden_dataset("v1")
    for tc in dataset.test_cases:
        assert tc.expected_summary.strip(), f"{tc.id} has an empty expected_summary"
