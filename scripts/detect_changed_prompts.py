"""CLI wrapper — prints space-separated prompt version_ids that changed vs
a base git ref. Used by the GitHub Actions workflow to decide what to eval.

Usage:
    python scripts/detect_changed_prompts.py origin/main
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.git_utils import detect_changed_prompt_versions

if __name__ == "__main__":
    base_ref = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
    versions = detect_changed_prompt_versions(base_ref)
    print(" ".join(versions))
