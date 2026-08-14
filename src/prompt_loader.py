"""Loads versioned prompt YAML files from /prompts into a PromptConfig.

Prompts are versioned as files, not as strings buried in code, so that a
prompt change is a diffable, reviewable, git-tracked event — the same way
a code change is. This is what Phase 5's CI/CD trigger watches.
"""
from pathlib import Path
import yaml

from .models import PromptConfig

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def load_prompt_config(version_id: str) -> PromptConfig:
    path = PROMPTS_DIR / f"{version_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"No prompt file found for version '{version_id}' at {path}"
        )
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return PromptConfig(**raw)


def list_prompt_versions() -> list[str]:
    """Returns all available version_ids in /prompts, for the eval runner to iterate over."""
    return sorted(p.stem for p in PROMPTS_DIR.glob("*.yaml"))
