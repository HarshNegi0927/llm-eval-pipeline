"""Tests for report.py. Builds fake EvalRun/ComparisonResult objects
directly — no LLM calls, no real file I/O beyond what save_report does."""
from src.comparison import CaseDiff, ComparisonResult, compare_runs
from src.eval_engine import EvalCaseResult, EvalRun, EvalRunSummary
from src.report import generate_html_report, save_report


def _case(tc_id, expected_category, actual_category, score=5, input_text="some input"):
    return EvalCaseResult(
        test_case_id=tc_id,
        input=input_text,
        expected_category=expected_category,
        expected_summary="expected",
        difficulty="easy",
        actual_category=actual_category,
        actual_summary="actual",
        category_match=(expected_category == actual_category),
        summary_score=score,
        latency_ms=100.0,
        input_tokens=10,
        output_tokens=5,
    )


def _run(run_id, results, prompt_version="v1", pass_rate_override=None):
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    return EvalRun(
        summary=EvalRunSummary(
            run_id=run_id,
            prompt_version=prompt_version,
            dataset_version="v1",
            model="test-model",
            timestamp="2026-08-15T00:00:00Z",
            total_cases=total,
            passed=passed,
            pass_rate=(pass_rate_override if pass_rate_override is not None else passed / total),
            category_accuracy={"billing": 0.8, "technical": 0.9},
            avg_summary_score=4.2,
            avg_latency_ms=250.0,
            total_input_tokens=1000,
            total_output_tokens=200,
            error_count=0,
        ),
        results=results,
    )


def test_report_renders_baseline_only_run():
    run = _run("run_a", [_case("tc_1", "billing", "billing")])
    html_out = generate_html_report(run, baseline=None, comparison=None, history=[run])

    assert html_out.startswith("<!DOCTYPE html>")
    assert "</html>" in html_out
    assert "run_a" in html_out
    assert "billing" in html_out


def test_report_renders_comparison_with_regressions_and_improvements():
    baseline = _run("run_a", [_case("tc_1", "billing", "technical"), _case("tc_2", "billing", "billing")])
    new = _run("run_b", [_case("tc_1", "billing", "billing"), _case("tc_2", "billing", "technical")])
    comparison = compare_runs(baseline, new)

    html_out = generate_html_report(new, baseline, comparison, history=[baseline, new])

    assert "REGRESSIONS" in html_out.upper() or "Regressions" in html_out
    assert "tc_1" in html_out
    assert "tc_2" in html_out
    assert comparison.severity.upper() in html_out


def test_report_escapes_html_special_characters_in_input():
    malicious_input = "<script>alert('x')</script> & \"quotes\""
    baseline = _run("run_a", [_case("tc_1", "billing", "technical")])
    new = _run("run_b", [_case("tc_1", "billing", "billing", input_text=malicious_input)])
    comparison = compare_runs(baseline, new)

    html_out = generate_html_report(new, baseline, comparison, history=[baseline, new])

    # The raw input appears in the diff table (via _diff_case_row) — it
    # must come out escaped, not as live markup.
    assert "<script>alert" not in html_out
    assert "&lt;script&gt;" in html_out


def test_report_handles_short_history_gracefully():
    run = _run("run_a", [_case("tc_1", "billing", "billing")])
    html_out = generate_html_report(run, baseline=None, comparison=None, history=[run])
    # Only one run in history — trend chart should degrade gracefully, not crash.
    assert "Not enough saved runs" in html_out


def test_save_report_writes_a_file(tmp_path, monkeypatch):
    import src.report as report_module

    monkeypatch.setattr(report_module, "REPORTS_DIR", tmp_path)
    path = save_report("<html>hi</html>", "run_xyz")

    assert path.exists()
    assert path.read_text(encoding="utf-8") == "<html>hi</html>"
