"""Tests for slack_alert.py. build_slack_message is pure logic (no
network); send_slack_alert's network call is mocked."""
from unittest.mock import MagicMock, patch

from src.comparison import compare_runs
from src.eval_engine import EvalCaseResult, EvalRun, EvalRunSummary
from src.slack_alert import build_slack_message, send_slack_alert


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
            timestamp="2026-08-15T00:00:00Z",
            total_cases=total,
            passed=passed,
            pass_rate=(passed / total if total else 0.0),
            category_accuracy={},
            avg_summary_score=4.0,
            avg_latency_ms=100.0,
            total_input_tokens=0,
            total_output_tokens=0,
            error_count=0,
        ),
        results=results,
    )


def test_build_message_for_baseline_run_has_no_comparison_language():
    run = _run("run_a", [_case("tc_1", "billing", "billing")])
    msg = build_slack_message(run, comparison=None, report_path="reports/run_a.html")

    assert "baseline" in msg["text"].lower()
    assert "run_a" not in msg["text"] or "reports/run_a.html" in msg["text"]


def test_build_message_includes_regression_case_ids():
    baseline = _run("run_a", [_case("tc_1", "billing", "billing")])
    new = _run("run_b", [_case("tc_1", "billing", "technical")])
    comparison = compare_runs(baseline, new)

    msg = build_slack_message(new, comparison, report_path="reports/run_b.html")

    assert "tc_1" in msg["text"]
    assert "CRITICAL" in msg["text"] or "regression" in msg["text"].lower()


def test_build_message_includes_drift_warning_when_present():
    run = _run("run_a", [_case("tc_1", "billing", "billing")])
    msg = build_slack_message(
        run, comparison=None, report_path="reports/run_a.html", drift_warning="slow drift text here"
    )
    assert "slow drift text here" in msg["text"]


def test_send_alert_returns_false_when_no_webhook_configured(monkeypatch):
    import src.slack_alert as slack_module

    monkeypatch.setattr(slack_module, "SLACK_WEBHOOK_URL", None)
    run = _run("run_a", [_case("tc_1", "billing", "billing")])

    sent = send_slack_alert(run, comparison=None, report_path="reports/run_a.html")
    assert sent is False


@patch("src.slack_alert.httpx.post")
def test_send_alert_posts_to_webhook_when_configured(mock_post, monkeypatch):
    import src.slack_alert as slack_module

    monkeypatch.setattr(slack_module, "SLACK_WEBHOOK_URL", "https://hooks.slack.test/fake")
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    run = _run("run_a", [_case("tc_1", "billing", "billing")])
    sent = send_slack_alert(run, comparison=None, report_path="reports/run_a.html")

    assert sent is True
    mock_post.assert_called_once()
    assert mock_post.call_args.kwargs["json"]["text"]
