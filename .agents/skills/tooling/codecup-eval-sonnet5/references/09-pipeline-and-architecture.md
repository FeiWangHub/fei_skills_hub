# Pipeline & Architecture (No Code — Component Responsibilities & Data Flow)

## 1. High-Level Flow

```
[1] Submission Intake
      -> (manifest file: templates/submission-manifest-template.yaml)
[2] Repo Fetch (read-only, internal Git hosting)
      ->
[3] Artifact Type Classifier
      ->
[4] Layer 0 - Deterministic Gate (schema validator + security scanner)
      |- FAIL -> Remediation Queue (skips 5-7)
      -> PASS
[5] Fact Extraction (contributor stats, test presence, doc structure) - deterministic, no LLM
      ->
[6] Tier 1 Judge LLM Call (internal endpoint only) - per artifact-type prompt template
      ->
[7] Aggregation & Ranking
      -> (only for organizer-selected top slice, if tier2_enabled)
[8] Tier 2 Sandboxed Dynamic Run (network-isolated)
      ->
[9] Report Data Assembly (submission_record + dashboard_aggregate JSON)
      ->
[10] Static HTML Site Generation (per-project pages + dashboard)
      ->
[11] Publish to GitHub Pages (or internal static host)
      ->
[12] Human Review Pass (gate failures + boundary cases + any dimension-3 band <=2)
```

## 2. Component Responsibilities

### 2.1 Submission Intake
- Input: a manifest (see `templates/submission-manifest-template.yaml`) listing repo URL, declared type (self-reported, may be wrong), track, contact.
- Output: a normalized `submission_record` shell (schema §4 in `08-json-output-schema.md`) with all evaluation fields null.

### 2.2 Repo Fetch
- Read-only shallow clone from internal Git hosting only. No submission repo content ever leaves the internal network boundary (hard security requirement — see parent SKILL.md).
- Should timeout/skip cleanly on inaccessible repos, logging to the remediation queue rather than blocking the whole batch.

### 2.3 Artifact Type Classifier
Detection rules (in priority order — first match wins; self-reported type in the manifest is used only as a **tiebreaker hint**, never blindly trusted, since misclassification would apply the wrong standard):
1. `SKILL.md` (or `skill.md`) present at any depth under a `skills/` or similarly-named directory, **and** frontmatter contains `name`+`description` → classify as `skill`. Sub-classify which standard (A/B/C) applies based on directory convention (`.claude/skills/`, `.github/skills/`, `.opencode/skill(s)/`, `.agents/skills/` — all four accept the same SKILL.md shape, so sub-classification mainly matters for locating the *directory-location* conformance check, not the frontmatter check).
2. `.github/agents/*.md` or `.github/agents/*.agent.md` present → classify as `copilot_agent`.
3. `.opencode/agent(s)/*.md` present → classify as `opencode_agent`.
4. None of the above → classify as `source_project`.
5. If multiple match (e.g. a repo ships both a Skill and a Copilot Agent) → treat as **multi-artifact submission**, evaluate each artifact separately, roll up to the submission's `final_score` as the **max** of its artifact scores (a project shouldn't be penalized for also including a skill on top of its main agent) — organizers should confirm this roll-up rule (see `11-...md` open questions).

### 2.4 Layer 0 Gate
- Runs the deterministic rules from `01`/`02`/`03` §"Machine-Checkable Conformance Rules" (schema) and `05` (security).
- Must be **idempotent and side-effect-free** (safe to re-run on the same submission without corrupting state).
- On failure, generates a human-readable remediation note per violation (file:line + rule + suggested fix pointer to the relevant reference doc section).

### 2.5 Fact Extraction (Pre-LLM)
Deterministic, non-LLM computation, to keep the LLM Judge from re-deriving facts it might get wrong or hallucinate:
- Contributor/commit stats: distinct committers, commit count distribution, presence of "single giant dump commit" pattern (one commit >80% of total lines changed).
- Test presence: existence of a test directory/convention for the detected language/framework; rough ratio of test files to source files.
- Doc structure: which of the expected sections (per `01`/`02`/`03`/rubric `04` §Dimension 5) are present in README/SKILL.md/AGENTS.md, via heading-text matching.
- These facts are injected verbatim into the Judge prompt (see `templates/judge-prompt-*.md` "Pre-Computed Facts" block) — the Judge reasons over them, does not recompute them.

### 2.6 Tier 1 Judge LLM Call
- Exactly one call per artifact per submission (not per dimension — the model reasons over all 5 dimensions in one structured response, per `08-json-output-schema.md` schema 2), to keep cost/latency bounded across 150+ submissions.
- Must run against an **internal/private LLM endpoint** — this is a hard security requirement, not a preference.
- On malformed/schema-invalid output: retry up to 2 times; if still invalid, route to human review with a "judge_failed" flag rather than silently dropping the submission.

### 2.7 Aggregation & Ranking
- Computes `final_score`, `rank_overall`, `rank_within_track`.
- Applies the human-review trigger rules from `04-scoring-rubric.md` §5.
- For boundary cases, triggers the second Judge pass per `06-llm-judge-methodology.md` §7.

### 2.8 Tier 2 (Optional)
- Only runs for the organizer-selected top slice.
- Sandboxed, network-isolated, timeout-bounded (see `07-dynamic-eval-metrics.md`).
- Failure to run (e.g. sandbox unavailable) must **not** block Tier 1 results from being published — Tier 2 is additive-only.

### 2.9 Report Data Assembly & Site Generation
- Produces the JSON described in `08-json-output-schema.md` §4-5.
- Site generation is purely a function of this JSON — see `10-html-report-requirements.md` for what the pages must show.

### 2.10 Human Review Pass
- A queue view (could be as simple as a filtered dashboard view, see `10-...md`) listing every submission with `needs_human_review: true`, with the specific `human_review_reasons`.
- Judges resolve by editing `human_review_notes`/`human_review_status`; this is a **manual step outside the AI pipeline's scope**, but the pipeline must expose the data needed for it.

## 3. Batching & Throughput (for 150+ Submissions)

- Process submissions **asynchronously in a queue**, not one synchronous call after another blocking on network/LLM latency.
- Recommended batch size for the Judge LLM stage: process in parallel batches of 5-10 concurrent calls (tune to the internal endpoint's rate limits), not all 150 at once (avoid overwhelming the internal endpoint) and not strictly serial (would be too slow for a hackathon deadline).
- Layer 0 gate (steps 2.2-2.4) has no LLM dependency and can run fully in parallel across all 150+ submissions immediately.
- Idempotency matters: if the pipeline is re-run (e.g. after a bug fix), it should skip re-fetching/re-gating/re-judging submissions whose inputs haven't changed (cache by repo commit SHA), to avoid wasting LLM budget re-scoring unchanged submissions.

## 4. Data Retention & Access Control

- `submission_record` JSON (with all evidence/reasoning) should be considered **judge-facing**, potentially sensitive (contains direct quotes/paths from participants' code) — access should be restricted to organizers/judges, not published in raw form.
- The **published HTML report** is a curated/redacted view derived from this JSON (see `10-...md`) — decide explicitly what evidence detail is safe to show to the submitter/public vs. judges-only (open question, see `11-...md`).
