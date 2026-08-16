"""Comparison logic: diffs one eval run against a baseline and decides how
worried to be about it. This is the actual "regression detection" — the
eval engine alone just produces scores, this is what turns scores into a
pass/warn/fail call.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from .eval_engine import EvalRun

# Configurable — flag as a warning if pass rate drops 3+ points, critical at
# 8+ points. These are the guide's suggested defaults; tune per how noisy
# your golden dataset's pass/fail boundary actually is.
WARNING_THRESHOLD = 0.03
CRITICAL_THRESHOLD = 0.08

DiffStatus = Literal["regression", "improvement", "unchanged_pass", "unchanged_fail"]
Severity = Literal["ok", "warning", "critical"]


class CaseDiff(BaseModel):
    test_case_id: str
    status: DiffStatus
    old_passed: bool
    new_passed: bool
    old_category: str | None
    new_category: str | None


class ComparisonResult(BaseModel):
    baseline_run_id: str
    new_run_id: str
    pass_rate_delta: float
    category_accuracy_delta: dict[str, float]
    regressions: list[CaseDiff]
    improvements: list[CaseDiff]
    severity: Severity


def compare_runs(baseline: EvalRun, new: EvalRun) -> ComparisonResult:
    baseline_by_id = {r.test_case_id: r for r in baseline.results}

    diffs: list[CaseDiff] = []
    for new_r in new.results:
        old_r = baseline_by_id.get(new_r.test_case_id)
        if old_r is None:
            # A test case that didn't exist in the baseline run (dataset
            # grew since then) — nothing to diff it against, skip it.
            continue

        old_passed, new_passed = old_r.passed, new_r.passed
        if old_passed and not new_passed:
            status: DiffStatus = "regression"
        elif not old_passed and new_passed:
            status = "improvement"
        elif old_passed and new_passed:
            status = "unchanged_pass"
        else:
            status = "unchanged_fail"

        diffs.append(
            CaseDiff(
                test_case_id=new_r.test_case_id,
                status=status,
                old_passed=old_passed,
                new_passed=new_passed,
                old_category=old_r.actual_category,
                new_category=new_r.actual_category,
            )
        )

    pass_rate_delta = new.summary.pass_rate - baseline.summary.pass_rate
    all_categories = set(new.summary.category_accuracy) | set(
        baseline.summary.category_accuracy
    )
    category_accuracy_delta = {
        cat: new.summary.category_accuracy.get(cat, 0.0)
        - baseline.summary.category_accuracy.get(cat, 0.0)
        for cat in all_categories
    }

    regressions = [d for d in diffs if d.status == "regression"]
    improvements = [d for d in diffs if d.status == "improvement"]

    drop = -pass_rate_delta  # positive number when pass rate got worse
    if drop >= CRITICAL_THRESHOLD:
        severity: Severity = "critical"
    elif drop >= WARNING_THRESHOLD:
        severity = "warning"
    else:
        severity = "ok"

    return ComparisonResult(
        baseline_run_id=baseline.summary.run_id,
        new_run_id=new.summary.run_id,
        pass_rate_delta=pass_rate_delta,
        category_accuracy_delta=category_accuracy_delta,
        regressions=regressions,
        improvements=improvements,
        severity=severity,
    )


def check_drift(
    history: list[EvalRun], window: int = 7, drift_threshold: float = 0.05
) -> str | None:
    """Beyond per-run diffs, catches SLOW degradation that no single run's
    comparison would flag: if the trailing `window`-run average pass rate
    has fallen more than `drift_threshold` below the *previous*
    `window`-run average, that's drift — each individual step might be too
    small to trip WARNING_THRESHOLD on its own, but the cumulative slide
    is real. `history` must be ordered oldest-first (as run_store.list_runs
    returns it). Returns a human-readable warning, or None if there isn't
    enough history yet or no drift is detected.
    """
    if len(history) < window * 2:
        return None  # need two full windows to compare

    recent_window = history[-window:]
    prior_window = history[-window * 2 : -window]

    recent_avg = sum(r.summary.pass_rate for r in recent_window) / window
    prior_avg = sum(r.summary.pass_rate for r in prior_window) / window

    drop = prior_avg - recent_avg
    if drop >= drift_threshold:
        return (
            f"Slow drift detected: the last {window}-run average pass rate "
            f"({recent_avg*100:.1f}%) is {drop*100:.1f} points below the "
            f"previous {window}-run average ({prior_avg*100:.1f}%), even "
            f"though no single run triggered a regression alert."
        )
    return None
