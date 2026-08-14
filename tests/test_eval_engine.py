"""Tests for the eval engine.

Both LLM calls (classify + judge) are mocked with AsyncMock — these tests
verify the orchestration logic (pass/fail rules, error isolation, scoring
aggregation), not model quality. Run scripts/run_eval.py locally with a
real key to see actual model behavior.
"""
import asyncio
from unittest.mock import AsyncMock, patch

from src.eval_engine import run_eval_async
from src.judge import JudgeScore
from src.llm_client import LLMCallResult
from src.models import EmailClassificationOutput


def _fake_classify_result(category="billing", summary="a summary"):
    output = EmailClassificationOutput(category=category, summary=summary)
    meta = LLMCallResult(
        content={"category": category, "summary": summary},
        latency_ms=120.0,
        input_tokens=50,
        output_tokens=20,
        model="test-model",
    )
    return output, meta


@patch("src.eval_engine.score_summary_relevance_async", new_callable=AsyncMock)
@patch("src.eval_engine.classify_email_with_metadata_async", new_callable=AsyncMock)
def test_all_correct_and_high_score_gives_full_pass_rate(mock_classify, mock_judge):
    async def _run():
        mock_classify.side_effect = lambda email, cfg: _fake_classify_result(
            category="billing", summary="x"
        )
        mock_judge.return_value = JudgeScore(score=5, reasoning="perfect match")
        return await run_eval_async("v1", "v1")

    run = asyncio.run(_run())
    billing_cases = sum(1 for r in run.results if r.expected_category == "billing")

    assert run.summary.total_cases == 85
    assert run.summary.passed == billing_cases
    assert run.summary.category_accuracy["billing"] == 1.0
    assert run.summary.error_count == 0


@patch("src.eval_engine.score_summary_relevance_async", new_callable=AsyncMock)
@patch("src.eval_engine.classify_email_with_metadata_async", new_callable=AsyncMock)
def test_low_judge_score_fails_the_case_even_with_correct_category(mock_classify, mock_judge):
    async def _run():
        mock_classify.side_effect = lambda email, cfg: _fake_classify_result(
            category="billing", summary="vague summary"
        )
        mock_judge.return_value = JudgeScore(score=2, reasoning="misses key facts")
        return await run_eval_async("v1", "v1")

    run = asyncio.run(_run())
    # Category matches for billing cases, but score=2 < 4 → none should pass.
    assert run.summary.passed == 0


@patch("src.eval_engine.score_summary_relevance_async", new_callable=AsyncMock)
@patch("src.eval_engine.classify_email_with_metadata_async", new_callable=AsyncMock)
def test_classifier_failure_is_isolated_per_case(mock_classify, mock_judge):
    async def _run():
        mock_classify.side_effect = Exception("simulated API failure")
        return await run_eval_async("v1", "v1")

    run = asyncio.run(_run())

    assert run.summary.error_count == run.summary.total_cases
    assert run.summary.passed == 0
    assert all(r.error is not None for r in run.results)
    mock_judge.assert_not_called()


@patch("src.eval_engine.score_summary_relevance_async", new_callable=AsyncMock)
@patch("src.eval_engine.classify_email_with_metadata_async", new_callable=AsyncMock)
def test_judge_failure_does_not_crash_the_run(mock_classify, mock_judge):
    async def _run():
        mock_classify.side_effect = lambda email, cfg: _fake_classify_result(
            category="billing", summary="x"
        )
        mock_judge.side_effect = Exception("judge API failure")
        return await run_eval_async("v1", "v1")

    run = asyncio.run(_run())

    assert run.summary.error_count == 0  # classification itself succeeded
    assert all(r.summary_score is None for r in run.results)
    assert all(r.passed is False for r in run.results)  # no score => conservative fail
