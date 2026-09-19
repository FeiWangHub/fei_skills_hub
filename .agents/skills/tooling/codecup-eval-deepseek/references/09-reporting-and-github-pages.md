# 09 — Reporting & GitHub Pages

## 1. Outputs

1. **Per-project report** — `reports/<slug>.html` — one page per submission.
2. **Dashboard** — `leaderboard.html` — sortable/filterable summary of all submissions.
3. Optional **per-type sub-dashboards** — skill / copilot_agent / opencode_agent / source_project.

## 2. Generation rule (non-negotiable)

**Reports are rendered from JSON by trusted plain code — never written by an LLM.**

- Input: `project_result.json` / `leaderboard.json`.
- Renderer: a static generator (e.g. a templating step, implemented later).
- Rationale: (a) reproducibility, (b) security — the LLM's blast radius stops at a JSON verdict and it can never inject markup/script into the published site.

## 3. No-CDN / air-gap rule

Generated HTML must reference **zero** external URLs. Concretely:
- No `<script src="https://...">`, no CSS `@import`, no web fonts.
- Use a system font stack; inline or locally vendor all CSS/JS.
- Add a CI gate that fails the build if any generated HTML contains an external URL.
- (Note: the existing `skill-creator` report generator references Google Fonts — strip that pattern when reusing.)

## 4. Per-project report — required content

| Section | Content |
|---|---|
| Header | Project name, team, artifact type, track, repo link, commit SHA |
| Score summary | Final score, static score, rank overall + rank within type |
| Dimension breakdown | Per-dimension bar: score/max, method (deterministic/hybrid/LLM), confidence |
| Hard-fail banner | If gated: reasons + "routed to human review" (visible, not hidden) |
| Evidence | Per dimension, the cited evidence entries (file:line + note) |
| Qualitative notes | Strengths, weaknesses, observations not scored |
| Provenance footer | rubric_version, prompt_version, model, scanned_at |
| Review flag | Whether the submission is in the human-review queue |

## 5. Dashboard — required features

- **Sortable** by final score and any dimension.
- **Filterable** by artifact type, track, security flag, review status.
- **Color thresholds** (e.g. ≥80 green, 50–79 amber, <50 red) — reuse the `skill-creator` viewer's pass-rate coloring approach.
- Columns: rank, project, team, type, each dimension, final score, flags, report link.
- A separate **gate-failure / human-review** list.
- Distribution summary: count, min/max/median/p90.

## 6. Implementation options

- Reuse the `skill-creator/eval-viewer` pattern: a single self-contained HTML template with data embedded via a placeholder (`/*__EMBEDDED_DATA__*/`), so the page is one portable file.
- Vanilla JS sort/filter is sufficient at this scale; no framework (also keeps the no-CDN rule trivial).
- Publish to GitHub Pages (internal GHE) via a static deploy step — note this does not exist yet and must be built.

## 7. Data contract

The report consumes `project_result.json`; the dashboard consumes `leaderboard.json`. Both are defined in `/schemas`. Example payloads: `templates/project-report-data-template.json`, `templates/leaderboard-data-template.json`.
