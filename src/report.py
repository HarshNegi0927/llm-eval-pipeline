"""Generates a self-contained HTML diff report — the guide's "quick
dashboard for diff views." No server, no JS framework: static HTML + CSS
and a hand-computed SVG trend chart, so it opens by double-clicking the
file and is easy to attach to a Slack message or commit as portfolio
evidence.
"""
from __future__ import annotations

import html
from pathlib import Path

from .comparison import ComparisonResult
from .eval_engine import EvalRun

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

_SEVERITY_COLORS = {"ok": "#16a34a", "warning": "#d97706", "critical": "#dc2626"}


def _esc(value) -> str:
    return html.escape(str(value)) if value is not None else ""


def _scorecard_html(run: EvalRun) -> str:
    s = run.summary
    rows = "".join(
        f'<div class="cat-row"><span class="cat-name">{_esc(cat)}</span>'
        f'<div class="bar-track"><div class="bar-fill" style="width:{acc*100:.0f}%"></div></div>'
        f'<span class="cat-pct">{acc*100:.1f}%</span></div>'
        for cat, acc in sorted(s.category_accuracy.items())
    )
    return f"""
    <div class="scorecard">
      <div class="big-stat">
        <div class="big-number">{s.pass_rate*100:.1f}%</div>
        <div class="big-label">{s.passed}/{s.total_cases} passed</div>
      </div>
      <div class="cat-breakdown">{rows}</div>
      <div class="mini-stats">
        <div><span class="mini-label">Avg summary score</span><span class="mini-value">{s.avg_summary_score:.2f}/5</span></div>
        <div><span class="mini-label">Avg latency</span><span class="mini-value">{s.avg_latency_ms:.0f}ms</span></div>
        <div><span class="mini-label">Tokens</span><span class="mini-value">{s.total_input_tokens} in / {s.total_output_tokens} out</span></div>
        <div><span class="mini-label">Errors</span><span class="mini-value">{s.error_count}</span></div>
      </div>
    </div>
    """


def _diff_case_row(case_id: str, run: EvalRun, baseline: EvalRun) -> str:
    old_r = next((r for r in baseline.results if r.test_case_id == case_id), None)
    new_r = next((r for r in run.results if r.test_case_id == case_id), None)
    if old_r is None or new_r is None:
        return ""
    return f"""
    <tr>
      <td><code>{_esc(case_id)}</code></td>
      <td>{_esc(new_r.input)}</td>
      <td>{_esc(old_r.actual_category)} (score {_esc(old_r.summary_score)})</td>
      <td>{_esc(new_r.actual_category)} (score {_esc(new_r.summary_score)})</td>
    </tr>
    """


def _comparison_html(run: EvalRun, baseline: EvalRun, comparison: ComparisonResult) -> str:
    color = _SEVERITY_COLORS[comparison.severity]
    regression_rows = "".join(
        _diff_case_row(d.test_case_id, run, baseline) for d in comparison.regressions
    )
    improvement_rows = "".join(
        _diff_case_row(d.test_case_id, run, baseline) for d in comparison.improvements
    )
    regressions_block = (
        f'<h3>Regressions ({len(comparison.regressions)})</h3>'
        f'<table class="diff-table"><tr><th>Case</th><th>Input</th><th>Was</th><th>Now</th></tr>'
        f'{regression_rows}</table>'
        if comparison.regressions
        else "<p class='muted'>No regressions.</p>"
    )
    improvements_block = (
        f'<h3>Improvements ({len(comparison.improvements)})</h3>'
        f'<table class="diff-table"><tr><th>Case</th><th>Input</th><th>Was</th><th>Now</th></tr>'
        f'{improvement_rows}</table>'
        if comparison.improvements
        else ""
    )
    return f"""
    <div class="severity-badge" style="background:{color}">{comparison.severity.upper()}</div>
    <p>vs run <code>{_esc(baseline.summary.run_id)}</code> ({_esc(baseline.summary.prompt_version)})
       — pass rate {comparison.pass_rate_delta*100:+.1f} pts</p>
    {regressions_block}
    {improvements_block}
    """


