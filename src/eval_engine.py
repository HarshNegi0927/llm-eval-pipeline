"""The evaluation engine: runs an entire golden dataset through a prompt
version, concurrently (async batching), and scores every case on multiple
dimensions — not just "did the category match."

This is the core of the whole project. Everything else (comparison,
alerting, CI) consumes an EvalRun produced here.
"""
from __future__ import annotations

import asyncio
import uuid
from collections import defaultdict
from datetime import datetime, timezone

from pydantic import BaseModel, computed_field

from .classifier import classify_email_with_metadata_async
from .golden_dataset import GoldenTestCase, load_golden_dataset
from .judge import score_summary_relevance_async
from .llm_client import MODEL_NAME
from .prompt_loader import load_prompt_config

# Concurrency cap so an 80+ case run doesn't slam the API and trip rate
# limits — tune down if you're on a very restrictive free tier.
MAX_CONCURRENT_REQUESTS = 5


class EvalCaseResult(BaseModel):
    test_case_id: str
    input: str
    expected_category: str
    expected_summary: str
    difficulty: str
    actual_category: str | None = None
    actual_summary: str | None = None
    category_match: bool = False
    summary_score: int | None = None  # 1-5, from the LLM-as-judge
    latency_ms: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    error: str | None = None

    @computed_field
    @property
    def passed(self) -> bool:
        """A case passes only if the category matched AND the judge scored
        the summary at least 4/5. Category-only matching would let a
        technically-right-category-but-garbage-summary slip through."""
        if self.error:
            return False
        return self.category_match and (self.summary_score or 0) >= 4


class EvalRunSummary(BaseModel):
    run_id: str
    prompt_version: str
    dataset_version: str
    model: str
    timestamp: str
    total_cases: int
    passed: int
    pass_rate: float
    category_accuracy: dict[str, float]
    avg_summary_score: float
    avg_latency_ms: float
    total_input_tokens: int
    total_output_tokens: int
    error_count: int


class EvalRun(BaseModel):
    summary: EvalRunSummary
    results: list[EvalCaseResult]


async def _evaluate_one(
    tc: GoldenTestCase,
    prompt_config,
    semaphore: asyncio.Semaphore,
    progress: dict,
    total: int,
) -> EvalCaseResult:
    async with semaphore:
        try:
            output, call_meta = await classify_email_with_metadata_async(
                tc.input, prompt_config
            )
        except Exception as e:
            # A single bad case (malformed JSON, validation failure, API
            # error) must not take down the whole 85-case run. Record it
            # as a failed case and move on — this is what "graceful
            # degradation" means in an eval pipeline.
            result = EvalCaseResult(
                test_case_id=tc.id,
                input=tc.input,
                expected_category=tc.expected_category,
                expected_summary=tc.expected_summary,
                difficulty=tc.difficulty,
                error=str(e),
            )
            progress["done"] += 1
            print(f"  [{progress['done']}/{total}] {tc.id} -> ERROR ({e})", flush=True)
            return result

        summary_score: int | None = None
        try:
            judge_result = await score_summary_relevance_async(
                tc.expected_summary, output.summary
            )
            summary_score = judge_result.score
        except Exception:
            # Judge failure shouldn't nuke the classification result we
            # already have — the case just ends up with no summary_score,
            # which the `passed` property treats as a fail (conservative).
            summary_score = None

        result = EvalCaseResult(
            test_case_id=tc.id,
            input=tc.input,
            expected_category=tc.expected_category,
            expected_summary=tc.expected_summary,
            difficulty=tc.difficulty,
            actual_category=output.category,
            actual_summary=output.summary,
            category_match=(output.category == tc.expected_category),
            summary_score=summary_score,
            latency_ms=call_meta.latency_ms,
            input_tokens=call_meta.input_tokens,
            output_tokens=call_meta.output_tokens,
        )
        progress["done"] += 1
        status = "PASS" if result.passed else "FAIL"
        print(f"  [{progress['done']}/{total}] {tc.id} -> {status}", flush=True)
        return result


def _build_summary(
    results: list[EvalCaseResult], prompt_version: str, dataset_version: str
) -> EvalRunSummary:
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    errors = sum(1 for r in results if r.error)

    cat_totals: dict[str, int] = defaultdict(int)
    cat_matches: dict[str, int] = defaultdict(int)
    for r in results:
        cat_totals[r.expected_category] += 1
        if r.category_match:
            cat_matches[r.expected_category] += 1
    category_accuracy = {
        cat: (cat_matches[cat] / cat_totals[cat] if cat_totals[cat] else 0.0)
        for cat in cat_totals
    }

    scored = [r.summary_score for r in results if r.summary_score is not None]
    avg_summary_score = sum(scored) / len(scored) if scored else 0.0

    latencies = [r.latency_ms for r in results if r.latency_ms is not None]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

    return EvalRunSummary(
        run_id=str(uuid.uuid4())[:8],
        prompt_version=prompt_version,
        dataset_version=dataset_version,
        model=MODEL_NAME,
        timestamp=datetime.now(timezone.utc).isoformat(),
        total_cases=total,
        passed=passed,
        pass_rate=(passed / total if total else 0.0),
        category_accuracy=category_accuracy,
        avg_summary_score=avg_summary_score,
        avg_latency_ms=avg_latency,
        total_input_tokens=sum(r.input_tokens or 0 for r in results),
        total_output_tokens=sum(r.output_tokens or 0 for r in results),
        error_count=errors,
    )


async def run_eval_async(prompt_version: str, dataset_version: str = "v1") -> EvalRun:
    """Runs the full golden dataset against one prompt version, with up to
    MAX_CONCURRENT_REQUESTS cases in flight at once. Actual pace is set by
    the rate limiter in llm_client.py, not this concurrency cap — on Groq's
    free tier (30 RPM / 6,000 TPM) an 85-case run legitimately takes several
    minutes. Progress prints as each case finishes so it never looks stuck."""
    prompt_config = load_prompt_config(prompt_version)
    dataset = load_golden_dataset(dataset_version)
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    total = len(dataset.test_cases)
    progress = {"done": 0}

    tasks = [
        _evaluate_one(tc, prompt_config, semaphore, progress, total)
        for tc in dataset.test_cases
    ]
    results = await asyncio.gather(*tasks)

    summary = _build_summary(list(results), prompt_version, dataset_version)
    return EvalRun(summary=summary, results=list(results))
