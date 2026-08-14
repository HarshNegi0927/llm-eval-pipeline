"""LLM-as-judge: scores how well a candidate summary matches a reference
summary of the same customer email. This turns "the text is different" into
a number (1-5) the eval engine can threshold against — the guide's
'summary relevance' dimension.
"""
from pydantic import BaseModel, Field

from .llm_client import call_llm_json_full_async

JUDGE_SYSTEM_PROMPT = (
    "You are a strict grader comparing two summaries of the same customer "
    "support email: a REFERENCE summary (assumed correct) and a CANDIDATE "
    "summary (to be graded). Score how well the candidate captures the same "
    "key facts as the reference, on a 1-5 scale: "
    "5 = all key facts present and correct, no contradictions; "
    "4 = all key facts present, only minor wording differences; "
    "3 = most key facts present, one minor detail missing or vague; "
    "2 = misses an important fact or adds one not supported by either summary; "
    "1 = contradicts the reference or is substantively wrong. "
    'Respond ONLY as JSON: {"score": <int 1-5>, "reasoning": "<one short sentence>"}'
)


class JudgeScore(BaseModel):
    score: int = Field(..., ge=1, le=5)
    reasoning: str


async def score_summary_relevance_async(
    reference_summary: str, candidate_summary: str
) -> JudgeScore:
    user_prompt = f"REFERENCE: {reference_summary}\nCANDIDATE: {candidate_summary}"
    call_result = await call_llm_json_full_async(JUDGE_SYSTEM_PROMPT, user_prompt)
    return JudgeScore(**call_result.content)