def _trend_svg(history: list[EvalRun], width: int = 700, height: int = 130) -> str:
    """Hand-computed SVG line chart of pass rate across saved runs — no
    charting library, just points derived from run_store history."""
    if len(history) < 2:
        return "<p class='muted'>Not enough saved runs yet for a trend chart — need at least 2.</p>"

    pad = 24
    n = len(history)
    xs = [pad + i * (width - 2 * pad) / (n - 1) for i in range(n)]
    ys = [height - pad - r.summary.pass_rate * (height - 2 * pad) for r in history]
    points = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    dots = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#4f46e5" />' for x, y in zip(xs, ys)
    )
    labels = "".join(
        f'<text x="{x:.1f}" y="{height-4}" font-size="10" text-anchor="middle" fill="#6b7280">'
        f'{_esc(r.summary.prompt_version)}</text>'
        for x, r in zip(xs, history)
    )
    return f"""
    <svg viewBox="0 0 {width} {height}" width="100%" height="{height}">
      <polyline points="{points}" fill="none" stroke="#4f46e5" stroke-width="2" />
      {dots}
      {labels}
    </svg>
    """


def generate_html_report(
    run: EvalRun,
    baseline: EvalRun | None,
    comparison: ComparisonResult | None,
    history: list[EvalRun],
    drift_warning: str | None = None,
) -> str:
    s = run.summary
    comparison_html = (
        _comparison_html(run, baseline, comparison) if (baseline and comparison) else ""
    )
    drift_html = (
        f'<div class="card"><div class="severity-badge" style="background:#d97706">DRIFT</div>'
        f'<p>{_esc(drift_warning)}</p></div>'
        if drift_warning
        else ""
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Eval report — {_esc(s.run_id)}</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; background:#f9fafb; color:#111827; margin:0; padding:32px; }}
  .container {{ max-width: 900px; margin: 0 auto; }}
  h1 {{ font-size: 20px; margin-bottom:4px; }}
  .meta {{ color:#6b7280; font-size:13px; margin-bottom:24px; }}
  .card {{ background:#fff; border:1px solid #e5e7eb; border-radius:10px; padding:20px; margin-bottom:20px; }}
  .scorecard {{ display:flex; gap:32px; align-items:center; flex-wrap:wrap; }}
  .big-number {{ font-size:42px; font-weight:700; }}
  .big-label {{ color:#6b7280; font-size:13px; }}
  .cat-breakdown {{ flex:1; min-width:220px; }}
  .cat-row {{ display:flex; align-items:center; gap:8px; margin-bottom:6px; font-size:13px; }}
  .cat-name {{ width:80px; text-transform:capitalize; }}
  .bar-track {{ flex:1; background:#e5e7eb; border-radius:4px; height:8px; overflow:hidden; }}
  .bar-fill {{ background:#4f46e5; height:100%; }}
  .cat-pct {{ width:48px; text-align:right; color:#6b7280; }}
  .mini-stats {{ display:flex; gap:24px; flex-wrap:wrap; }}
  .mini-stats > div {{ display:flex; flex-direction:column; }}
  .mini-label {{ color:#6b7280; font-size:11px; }}
  .mini-value {{ font-size:15px; font-weight:600; }}
  .severity-badge {{ display:inline-block; color:#fff; font-weight:700; font-size:12px; padding:4px 10px; border-radius:6px; margin-bottom:8px; }}
  table.diff-table {{ width:100%; border-collapse:collapse; font-size:13px; margin-bottom:16px; }}
  table.diff-table th, table.diff-table td {{ text-align:left; padding:6px 8px; border-bottom:1px solid #f0f0f0; }}
  table.diff-table th {{ color:#6b7280; font-weight:600; font-size:11px; text-transform:uppercase; }}
  .muted {{ color:#9ca3af; font-size:13px; }}
  code {{ background:#f3f4f6; padding:1px 5px; border-radius:4px; }}
</style>
</head>
<body>
<div class="container">
  <h1>Eval Report — {_esc(s.prompt_version)}</h1>
  <div class="meta">run {_esc(s.run_id)} &middot; {_esc(s.model)} &middot; {_esc(s.timestamp)} &middot; dataset {_esc(s.dataset_version)}</div>

  <div class="card">{_scorecard_html(run)}</div>

  {f'<div class="card">{comparison_html}</div>' if comparison_html else ''}

  {drift_html}

  <div class="card">
    <h3 style="margin-top:0">Pass rate trend</h3>
    {_trend_svg(history)}
  </div>
</div>
</body>
</html>"""


def save_report(html_content: str, run_id: str) -> Path:
    path = REPORTS_DIR / f"{run_id}.html"
    path.write_text(html_content, encoding="utf-8")
    return path
