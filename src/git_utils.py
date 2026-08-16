"""Detects which prompt version files changed between the current branch
and a base ref. This is what tells CI which prompt versions actually need
an eval run — no point re-testing v1 if only v3 changed in this PR.
"""
from __future__ import annotations

import subprocess
from pathlib import Path


def detect_changed_prompt_versions(
    base_ref: str, repo_dir: str | Path | None = None
) -> list[str]:
    """Returns version_ids (filename stems) for every prompts/*.yaml file
    that differs between base_ref and the current HEAD.

    Uses `base...HEAD` (triple-dot) deliberately: this diffs against the
    merge-base, i.e. "what changed on this branch since it forked from
    base" — not "what's different between the two tips right now", which
    would also pick up unrelated commits landed on base afterward.
    """
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD", "--", "prompts/*.yaml"],
        capture_output=True,
        text=True,
        cwd=repo_dir,
        check=True,
    )
    versions = []
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if line:
            versions.append(Path(line).stem)
    return versions
