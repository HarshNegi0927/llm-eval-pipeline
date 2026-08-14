"""Pydantic schemas for the email classifier feature under test.

This is the interface contract: whatever the prompt/model, input is always
raw email text and output must always match EmailClassificationOutput.
The eval pipeline (Phase 3) is built entirely against this contract.
"""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class EmailClassificationOutput(BaseModel):
    """Structured output contract for the classifier LLM call."""

    category: Literal["billing", "technical", "account", "general"] = Field(
        ..., description="The single best-fit category for the email."
    )
    summary: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="One-sentence summary of the email's content.",
    )


class FewShotExample(BaseModel):
    input: str
    output: EmailClassificationOutput


class PromptConfig(BaseModel):
    """A versioned, loadable prompt configuration.

    This is the "code" the eval pipeline runs CI against in later phases —
    every eval run is scoped to exactly one PromptConfig version.
    """

    version_id: str
    timestamp: str
    system_prompt: str
    few_shot_examples: list[FewShotExample] = Field(default_factory=list)
