"""Thin wrapper around the Groq API — sync AND async.

Every other module calls call_llm_json() (sync, Phase 1) or
call_llm_json_full_async() (async + metadata, Phase 3 eval engine).
Nobody else imports the Groq SDK directly. If you ever swap providers, this
is the only file that changes.
"""
import json
import os
import time

from dotenv import load_dotenv
from groq import AsyncGroq, Groq
from pydantic import BaseModel

load_dotenv()

# Model names on Groq change as they add/retire models — check
# console.groq.com for what's currently available if this one 404s.
MODEL_NAME = os.environ.get("EVAL_MODEL", "llama-3.1-8b-instant")

_client: Groq | None = None
_async_client: AsyncGroq | None = None


class LLMCallResult(BaseModel):
    """Everything the eval engine needs beyond the parsed content: how long
    it took and how many tokens it burned, per call."""

    content: dict
    latency_ms: float
    input_tokens: int
    output_tokens: int
    model: str


def _get_client() -> Groq:
    """Lazily builds the sync client — see the docstring on the async
    version below for why this matters for tests/CI."""
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    return _client


def _get_async_client() -> AsyncGroq:
    """Lazily builds the async client on first real use.

    Deliberately NOT built at import time: importing this module (or
    anything that imports it, like classifier.py or eval_engine.py) must
    work even with no GROQ_API_KEY set — e.g. in unit tests that mock the
    call functions entirely, or in a CI collection step before secrets are
    injected.
    """
    global _async_client
    if _async_client is None:
        _async_client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))
    return _async_client


def call_llm_json_full(system_prompt: str, user_prompt: str) -> LLMCallResult:
    """Sync call with full metadata (latency, tokens). Used where async isn't needed."""
    start = time.perf_counter()
    response = _get_client().chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    latency_ms = (time.perf_counter() - start) * 1000
    content = json.loads(response.choices[0].message.content)
    usage = response.usage
    return LLMCallResult(
        content=content,
        latency_ms=latency_ms,
        input_tokens=usage.prompt_tokens if usage else 0,
        output_tokens=usage.completion_tokens if usage else 0,
        model=MODEL_NAME,
    )


def call_llm_json(system_prompt: str, user_prompt: str) -> dict:
    """Backward-compatible wrapper used by Phase 1's classify_email() —
    returns just the parsed content dict, discarding timing/token metadata.
    Raises json.JSONDecodeError if the model returns non-JSON; that failure
    is intentionally not swallowed here."""
    return call_llm_json_full(system_prompt, user_prompt).content


async def call_llm_json_full_async(system_prompt: str, user_prompt: str) -> LLMCallResult:
    """Async call with full metadata. This is what the eval engine (Phase 3)
    batches across all golden-dataset cases concurrently, instead of
    awaiting them one at a time — that's the "async batching" the build
    guide calls for, to keep a run of 80+ cases fast and not run up cost
    through idle wall-clock time."""
    start = time.perf_counter()
    response = await _get_async_client().chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    latency_ms = (time.perf_counter() - start) * 1000
    content = json.loads(response.choices[0].message.content)
    usage = response.usage
    return LLMCallResult(
        content=content,
        latency_ms=latency_ms,
        input_tokens=usage.prompt_tokens if usage else 0,
        output_tokens=usage.completion_tokens if usage else 0,
        model=MODEL_NAME,
    )