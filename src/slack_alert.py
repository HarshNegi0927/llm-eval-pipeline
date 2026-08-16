"""Sends a Slack alert via an incoming webhook — status, headline numbers,
and a pointer to the full HTML report. Optional: if SLACK_WEBHOOK_URL isn't
set, this quietly does nothing (not an error) so the pipeline still works
for people who haven't set up Slack.
"""
from __future__ import annotations

import os

import httpx
from dotenv import load_dotenv

from .comparison import ComparisonResult
from .eval_engine import EvalRun

load_dotenv()

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

_SEVERITY_EMOJI = {"ok": "✅", "warning": "⚠️", "critical": "🚨"}


def build_slack_message(
    run: EvalRun, comparison: ComparisonResult | None, report_path, drift_warning: str | None = None
) -> dict:
    s = run.summary

    if comparison is None:
        text = (
            f"📊 *Eval baseline saved* — prompt `{s.prompt_version}`\n"
            f"Pass rate: *{s.passed}/{s.total_cases} ({s.pass_rate*100:.1f}%)*\n"
        )
        if drift_warning:
            text += f"🐌 {drift_warning}\n"
        text += f"Report: `{report_path}`"
        return {"text": text}

    emoji = _SEVERITY_EMOJI[comparison.severity]
    lines = [
        f"{emoji} *Eval run complete* — prompt `{s.prompt_version}` vs `{comparison.baseline_run_id}`",
        f"Pass rate: *{s.passed}/{s.total_cases} ({s.pass_rate*100:.1f}%)* "
        f"({comparison.pass_rate_delta*100:+.1f} pts) — *{comparison.severity.upper()}*",
    ]
    if comparison.regressions:
        case_ids = ", ".join(d.test_case_id for d in comparison.regressions[:10])
        more = (
            f" (+{len(comparison.regressions) - 10} more)"
            if len(comparison.regressions) > 10
            else ""
        )
        lines.append(f"🔻 {len(comparison.regressions)} regression(s): {case_ids}{more}")
    if comparison.improvements:
        lines.append(f"🔺 {len(comparison.improvements)} improvement(s)")
    if drift_warning:
        lines.append(f"🐌 {drift_warning}")
    lines.append(f"Report: `{report_path}`")
    return {"text": "\n".join(lines)}


def send_slack_alert(
    run: EvalRun,
    comparison: ComparisonResult | None,
    report_path,
    drift_warning: str | None = None,
) -> bool:
    """Returns True if a message was sent, False if no webhook is
    configured (this is a valid, non-error state — Slack is optional).
    Raises on an actual HTTP failure so a broken webhook fails loudly
    instead of silently swallowing the alert."""
    if not SLACK_WEBHOOK_URL:
        return False
    payload = build_slack_message(run, comparison, report_path, drift_warning)
    response = httpx.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
    response.raise_for_status()
    return True
