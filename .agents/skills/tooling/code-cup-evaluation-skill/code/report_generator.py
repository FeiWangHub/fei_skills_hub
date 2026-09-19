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
table { border-collapse: collapse; width: 100%; font-size: .875rem; }
th, td { text-align: left; padding: .55rem .7rem; border-bottom: 1px solid #262a33; }
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
.bar { height: 6px; background: #262a33; border-radius: 3px; overflow: hidden; min-width: 80px; }
.bar > span { display: block; height: 100%; background: #4c8dff; }
.card { background: #161a21; border: 1px solid #262a33; border-radius: 10px;
        padding: 1.25rem; margin-bottom: 1.5rem; }
.kv { display: grid; grid-template-columns: 180px 1fr; gap: .35rem 1rem; font-size: .85rem; }
.kv dt { color: #8b909a; }
.kv dd { margin: 0; }
code { background: #23262e; padding: .1rem .35rem; border-radius: 4px;
       font-size: .8rem; font-family: ui-monospace, SFMono-Regular, monospace; }
ul.evidence { padding-left: 1.1rem; font-size: .82rem; color: #b8bcc4; }
.review { background: #3a1414; border-color: #5a2020; }
"""


def _escape(value: object) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


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
    total = float(record.get("total", 0) or 0)
    confidence = str(record.get("confidence", "low"))
    gate = record.get("static_gate") or {}
    provenance = record.get("provenance") or {}

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
    <dt>Total score</dt><dd><strong>{_escape(total)} / 100</strong></dd>
    <dt>Rank</dt><dd>{_escape(record.get('rank', '—'))}</dd>
  </dl>
</div>
<h2>Dimension scores</h2>
<table>
  <thead><tr><th>Dimension</th><th class="num">Band</th><th>Scale</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
<h2>Static gate findings</h2>
<table>
  <thead><tr><th>Severity</th><th>Category</th><th>File</th><th class="num">Line</th></tr></thead>
  <tbody>{finding_rows}</tbody>
</table>
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


def render_dashboard(records: list[dict[str, object]], generated_at: str | None = None) -> str:
    """Render the sortable-free summary leaderboard page."""
    stamp = generated_at or datetime.now(timezone.utc).isoformat()

    rows = []
    for record in records:
        gate = record.get("static_gate") or {}
        passed = bool(gate.get("passed")) if isinstance(gate, dict) else False
        confidence = str(record.get("confidence", "low"))
        rows.append(
            "<tr>"
            f'<td class="num">{_escape(record.get("rank", "—"))}</td>'
            f"<td>{_escape(record.get('team_name'))}</td>"
            f"<td>{_escape(record.get('artifact_type'))}</td>"
            f'<td class="num">{_escape(record.get("total", 0))}</td>'
            f'<td><span class="badge {CONFIDENCE_CLASS.get(confidence, "conf-low")}">{_escape(confidence)}</span></td>'
            f'<td class="{"gate-pass" if passed else "gate-fail"}">{"pass" if passed else "blocked"}</td>'
            f"<td>{_escape(record.get('state'))}</td>"
            "</tr>"
        )

    total_count = len(records)
    blocked = sum(
        1
        for r in records
        if isinstance(r.get("static_gate"), dict) and not r["static_gate"].get("passed")  # type: ignore[index]
    )
    review = sum(1 for r in records if r.get("human_review_required"))

    body = f"""
<h1>Code Cup — Evaluation Dashboard</h1>
<div class="sub">
  {total_count} submissions &nbsp;·&nbsp; {blocked} blocked by the static gate
  &nbsp;·&nbsp; {review} flagged for human review &nbsp;·&nbsp; generated {_escape(stamp)}
</div>
<table>
  <thead>
    <tr>
      <th class="num">#</th><th>Team</th><th>Artifact</th>
      <th class="num">Score</th><th>Confidence</th><th>Gate</th><th>State</th>
    </tr>
  </thead>
  <tbody>{''.join(rows)}</tbody>
</table>
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
    written: dict[str, str] = {}

    dashboard_path = out / "index.html"
    dashboard_path.write_text(render_dashboard(results), encoding="utf-8")
    written["dashboard"] = str(dashboard_path)

    for record in results:
        submission_id = str(record.get("submission_id", "unknown"))
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in submission_id)
        page_path = out / f"{safe_name}.html"
        page_path.write_text(render_submission_report(record), encoding="utf-8")
        written[submission_id] = str(page_path)

    return written


def load_bundle(path: str | Path) -> dict[str, object]:
    bundle_path = Path(path)
    if not bundle_path.exists():
        raise FileNotFoundError(f"Result bundle not found: {bundle_path}")
    return json.loads(bundle_path.read_text(encoding="utf-8"))
