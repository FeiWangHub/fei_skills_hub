# CodeCup Scoring Rubric — Full Specification

This is the authoritative rubric. All weights, dimensions, and point anchors below are **decisions the hackathon organizers must ratify** before implementation (see `11-product-requirements-and-open-questions.md`). Numbers shown are the recommended defaults from the design consultation.

---

## 0. Two-Layer Model

```
LAYER 0 — HARD GATE (deterministic, no LLM, pass/fail)
   ├─ Schema Conformance Gate  (per artifact type — see references 01/02/03 §"Machine-Checkable Conformance Rules")
   └─ Security Red-Flag Gate  (see 05-security-static-checklist.md — "Auto-Fail" category only)
        ↓ pass
LAYER 1 — TIER 1 STATIC SCORE (LLM Judge + injected static-scan facts) — 100 points, mandatory for all submissions
        ↓ (only for top N% by Tier 1 score, if tier2_enabled)
LAYER 2 — TIER 2 DYNAMIC SCORE (sandboxed execution) — +30 bonus points, optional/stretch
```

A submission that fails Layer 0 does **not** receive a Tier 1 score. It is routed to the human-review / "needs remediation" queue with a machine-generated list of specific failures (see `08-json-output-schema.md`, `gate_fail_reasons`).

---

## 1. Tier 1 Static Score — Dimension Weights

| # | Dimension | Weight (pts) | Primary Evidence Sources |
|---|---|---|---|
| 1 | Business Value & Banking Relevance | 25 | README/description narrative, target users, problem statement |
| 2 | Technical Architecture & Engineering Design | 25 | Code structure, module boundaries, tool/prompt design (for agents/skills), design docs |
| 3 | Security, Compliance & Governance | 20 | Static scan results (injected as facts) + Layer 0 gate outcome + manual pattern review |
| 4 | Engineering Rigor (tests, contributor health, code cleanliness) | 15 | Test directory presence/ratio, git history stats, lint config, type coverage |
| 5 | Documentation & Schema/Standard Conformance | 15 | README completeness, SKILL.md/AGENTS.md quality (beyond the hard gate), example usage |
| | **Total** | **100** | |

### Track-Specific Weight Adjustments (Pre-Approved Alternatives)

For a **plain source-code project** (no SKILL.md / no agent definition file detected):
- Dimension 5 drops to **10 pts**; the freed **5 pts move to Dimension 4** (Engineering Rigor → 20 pts), since there is no schema to conform to.
- All other weights unchanged.

No other re-weighting is permitted without organizer sign-off — this prevents judges/teams from gaming the rubric per-submission.

---

## 2. Scoring Anchors (1 / 3 / 5 point-band descriptions per dimension)

Each dimension is scored on a **0-25 or 0-20 or 0-15 scale**, but the LLM Judge must first reason in a **1-5 qualitative band**, then map to the point scale via `points = round(band / 5 * dimension_max)`. This forces anchored reasoning instead of raw numeric guessing (LLM-as-judge best practice — see `06-llm-judge-methodology.md`).

### Dimension 1 — Business Value & Banking Relevance

| Band | Description |
|---|---|
| 1 | No clear problem statement; appears to be a tech demo with no stated business/user beneficiary. |
| 2 | Problem stated but generic/hypothetical; no evidence of real internal pain point. |
| 3 | Clear, specific problem tied to a real SDLC or business workflow; single-team benefit. |
| 4 | Clear problem + quantified or plausible impact estimate (time saved, risk reduced, cost avoided); reusable by more than one team as-is. |
| 5 | Clear problem + quantified impact + explicit platformization/reuse story (e.g. "any team can install this Skill/Agent and get X without modification"); addresses a compliance/regulatory/risk-reduction angle relevant to a regulated enterprise. |

### Dimension 2 — Technical Architecture & Engineering Design

| Band | Description |
|---|---|
| 1 | Monolithic/ad-hoc script; no separation of concerns; prompt (if any) is unstructured free text with no role/format constraints. |
| 2 | Some structure but tightly coupled; error handling is absent or superficial (empty catch, silent failure). |
| 3 | Reasonable module boundaries; agent/skill has explicit role, scope, and at least basic error handling; tool definitions (if any) are typed/schema'd. |
| 4 | Clear separation of prompt/tool/runner logic (for agents); deterministic output formatting; input validation on tool boundaries; graceful degradation on failure. |
| 5 | All of band 4, plus: explicit state management or retry/recovery logic; tool permissions scoped to least-privilege (relevant for OpenCode `permission` blocks / Copilot `tools` arrays); design rationale documented (why this architecture, not just what). |

