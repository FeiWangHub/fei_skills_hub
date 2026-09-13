# HTML Report & Dashboard — Content/Functional Requirements (No Code)

These are **requirements**, not markup — the internal implementer chooses the actual HTML/CSS/JS stack. The only hard constraint: **fully static output**, deployable as-is to GitHub Pages (or an internal static file host), with no backend server required at view-time.

---

## 1. Per-Project Report Page (`/reports/<submission_id>/index.html`)

### Must Show
1. **Header**: project name, artifact type badge (Skill / Copilot Agent / OpenCode Agent / Source Project), track, `final_score`, `rank_overall`, `rank_within_track`.
2. **Gate Status Banner**: prominent pass/fail indicator. If failed, list every `gate_fail_reasons` entry with file:line and a plain-language fix hint.
3. **Dimension Breakdown** (5 dimensions): for each — the band (1-5), the point score, the reasoning text, and the evidence list rendered as `file_path:line` references (as plain text is sufficient if the internal Git host doesn't support deep-linking; as clickable links if it does).
4. **Visual score summary**: a radar/spider chart or equivalent showing the 5 dimension scores normalized to a common scale (e.g., percentage of that dimension's max) — makes it visually obvious at a glance where a project is strong/weak.
5. **Strengths / Weaknesses lists** (from `judge_output.strengths` / `.weaknesses`).
6. **Tier 2 section** (only rendered if `tier2_result.evaluated == true`): task success rate, token/cost efficiency, stability score, with the same reasoning-first presentation style.
7. **Security Findings** (from `gate_result.security_scan_result`): list Warn-level hits even if the gate passed — transparency for judges, doesn't have to be alarming, just visible.
8. **Human Review Flag** (if `needs_human_review == true`): a visible note (not necessarily shown to the submitter-facing version — see redaction question below) so judges immediately know to double check.

### Must NOT Show (Redaction Rule)
- Raw full-file dumps of submitted source code (avoid turning the report site into an unintentional code-hosting mirror — evidence snippets should be short, targeted excerpts, not entire files).
- Any evidence/reasoning text that itself echoes back a real secret detected by the security scanner (the report must reference *that* a secret was found at file:line, never reprint the secret value itself).

## 2. Summary Dashboard Page (`/index.html`)

### Must Show
1. **Sortable/filterable table**: columns = project name, artifact type, track, `final_score`, per-dimension mini scores, gate status, `needs_human_review` flag.
2. **Filters**: by track, by artifact type, by score range, by "has security warn/fail", by "needs human review".
3. **Default sort**: `final_score` descending; user can re-sort by any single dimension column (this is explicitly requested — "方便评委筛选" / lets judges see who scored highest on any specific criterion, not just overall).
4. **Aggregate stats header**: total submissions, gate pass/fail counts, score distribution (min/median/p90/max), breakdown by artifact type and by track.
5. **Link from every row** to that project's full report page.

### Should Show (Nice-to-Have, Not Blocking)
- A simple bar chart of score distribution across all submissions.
- A toggle to show/hide Tier 2-evaluated-only submissions.

## 3. Accessibility & Practical Constraints

- Must render correctly without JavaScript for the core table/content (progressive enhancement for charts/sorting is fine, but a judge with JS disabled or a slow intranet connection should still be able to read every score and every reasoning string).
- Must work fully offline/intranet — no CDN dependencies on public internet resources for fonts/charting libraries (self-host any JS/CSS assets, consistent with the org's air-gap requirements — see parent SKILL.md Security Requirements).
- Page weight should stay reasonable for 150+ project pages — avoid embedding full submission source code inline (ties back to the redaction rule above).

## 4. Data Source Contract

Every page is a pure rendering of the JSON schemas defined in `08-json-output-schema.md` (`submission_record` for per-project pages, `dashboard_aggregate` for the summary page). The site generator must not need to re-derive or recompute any score — it only formats what the pipeline already produced. This separation (data pipeline vs. presentation) lets the report site be regenerated cheaply if only styling changes, without re-running any LLM Judge calls.

## 5. Judge-Facing vs Public-Facing Variant (Open Decision)

Two options — organizers must pick one before implementation (see `11-...md`):
- **Option A (single audience)**: one report site, visible to all participants and judges, with the redaction rules in §1 applied uniformly.
- **Option B (two audiences)**: a judges-only internal view (full evidence detail, human-review flags visible) + a separate, more redacted participant-facing view (scores + high-level strengths/weaknesses only, no evidence file:line detail, no visible human-review flag). Requires two site-generation passes from the same underlying JSON.
