"""Schema + loader for the golden dataset.

The golden dataset is the ground truth the eval engine (Phase 3) diffs every
prompt version against. It is NOT generated ground truth — see the notes
field on every case and README.md's review checklist.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

GOLDEN_DATASET_DIR = Path(__file__).resolve().parent.parent / "golden_dataset"

Difficulty = Literal["easy", "medium", "hard", "edge"]
Category = Literal["billing", "technical", "account", "general"]


class GoldenTestCase(BaseModel):
    id: str
    input: str
    expected_category: Category
    expected_summary: str
    difficulty: Difficulty
    notes: str = Field(
        default="", description="Why this case matters / what it's testing for"
    )
    human_verified: bool = Field(
        default=False,
        description="Set True only after a human has read this case and "
        "confirmed expected_category/expected_summary are correct.",
    )


class GoldenDataset(BaseModel):
    dataset_version: str
    created: str
    test_cases: list[GoldenTestCase]


def load_golden_dataset(version: str = "v1") -> GoldenDataset:
    path = GOLDEN_DATASET_DIR / f"{version}.json"
    if not path.exists():
        raise FileNotFoundError(f"No golden dataset found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return GoldenDataset(**raw)
