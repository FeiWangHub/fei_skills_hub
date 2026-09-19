"""Static report generation for Code Cup evaluation results.

Rules enforced here:
- HTML is rendered deterministically from validated JSON; no LLM writes markup
- all interpolated values are escaped, so a hostile repo name cannot inject HTML
- no external assets are referenced, so reports work on an internal host with no
  outbound network access and no CDN dependency

This module performs no network calls.
"""

from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path

SCORE_LABELS = (
    ("d1_security_and_compliance", "Security and compliance"),
    ("d2_structure_and_conformance", "Structure and conformance"),
    ("d3_code_quality", "Code and content quality"),
    ("d4_documentation", "Documentation"),
    ("d5_testing_and_reliability", "Testing and reliability"),
    ("d6_business_value", "Business value"),
    ("d7_innovation", "Innovation"),
)

CONFIDENCE_CLASS = {
    "high": "conf-high",
    "medium": "conf-medium",
    "low": "conf-low",
}

BASE_STYLE = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body {
  margin: 0; padding: 2rem;
  font-family: ui-sans-serif, -apple-system, "Segoe UI", Roboto, sans-serif;
  background: #0f1115; color: #e8eaed; line-height: 1.5;
}
h1 { font-size: 1.5rem; margin: 0 0 .25rem; }
h2 { font-size: 1.05rem; margin: 2rem 0 .75rem; color: #b8bcc4; font-weight: 600; }
.sub { color: #8b909a; font-size: .85rem; margin-bottom: 2rem; }
/* Wide tables scroll horizontally instead of clipping their last columns. */
.scroll { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: .875rem; }
th, td { text-align: left; padding: .55rem .7rem; border-bottom: 1px solid #262a33;
         white-space: nowrap; }
th { color: #9aa0aa; font-weight: 600; font-size: .78rem;
     text-transform: uppercase; letter-spacing: .04em; }
tr:hover td { background: #161a21; }
.num { text-align: right; font-variant-numeric: tabular-nums; }
.badge { display: inline-block; padding: .1rem .5rem; border-radius: 999px;
         font-size: .72rem; font-weight: 600; }
.conf-high { background: #10331f; color: #57d98a; }
.conf-medium { background: #3a3110; color: #e3c04a; }
.conf-low { background: #3a1414; color: #e8706f; }
.state { font-size: .75rem; padding: .1rem .5rem; border-radius: 4px;
         background: #23262e; color: #c2c6cd; }
.gate-fail { color: #e8706f; font-weight: 600; }
.gate-pass { color: #57d98a; font-weight: 600; }
.pending { color: #e3c04a; font-size: .78rem; }
.bar { height: 6px; background: #262a33; border-radius: 3px; overflow: hidden; min-width: 80px; }
.bar > span { display: block; height: 100%; background: #4c8dff; }
.card { background: #161a21; border: 1px solid #262a33; border-radius: 10px;
        padding: 1.25rem; margin-bottom: 1.5rem; }
.kv { display: grid; grid-template-columns: 180px 1fr; gap: .35rem 1rem; font-size: .85rem; }
.kv dt { color: #8b909a; }
.kv dd { margin: 0; }
code { background: #23262e; padding: .1rem .35rem; border-radius: 4px;
       font-size: .8rem; font-family: ui-monospace, SFMono-Regular, monospace; }
a { color: #4c8dff; text-decoration: none; }
a:hover { text-decoration: underline; }
ul.evidence { padding-left: 1.1rem; font-size: .82rem; color: #b8bcc4; }
.review { background: #3a1414; border-color: #5a2020; }
"""


def _escape(value: object) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def _format_int(value: object) -> str:
    """Group thousands so large token counts stay readable.

    `36866` is hard to parse at a glance; `36,866` is not. Falls back to the
    raw value when the input is not a number.
    """
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return _escape(value)


def _format_seconds(value: object) -> str:
    """Render a duration at a readable precision, grouped where needed."""
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        return _escape(value)

    if seconds >= 60:
        minutes = int(seconds // 60)
        remainder = seconds - minutes * 60
        return f"{minutes}m {remainder:.1f}s"
    if seconds >= 1:
        return f"{seconds:.2f}s"
    if seconds >= 0.001:
        return f"{seconds * 1000:.1f}ms"
    return f"{seconds * 1000:.2f}ms"


def _record_total(record: dict[str, object]) -> float:
    """Read a submission's total, tolerating both storage shapes.

    The pipeline keeps it in `scores["total"]`; older and synthetic records put
    it at the top level. A field-path mismatch here would render a scored
    submission as zero.
    """
    scores = record.get("scores")
    if isinstance(scores, dict):
        try:
            return float(scores.get("total", 0) or 0)
        except (TypeError, ValueError):
            pass
    try:
        return float(record.get("total", 0) or 0)
    except (TypeError, ValueError):
        return 0.0


def _render_page(title: str, body: str) -> str:
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<meta name="referrer" content="no-referrer">\n'
        f"<title>{_escape(title)}</title>\n"
        f"<style>{BASE_STYLE}</style>\n"
        "</head>\n<body>\n"
        f"{body}\n"
        "</body>\n</html>\n"
    )


def render_submission_report(record: dict[str, object]) -> str:
    """Render a single submission report page."""
    scores = record.get("scores") or {}
    total = _record_total(record)
    confidence = str(record.get("confidence", "low"))
    gate = record.get("static_gate") or {}
    provenance = record.get("provenance") or {}
    status = record.get("scoring_status") or {}

    # A total of 0 before the judge runs means "not scored yet", not "scored
    # zero". Showing a bare 0.0 misleads, so say which it is.
    pending = list(status.get("pending_dimensions") or [])
    is_final = bool(status.get("final", not pending))
    if is_final:
        total_display = f"{_escape(total)} / 100"
        total_note = ""
    else:
        partial = status.get("partial_total", 0)
        total_display = "Pending judge"
        total_note = (
            f'<dt>Deterministic subtotal</dt>'
            f"<dd>{_escape(partial)} / 100 from "
            f"{len(pending)} of 7 dimensions not yet judged</dd>"
            f"<dt>Awaiting</dt><dd>{_escape(', '.join(pending))}</dd>"
        )

    rows = []
    for key, label in SCORE_LABELS:
        value = float(scores.get(key, 0) or 0) if isinstance(scores, dict) else 0.0
        pct = (value / 5.0) * 100
        rows.append(
            "<tr>"
            f"<td>{_escape(label)}</td>"
            f'<td class="num">{_escape(value)}</td>'
            f'<td><div class="bar"><span style="width:{pct:.0f}%"></span></div></td>'
            "</tr>"
        )

    findings = gate.get("findings", []) if isinstance(gate, dict) else []
    finding_rows = "".join(
        "<tr>"
        f"<td>{_escape(f.get('severity'))}</td>"
        f"<td>{_escape(f.get('category'))}</td>"
        f"<td><code>{_escape(f.get('file_path'))}</code></td>"
        f'<td class="num">{_escape(f.get("line"))}</td>'
        "</tr>"
        for f in findings
        if isinstance(f, dict)
    ) or '<tr><td colspan="4">No findings.</td></tr>'

    evidence = record.get("evidence") or []
    evidence_items = "".join(
        f"<li><code>{_escape(e.get('file_path'))}</code> "
        f"{_escape(e.get('line_or_range'))} — {_escape(e.get('note'))}</li>"
        for e in evidence
        if isinstance(e, dict)
    ) or "<li>No evidence cited.</li>"

    gate_class = "gate-pass" if gate.get("passed") else "gate-fail"
    gate_text = "passed" if gate.get("passed") else "blocked"

    review_banner = ""
    if record.get("human_review_required"):
        reason = record.get("review_reason") or "low confidence"
        review_banner = (
            f'<div class="card review"><strong>Human review required</strong><br>'
            f"{_escape(reason)}</div>"
        )

    metrics = record.get("metrics") or {}
    stage_rows = "".join(
        "<tr>"
        f"<td>{_escape(stage.get('name'))}</td>"
        f'<td class="num">{_format_seconds(stage.get("elapsed_s"))}</td>'
        f'<td class="num">{_format_int((stage.get("tokens") or {}).get("total_tokens", 0))}</td>'
        f"<td>{_escape((stage.get('tokens') or {}).get('source'))}</td>"
        "</tr>"
        for stage in (metrics.get("stages") or [])
        if isinstance(stage, dict)
    ) or '<tr><td colspan="4">No stages recorded.</td></tr>'

    totals = metrics.get("total_tokens") or {}
    total_tokens = totals.get("total_tokens", 0)
    token_source = totals.get("source", "none")

    body = f"""
<h1>{_escape(record.get('team_name'))}</h1>
<div class="sub">
  <span class="state">{_escape(record.get('state'))}</span>
  &nbsp; <span class="badge {CONFIDENCE_CLASS.get(confidence, 'conf-low')}">{_escape(confidence)} confidence</span>
  &nbsp; submission {_escape(record.get('submission_id'))}
</div>
{review_banner}
<div class="card">
  <dl class="kv">
    <dt>Artifact type</dt><dd>{_escape(record.get('artifact_type'))}</dd>
    <dt>Commit SHA</dt><dd><code>{_escape(record.get('commit_sha'))}</code></dd>
    <dt>Static gate</dt><dd class="{gate_class}">{_escape(gate_text)}</dd>
    <dt>Total score</dt><dd><strong>{total_display}</strong></dd>
    {total_note}
    <dt>Rank</dt><dd>{_escape(record.get('rank', '—'))}</dd>
  </dl>
</div>
<h2>Dimension scores</h2>
<div class="scroll">
<table>
  <thead><tr><th>Dimension</th><th class="num">Band</th><th>Scale</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
</div>
<h2>Cost and timing</h2>
<div class="scroll">
<table>
  <thead><tr><th>Stage</th><th class="num">Elapsed</th><th class="num">Tokens</th><th>Source</th></tr></thead>
  <tbody>{stage_rows}</tbody>
</table>
</div>
<p class="sub">
  Total {_format_seconds(metrics.get('total_elapsed_s', 0))} &nbsp;·&nbsp;
  {_format_int(total_tokens)} tokens (<code>{_escape(token_source)}</code>) &nbsp;·&nbsp;
  <code>measured</code> means the model reported it;
  <code>estimated</code> is a character heuristic for stages that call no model.
</p>
{_agent_phase_note(metrics)}
<h2>Static gate findings</h2>
<div class="scroll">
<table>
  <thead><tr><th>Severity</th><th>Category</th><th>File</th><th class="num">Line</th></tr></thead>
  <tbody>{finding_rows}</tbody>
</table>
</div>
<h2>Cited evidence</h2>
<ul class="evidence">{evidence_items}</ul>
<h2>Provenance</h2>
<div class="card">
  <dl class="kv">
    <dt>Rubric version</dt><dd>{_escape(provenance.get('rubric_version'))}</dd>
    <dt>Prompt version</dt><dd>{_escape(provenance.get('prompt_version'))}</dd>
    <dt>Model version</dt><dd>{_escape(provenance.get('model_version'))}</dd>
    <dt>Scanned at</dt><dd>{_escape(provenance.get('scanned_at'))}</dd>
  </dl>
</div>
"""
    return _render_page(f"{record.get('team_name')} — Code Cup report", body)


def _agent_phase_note(metrics: dict[str, object]) -> str:
    """Explain the agent phase, which cannot be measured the way stages are.

    Showing its wall-clock span as if it were compute time would overstate the
    cost, so it is reported separately and labelled.
    """
    wall = float(metrics.get("agent_wall_clock_s", 0) or 0)
    if wall <= 0:
        return ""

    stages = metrics.get("stages") or []
    agent_stage = next(
        (s for s in stages if isinstance(s, dict) and s.get("name") == "judge_wall_clock"),
        None,
    )
    tokens = (agent_stage or {}).get("tokens") or {}
    token_amount = int(tokens.get("total_tokens", 0) or 0)

    if tokens.get("source") == "measured":
        token_text = f"{_format_int(token_amount)} tokens reported by the host agent"
    elif tokens.get("source") == "estimated":
        token_text = (
            f"about {_format_int(token_amount)} tokens, estimated from the judge "
            "request and response sizes"
        )
    else:
        token_text = "no token figure available for this phase"

    return (
        '<p class="sub">Judging ran inside the host agent and is '
        f"<strong>not</strong> included in the total above. "
        f"Wall-clock from prepare to merge: {_format_seconds(wall)} "
        "(includes idle time, so it is an upper bound rather than compute time) — "
        f"{token_text}.</p>"
    )


def report_filename(submission_id: object) -> str:
    """Map a submission id to its report file name.

    Used by both the per-submission writer and the dashboard links so the two
    can never drift apart.
    """
    raw = str(submission_id if submission_id is not None else "unknown")
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in raw)
    return f"{safe or 'unknown'}.html"


def render_dashboard(
    records: list[dict[str, object]],
    generated_at: str | None = None,
    cost: dict[str, object] | None = None,
) -> str:
    """Render the summary leaderboard, linking each row to its report page.

    When `cost` is supplied (the batch block from `execution-state.json`), the
    aggregate time and token figures are shown in the header.
    """
    stamp = generated_at or datetime.now(timezone.utc).isoformat()

    rows = []
    for record in records:
        gate = record.get("static_gate") or {}
        passed = bool(gate.get("passed")) if isinstance(gate, dict) else False
        confidence = str(record.get("confidence", "low"))
        link = report_filename(record.get("submission_id"))
        team = _escape(record.get("team_name"))
        record_metrics = record.get("metrics") or {}
        elapsed = record_metrics.get("total_elapsed_s", 0) if isinstance(record_metrics, dict) else 0
        tokens = (
            (record_metrics.get("total_tokens") or {}).get("total_tokens", 0)
            if isinstance(record_metrics, dict)
            else 0
        )

        record_status = record.get("scoring_status") or {}
        pending = list(record_status.get("pending_dimensions") or [])
        if pending:
            score_cell = '<span class="pending">pending</span>'
        else:
            score_cell = _escape(_record_total(record))

        rows.append(
            "<tr>"
            f'<td class="num">{_escape(record.get("rank", "—"))}</td>'
            f'<td><a href="{_escape(link)}">{team}</a></td>'
            f"<td>{_escape(record.get('artifact_type'))}</td>"
            f'<td class="num">{score_cell}</td>'
            f'<td><span class="badge {CONFIDENCE_CLASS.get(confidence, "conf-low")}">{_escape(confidence)}</span></td>'
            f'<td class="{"gate-pass" if passed else "gate-fail"}">{"pass" if passed else "blocked"}</td>'
            f'<td>{_escape(record.get("state"))}</td>'
            f'<td class="num">{_format_seconds(elapsed)}</td>'
            f'<td class="num">{_format_int(tokens)}</td>'
            "</tr>"
        )

    total_count = len(records)
    blocked = sum(
        1
        for r in records
        if isinstance(r.get("static_gate"), dict) and not r["static_gate"].get("passed")  # type: ignore[index]
    )
    review = sum(1 for r in records if r.get("human_review_required"))

    cost_line = ""
    if cost:
        cost_line = (
            f'<br>Total {_format_seconds(cost.get("total_elapsed_s", 0))}'
            f' &nbsp;·&nbsp; {_format_int(cost.get("total_tokens", 0))} tokens'
            f' ({_format_int(cost.get("measured_tokens", 0))} measured,'
            f' {_format_int(cost.get("estimated_tokens", 0))} estimated)'
        )

    body = f"""
<h1>Code Cup — Evaluation Dashboard</h1>
<div class="sub">
  {total_count} submissions &nbsp;·&nbsp; {blocked} blocked by the static gate
  &nbsp;·&nbsp; {review} flagged for human review &nbsp;·&nbsp; generated {_escape(stamp)}
  {cost_line}
</div>
<p class="sub">Select a team name to open its full report.</p>
<div class="scroll">
<table>
  <thead>
    <tr>
      <th class="num">#</th><th>Team</th><th>Artifact</th>
      <th class="num">Score</th><th>Confidence</th><th>Gate</th><th>State</th>
      <th class="num">Time</th><th class="num">Tokens</th>
    </tr>
  </thead>
  <tbody>{''.join(rows)}</tbody>
</table>
</div>
"""
    return _render_page("Code Cup — Evaluation Dashboard", body)


def generate_reports(
    bundle: dict[str, object],
    output_dir: str | Path,
) -> dict[str, str]:
    """Write the dashboard plus one page per submission. Returns written paths."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    results = list(bundle.get("results", []) or [])
    cost = bundle.get("cost") if isinstance(bundle.get("cost"), dict) else None
    written: dict[str, str] = {}

    dashboard_path = out / "index.html"
    dashboard_path.write_text(render_dashboard(results, cost=cost), encoding="utf-8")
    written["dashboard"] = str(dashboard_path)

    for record in results:
        submission_id = str(record.get("submission_id", "unknown"))
        page_path = out / report_filename(submission_id)
        page_path.write_text(render_submission_report(record), encoding="utf-8")
        written[submission_id] = str(page_path)

    return written


def load_bundle(path: str | Path) -> dict[str, object]:
    bundle_path = Path(path)
    if not bundle_path.exists():
        raise FileNotFoundError(f"Result bundle not found: {bundle_path}")
    return json.loads(bundle_path.read_text(encoding="utf-8"))
