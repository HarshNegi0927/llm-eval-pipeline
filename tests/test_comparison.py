"""Tests for comparison.py — pure logic, no LLM calls involved at all.
Builds fake EvalRun objects directly to test diffing and threshold math.
"""
from src.comparison import compare_runs
from src.eval_engine import EvalCaseResult, EvalRun, EvalRunSummary


def _case(tc_id, expected_category, actual_category, score=5):
    return EvalCaseResult(
        test_case_id=tc_id,
        input="irrelevant",
        expected_category=expected_category,
        expected_summary="irrelevant",
        difficulty="easy",
        actual_category=actual_category,
        actual_summary="irrelevant",
        category_match=(expected_category == actual_category),
        summary_score=score,
        latency_ms=100.0,
        input_tokens=10,
        output_tokens=5,
    )


def _run(run_id, results, prompt_version="v1"):
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    return EvalRun(
        summary=EvalRunSummary(
            run_id=run_id,
            prompt_version=prompt_version,
            dataset_version="v1",
            model="test-model",
            timestamp="2026-08-14T00:00:00Z",
            total_cases=total,
            passed=passed,
            pass_rate=(passed / total if total else 0.0),
            category_accuracy={},
            avg_summary_score=5.0,
            avg_latency_ms=100.0,
            total_input_tokens=0,
            total_output_tokens=0,
            error_count=0,
        ),
        results=results,
    )


def test_detects_a_regression():
    baseline = _run("run_a", [_case("tc_1", "billing", "billing")])
    new = _run("run_b", [_case("tc_1", "billing", "technical")])

    diff = compare_runs(baseline, new)

    assert len(diff.regressions) == 1
    assert diff.regressions[0].test_case_id == "tc_1"
    assert len(diff.improvements) == 0


def test_detects_an_improvement():
    baseline = _run("run_a", [_case("tc_1", "billing", "technical")])
    new = _run("run_b", [_case("tc_1", "billing", "billing")])

    diff = compare_runs(baseline, new)

    assert len(diff.improvements) == 1
    assert len(diff.regressions) == 0


def test_unchanged_cases_are_not_flagged_either_way():
    baseline = _run("run_a", [_case("tc_1", "billing", "billing")])
    new = _run("run_b", [_case("tc_1", "billing", "billing")])

    diff = compare_runs(baseline, new)

    assert len(diff.regressions) == 0
    assert len(diff.improvements) == 0


def test_new_test_case_not_in_baseline_is_skipped_not_crashed():
    baseline = _run("run_a", [_case("tc_1", "billing", "billing")])
    new = _run(
        "run_b",
        [_case("tc_1", "billing", "billing"), _case("tc_new", "technical", "technical")],
    )

    diff = compare_runs(baseline, new)  # should not raise
    assert len(diff.regressions) == 0


def test_severity_is_critical_above_8_percent_drop():
    baseline_results = [_case(f"tc_{i}", "billing", "billing") for i in range(10)]
    new_results = [_case(f"tc_{i}", "billing", "billing") for i in range(9)]
    new_results.append(_case("tc_9", "billing", "technical"))  # 1/10 = 10% drop

    diff = compare_runs(_run("run_a", baseline_results), _run("run_b", new_results))

    assert diff.severity == "critical"


def test_severity_is_warning_between_3_and_8_percent_drop():
    baseline_results = [_case(f"tc_{i}", "billing", "billing") for i in range(20)]
    new_results = [_case(f"tc_{i}", "billing", "billing") for i in range(19)]
    new_results.append(_case("tc_19", "billing", "technical"))  # 1/20 = 5% drop

    diff = compare_runs(_run("run_a", baseline_results), _run("run_b", new_results))

    assert diff.severity == "warning"


def test_severity_is_ok_below_3_percent_drop():
    baseline_results = [_case(f"tc_{i}", "billing", "billing") for i in range(100)]
    new_results = [_case(f"tc_{i}", "billing", "billing") for i in range(99)]
    new_results.append(_case("tc_99", "billing", "technical"))  # 1/100 = 1% drop

    diff = compare_runs(_run("run_a", baseline_results), _run("run_b", new_results))

    assert diff.severity == "ok"
