# Product Requirements Summary & Open Decisions

## 1. Problem Statement

A large enterprise's internal IT department is running an internal AI hackathon ("CodeCup") with 150+ submissions across three artifact types: AI Agents (GitHub Copilot / OpenCode), Agent Skills, and plain source-code projects. Judges need an AI-assisted way to produce consistent, defensible, evidence-backed scores across all submissions, published as a static HTML site, without any submission code ever leaving the internal network.

## 2. Goals

- **G1**: Every submission receives a deterministic, code-execution-free Tier 1 static score (0-100) across 5 weighted dimensions, with cited evidence.
- **G2**: Security/compliance issues are caught by deterministic pattern scanning first, with the LLM only interpreting — not discovering — findings, and confirmed real secrets/exfiltration hard-fail the submission before it's scored.
- **G3**: Optionally, top-scoring submissions get a Tier 2 dynamic score (sandboxed execution) measuring success rate, token/cost efficiency, and stability.
- **G4**: Results publish as a static HTML site (GitHub Pages-compatible): one page per project + one summary dashboard sortable/filterable by any dimension.
- **G5**: The whole system respects the same security posture it's judging by — no external LLM API calls, no data leaving the internal network, no credential handling.

## 3. Non-Goals

- Not building a submission portal / intake form (assume a manifest file is sufficient for v1).
- Not replacing human judges — this augments/accelerates them with a defensible first-pass score plus a mandatory human-review queue for edge cases.
- Not evaluating live/production integration — Tier 2 execution uses synthetic test scenarios only, never real internal systems or data.
- Not building real-time/streaming scoring — batch processing of ~150 submissions is acceptable to run over hours, not required to be instant.

## 4. Success Criteria (Acceptance Criteria)

- [ ] Layer 0 gate correctly classifies artifact type for a representative sample set (organizer-curated test set of ~10-15 known-good/known-bad example repos) with zero misclassifications.
- [ ] Layer 0 gate correctly hard-fails 100% of a curated set of "planted" security violations (organizer creates deliberately-bad test fixtures covering each Category 1-4 signature in `05-security-static-checklist.md`) — this is the security correctness bar, non-negotiable.
- [ ] Tier 1 Judge produces schema-valid structured output (per `08-json-output-schema.md` schema 2) on ≥98% of calls without requiring the retry path.
- [ ] Re-running the same submission's Judge call twice at temperature 0 produces `tier1_total` scores within ±3 points (determinism spot-check on ≥10 submissions).
- [ ] Every non-zero dimension score has ≥1 evidence citation (automatically checkable — reject/retry output that violates this).
- [ ] Dashboard renders and is sortable/filterable for all 150+ submissions without requiring JavaScript for basic readability (§3 in `10-html-report-requirements.md`).
- [ ] No outbound call to any public-internet AI API occurs anywhere in the pipeline (verifiable via network-egress audit of the implementation before go-live).

## 5. Rollout Plan (Suggested)

1. **Pilot** (5-10 known submissions, mix of all artifact types) — validate gate accuracy and Judge output quality manually against organizer expectations.
2. **Calibration pass** — organizers review pilot Judge outputs, adjust rubric band wording in `04-scoring-rubric.md` if reasoning consistently misapplies a band (this is expected and normal — treat v1 rubric wording as a draft to be tuned against real outputs).
3. **Full batch run** (all 150+) — Layer 0 gate first (fast, parallel, no LLM), then Tier 1 Judge in throttled batches (`09-pipeline-and-architecture.md` §3).
4. **Human review pass** — judges work through the `needs_human_review` queue.
5. **Tier 2 (optional)** — run only if time/infra permits, on the organizer-selected top slice.
6. **Publish** — generate and deploy the static site.
7. **Retrospective** — compare AI-assisted rankings against final judge decisions; log disagreements as future rubric-calibration input.

## 6. Open Decisions Requiring Organizer Sign-Off Before Implementation

| # | Decision | Options | Recommendation |
|---|---|---|---|
| 1 | Internal LLM endpoint to use for Judge calls | Specify which internal/private endpoint is approved | Must be confirmed with internal security/infra team before any implementation starts — this is the single hardest blocker. |
| 2 | Judges-only vs. also-participant-facing report site | Option A (single site) vs Option B (two-tier) — see `10-html-report-requirements.md` §5 | Recommend Option B (judges-only full detail; participants see redacted scores) to avoid disputes over exact evidence wording being publicly visible. |
| 3 | Tier 2 scope | Skip entirely / run on top 20% / run on top-N fixed count | Recommend: run on top 20% or top 30 (whichever smaller), only if sandbox infra is ready in time. |
| 4 | Multi-artifact submissions roll-up rule | Max of artifact scores / average / evaluate separately with no roll-up | See `09-pipeline-and-architecture.md` §2.3 point 5 — recommend "max", pending organizer confirmation. |
| 5 | Approved external-endpoint allow-list (for Category 2 security scan false-positive avoidance) | e.g., internal package mirrors that look like "external" URLs but are actually internal-proxied | Organizers/security team must supply this allow-list before the scanner can distinguish real violations from internal-proxy false positives. |
| 6 | Award-cutoff thresholds (which score boundaries trigger the ±5-point human-review rule) | e.g., top-10, top-20, per-track top-3 | Needs the actual prize structure to be finalized first. |
| 7 | Remediation flow for gate failures | One-shot final score / allow one resubmission window before final judging | Recommend allowing exactly one resubmission window, clearly time-boxed, to be fair to teams who fail on a fixable technicality (e.g., wrong filename). |

## 7. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| LLM Judge hallucinates a security pass despite a real issue | Security dimension is gated by the deterministic scanner first; LLM never originates a security pass/fail on its own for Auto-Fail-tier issues. |
| 150+ submissions overwhelm internal LLM endpoint capacity/cost | Throttled batching (§3 in `09-...md`); Layer 0 gate filters out failures before any LLM call is spent on them. |
| Rubric wording is ambiguous, causing inconsistent Judge outputs | Calibration pass (Rollout §2) before the full batch run; determinism spot-check is part of acceptance criteria. |
| Participants dispute their score | Evidence-citation requirement (every score traceable to file:line) makes disputes resolvable by inspection rather than argument; human-review queue exists precisely for this. |
| Static scanner false-positives on legitimate internal-proxy URLs | Organizer-maintained allow-list (Open Decision #5) reviewed before go-live. |
| Tier 2 sandbox itself becomes a security exposure (running unknown code) | Network-isolated sandbox is a hard requirement (`07-dynamic-eval-metrics.md` §1); Tier 2 only runs on submissions that already passed the security gate. |

## 8. Glossary

- **Gate / Layer 0**: deterministic, non-LLM pass/fail check (schema conformance + security pattern scan).
- **Tier 1**: mandatory static LLM-judged score (0-100), no code execution.
- **Tier 2**: optional dynamic sandboxed-execution score (+30), for top-scoring submissions only.
- **Band**: the 1-5 qualitative rubric level a dimension is reasoned into before being mapped to a point score.
- **Auto-Fail vs Warn**: security finding severity tiers — Auto-Fail hard-fails the gate; Warn is informational input to the Security dimension score.
- **regulated enterprise**: Global Systemically Important Bank — the regulatory category driving this project's strict air-gap/security requirements.
