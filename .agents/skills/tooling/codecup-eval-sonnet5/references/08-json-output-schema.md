# Canonical JSON Output Schemas

All schemas below are **illustrative data-shape specifications** (JSON with inline comments removed for validity), not executable code. An implementer should treat these as the contract between pipeline stages.

---

## 1. `gate_result` — Layer 0 Output (per submission)

```json
{
  "submission_id": "string",
  "artifact_type": "skill | copilot_agent | opencode_agent | source_project",
  "gate_status": "pass | fail",
  "schema_conformance": {
    "checked_against": "standard_a_claude_skill | standard_b_copilot_agent | standard_c_opencode | none",
    "violations": [
      { "rule": "string", "severity": "hard_fail | warn", "detail": "string", "file_path": "string", "line": "number | null" }
    ]
  },
  "security_scan_result": {
    "auto_fail_hits": [
      { "category": "string", "signature_matched": "string", "file_path": "string", "line": "number" }
    ],
    "warn_hits": [
      { "category": "string", "signature_matched": "string", "file_path": "string", "line": "number" }
    ]
  },
  "gate_fail_reasons": ["string"],
  "evaluated_at": "ISO-8601 timestamp"
}
```

---

## 2. `judge_output` — Tier 1 LLM Judge Response (per submission, per dimension)

This is the schema the Judge LLM call must be constrained to produce.

```json
{
  "submission_id": "string",
  "artifact_type": "skill | copilot_agent | opencode_agent | source_project",
  "dimensions": {
    "business_value": {
      "band": "1-5 integer",
      "score": "0-25 number",
      "reasoning": "string, must reference evidence",
      "evidence": [ { "file_path": "string", "line": "string or number range", "note": "string" } ]
    },
    "technical_architecture": {
      "band": "1-5 integer",
      "score": "0-25 number",
      "reasoning": "string",
      "evidence": [ { "file_path": "string", "line": "string", "note": "string" } ]
    },
    "security_compliance": {
      "band": "1-5 integer",
      "score": "0-20 number",
      "reasoning": "string",
      "locked_by_gate_failure": "boolean",
      "evidence": [ { "file_path": "string", "line": "string", "note": "string" } ]
    },
    "engineering_rigor": {
      "band": "1-5 integer",
      "score": "0-15 number (0-20 for source_project track)",
      "reasoning": "string",
      "evidence": [ { "file_path": "string", "line": "string", "note": "string" } ]
    },
    "docs_schema_conformance": {
      "band": "1-5 integer",
      "score": "0-15 number (0-10 for source_project track)",
      "reasoning": "string",
      "evidence": [ { "file_path": "string", "line": "string", "note": "string" } ]
    }
  },
  "tier1_total": "number (0-100)",
  "strengths": ["string"],
  "weaknesses": ["string"],
  "observations_not_scored": ["string"],
  "judge_model": "string, e.g. internal-llm-v1",
  "judge_temperature": "number",
  "judged_at": "ISO-8601 timestamp"
}
```

---

## 3. `tier2_result` — Dynamic Evaluation Output (per submission, optional)

```json
{
  "submission_id": "string",
  "evaluated": "boolean",
  "task_success_rate": { "tcr_percent": "number", "score": "0-15 number" },
  "token_cost_efficiency": {
    "total_tokens_per_run": ["number"],
    "cost_per_resolved_task": "number",
    "step_efficiency": "number",
    "context_expansion_ratio": "number",
    "cohort_percentile": "number 0-100",
    "score": "0-10 number"
  },
  "stability": {
    "pass_at_k": "number 0-1",
    "pass_hat_k": "number 0-1",
    "tool_call_error_rate": "number 0-1",
    "score": "0-5 number"
  },
  "tier2_total": "number (0-30)",
  "sandbox_run_ids": ["string"],
  "evaluated_at": "ISO-8601 timestamp"
}
```

---

## 4. `submission_record` — Final Aggregated Record (feeds report + dashboard)

```json
{
  "submission_id": "string",
  "project_name": "string",
  "repo_url": "string",
  "track": "string",
  "artifact_type": "skill | copilot_agent | opencode_agent | source_project",
  "contact": "string",
  "gate_result": "<see schema 1>",
  "judge_output": "<see schema 2, null if gate failed>",
  "tier2_result": "<see schema 3, null if not evaluated>",
  "final_score": "number (tier1_total [+ tier2_total])",
  "needs_human_review": "boolean",
  "human_review_reasons": ["string"],
  "human_review_status": "not_needed | pending | resolved",
  "human_review_notes": "string | null",
  "rank_overall": "integer | null",
  "rank_within_track": "integer | null"
}
```

---

## 5. `dashboard_aggregate` — Summary Page Data

```json
{
  "generated_at": "ISO-8601 timestamp",
  "total_submissions": "integer",
  "gate_pass_count": "integer",
  "gate_fail_count": "integer",
  "tier2_evaluated_count": "integer",
  "by_artifact_type": {
    "skill": "integer",
    "copilot_agent": "integer",
    "opencode_agent": "integer",
    "source_project": "integer"
  },
  "score_distribution": {
    "min": "number", "max": "number", "median": "number", "p90": "number"
  },
  "submissions": ["<array of submission_record, sorted by final_score desc>"]
}
```

## 6. Field-Level Rules

- `score` fields must always be internally consistent with `band` per the mapping formula in `04-scoring-rubric.md`.
- `evidence` arrays must contain at least 1 entry whenever `score > 0` (see `06-llm-judge-methodology.md` §3).
- `needs_human_review` is computed downstream of `judge_output`, per the rules in `04-scoring-rubric.md` §5 — it is never something the Judge LLM sets itself.
