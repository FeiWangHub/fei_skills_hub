# 07 — Data Model & Schemas

The machine-readable contracts live in `/schemas/*.json`. This file explains them and the field-level rules.

## 1. Objects

| Schema | Produced by | Purpose |
|---|---|---|
| `submission_manifest.schema.json` | organizer (frozen) | The 150+ submission list |
| `hackathon_questionnaire.schema.json` | each team | Structured business-value inputs |
| `gate_result` (inline, layer 0) | deterministic orchestrator | Schema conformance + security scan verdict |
| `judge_output` (inline, layer 1) | sandboxed LLM judge | Per-dimension qualitative scores |
| `project_result.schema.json` | orchestrator | Final aggregated record per submission |
| `leaderboard.schema.json` | orchestrator | Dashboard aggregate |

## 2. `judge_output` (what the LLM call is constrained to return)

```json
{
  "submission_id": "string",
  "artifact_type": "skill | copilot_agent | opencode_agent | source_project",
  "dimensions": {
    "code_content_quality": { "band": 1, "score": 0, "reasoning": "string", "evidence": [] },
    "documentation":       { "band": 1, "score": 0, "reasoning": "string", "evidence": [] },
    "innovation":          { "band": 1, "score": 0, "reasoning": "string", "evidence": [] }
  },
  "strengths": ["string"],
  "weaknesses": ["string"],
  "observations_not_scored": ["string"],
  "judge_model": "string",
  "judge_temperature": 0,
  "judged_at": "ISO-8601"
}
```

> The judge scores **only** the qualitative dimensions. Deterministic dimensions are merged in later by the orchestrator.

## 3. Deterministic-layer output (per dimension)

```json
{
  "dimension": "security_compliance | spec_structural | testing_reliability | business_value",
  "score": "number",
  "max": "number",
  "method": "deterministic",
  "evidence": [ { "rule": "string", "file_path": "string", "line": 0, "detail": "string" } ],
  "confidence": "high"
}
```

## 4. Aggregated `project_result` — key fields

See `schemas/project_result.schema.json` for the full contract. Principal fields:

- `repo`: url, slug, commit_sha (frozen), artifact_type, scanned_at
- `provenance`: orchestrator_version, model_id, model_version, prompt_version, rubric_version, weight_profile
- `gate_result`: status, schema violations, security hits, reasons
- `hard_fail`: triggered, reasons
- `dimensions`: map of dimension → `{score, max, method, evidence[], confidence}`
- `overall_score` (static), `dynamic` (nullable), `final_score`
- `security_flag`, `needs_human_review`, `human_review_reasons[]`
- `rank_overall`, `rank_within_type`
- `artifacts`: transcript_path (audit-only), report_path

## 5. `leaderboard` — key fields

See `schemas/leaderboard.schema.json`. Contains metadata (generated_at, rubric_version, weight_profile_version), counts, score distribution, and an `entries[]` array sorted by `final_score` desc, each with per-dimension scores and a `report_url`.

## 6. Field-level rules

1. `score` must be internally consistent with `band`: `score = max × band / 5`.
2. Any `score > 0` ⇒ `evidence` non-empty.
3. `needs_human_review` is **computed downstream** by the orchestrator (gate failure, low confidence, or top-N boundary) — never set by the judge.
4. `confidence` is `high | medium | low`; deterministic dimensions are always `high`.
5. All numeric scores rounded to 0.5.
6. Every result embeds full `provenance` for audit.
