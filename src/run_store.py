"""Stores eval runs as JSON files under /eval_runs — zero infrastructure,
portable, and diffable in a PR the same way the guide wants. SQLite would
work too, but for a project this size, one-file-per-run is simpler and
just as inspectable.
"""
from pathlib import Path

from .eval_engine import EvalRun

RUNS_DIR = Path(__file__).resolve().parent.parent / "eval_runs"
RUNS_DIR.mkdir(exist_ok=True)


def save_run(run: EvalRun) -> Path:
    path = RUNS_DIR / f"{run.summary.run_id}.json"
    path.write_text(run.model_dump_json(indent=2), encoding="utf-8")
    return path


def load_run(run_id: str) -> EvalRun:
    path = RUNS_DIR / f"{run_id}.json"
    return EvalRun.model_validate_json(path.read_text(encoding="utf-8"))


def list_runs(prompt_version: str | None = None) -> list[EvalRun]:
    """Returns all saved runs, oldest first. Filter to one prompt version
    if you only want that prompt's history."""
    runs = []
    for p in sorted(RUNS_DIR.glob("*.json")):
        run = EvalRun.model_validate_json(p.read_text(encoding="utf-8"))
        if prompt_version is None or run.summary.prompt_version == prompt_version:
            runs.append(run)
    runs.sort(key=lambda r: r.summary.timestamp)
    return runs


def get_latest_run(prompt_version: str | None = None) -> EvalRun | None:
    """The most recent run overall (or for one prompt version) — this is
    what a new run gets diffed against by default."""
    runs = list_runs(prompt_version)
    return runs[-1] if runs else None
