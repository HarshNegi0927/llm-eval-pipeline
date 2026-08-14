"""Thin wrapper around the Groq API.

Every other module calls call_llm_json() — nobody else imports the Groq SDK
directly. If you ever swap providers (OpenAI, Anthropic, local Ollama), this
is the only file that changes.
"""
import json
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Model names on Groq change as they add/retire models — check
# console.groq.com for what's currently available if this one 404s.
MODEL_NAME = os.environ.get("EVAL_MODEL", "llama-3.1-8b-instant")

_client: Groq | None = None


def _get_client() -> Groq:
    """Lazily builds the Groq client on first real use.

    Deliberately NOT built at import time: importing this module (or
    anything that imports it, like classifier.py) must work even with no
    GROQ_API_KEY set — e.g. in unit tests that mock call_llm_json entirely,
    or in a CI collection step before secrets are injected. Building the
    client eagerly at module load turns a missing env var into an import
    crash for code paths that never even call the LLM.
    """
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    return _client


def call_llm_json(system_prompt: str, user_prompt: str) -> dict:
    """Calls the LLM with JSON mode forced and returns a parsed dict.

    Raises json.JSONDecodeError if the model somehow returns non-JSON —
    that failure is intentionally not swallowed here. The eval engine
    (Phase 3) is what decides how to score/log a malformed response.
    """
    response = _get_client().chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    raw = response.choices[0].message.content
    return json.loads(raw)