### Dimension 3 — Security, Compliance & Governance

> **Note**: if Layer 0 gate already failed on an "Auto-Fail" item, this dimension is locked to 0 and the reasoning field is auto-filled with "Gate failure — see gate_fail_reasons". The bands below apply only to submissions that passed the gate but still have "Warn"-level findings.

| Band | Description |
|---|---|
| 1 | Multiple Warn-level static-scan findings (e.g. broad tool permissions, unvalidated external-looking calls even if not fatal) with no mitigating comments/justification. |
| 2 | One or two Warn-level findings, no justification given. |
| 3 | No Warn-level findings; permissions/tool grants are reasonably scoped; no obvious injection surface. |
| 4 | Band 3 + explicit input/output boundary handling for untrusted content (e.g. tagging external content before feeding to a model) where applicable. |
| 5 | Band 4 + submission explicitly documents its own data-boundary/security posture (mirrors what we require of our own skills in AGENTS.md) — e.g. a "Security Notes" section stating what it does/doesn't send anywhere. |

### Dimension 4 — Engineering Rigor

| Band | Description |
|---|---|
| 1 | No tests, no lint/type config, single giant commit, no meaningful commit history. |
| 2 | Minimal tests (smoke-test only) or tests present but clearly not run (broken imports, stale). |
| 3 | Meaningful test coverage of core logic OR (for skills) an `evals/` directory with realistic test prompts; commit history shows iterative development by at least one identifiable contributor. |
| 4 | Band 3 + CI config present (even if not verifiable as passing) + consistent code style/typing. |
| 5 | Band 4 + evidence of multi-contributor collaboration (>1 committer, or PR-based history) + test coverage spans edge cases, not just the happy path. |

### Dimension 5 — Documentation & Schema/Standard Conformance

| Band | Description |
|---|---|
| 1 | No README or a stub README; if Skill/Agent, frontmatter passes gate but body is near-empty. |
| 2 | README exists but missing setup/usage instructions. |
| 3 | README covers purpose, setup, usage, example; if Skill, body follows template sections reasonably (What It Does / How It Works / Example at minimum). |
| 4 | Band 3 + explicit "when to use / when NOT to use" trigger guidance (Skill) or explicit scope boundaries (Agent) + troubleshooting/gotchas section. |
| 5 | Band 4 + fully matches the applicable official standard's best-practice checklist (see references 01/02/03 §"Official ... Quality & Best-Practice Checklist" / "Official Best Practices") — progressive disclosure, size budget respected, least-privilege tools declared. |

---

## 3. Tier 2 — Dynamic Score (Optional, +30 pts, top-N% only)

See `07-dynamic-eval-metrics.md` for full metric definitions. Point allocation:

| Sub-dimension | Points |
|---|---|
| Task Success Rate (across N predefined test scenarios) | 15 |
| Token/Cost Efficiency | 10 |
| Stability/Resilience (repeat-run consistency, Pass^k) | 5 |

Tier 2 is **never** required to receive an award; it exists to break ties among top contenders and to surface "great on paper, unstable in practice" cases to judges.

---

## 4. Final Score Composition

```
final_score = tier1_total (0-100)  [+ tier2_total (0-30) if evaluated]
```

Dashboard must display both `tier1_total` and `final_score` separately (never hide the static-only score), so judges can distinguish "well-documented/secure" from "actually runs well" — these are different signals and both matter.

## 5. Human-Review Trigger Rules

Route to human review queue when ANY of:
- Layer 0 gate fails (schema or security)
- Dimension 3 (Security) band ≤ 2
- `final_score` is within **±5 points** of any award-cutoff threshold (e.g. top-10, top-20 boundary)
- Two independent Judge LLM runs (see `06-llm-judge-methodology.md` §"Multi-Judge Ensembling") disagree on `tier1_total` by more than 8 points
