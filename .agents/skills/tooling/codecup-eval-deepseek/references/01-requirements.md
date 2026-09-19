# 01 — Requirements

## 1. Background

A large enterprise's internal IT department runs an AI hackathon ("CodeCup"). ~150+ teams submit internally open-sourced projects. Judges must score every submission and publish results.

**Submission types (all four must be supported):**

| Type | What it is | Canonical form |
|---|---|---|
| `skill` | Agent Skill | `<name>/SKILL.md` (Claude/Agent Skills spec) |
| `copilot_agent` | GitHub Copilot custom agent | `.github/agents/<name>.agent.md` |
| `opencode_agent` | OpenCode agent | `.opencode/agent(s)/<name>.md` or `opencode.json` |
| `source_project` | Plain source-code project | any repo with a build/manifest file |

Each submission lives in its own internal Git repo. Scoring targets a **frozen commit SHA** (the submission snapshot), never the live branch.

## 2. Goal

Use AI to score 150+ submissions and produce:
1. **One HTML scoring report per project**, and
2. **One summary dashboard** (per-dimension scores, sortable/filterable for judges),

both statically generated and published on GitHub Pages (internal GHE).

## 3. Design stance (what makes this variant different)

Three principles drive every decision in this pack:

1. **Deterministic-first.** ≈70% of the score is computed by code with **no LLM** and **no execution** of submission code — spec conformance, security scan, license, trigger-collision, test presence, business-value checklist. The LLM judge only touches the qualitative remainder. Rationale: reproducibility and auditability are non-negotiable for a regulated enterprise.
2. **Judge isolation.** Scoring untrusted submissions with an LLM is itself an attack surface (ToxicSkills: 36.8% of public skills vulnerable, 13.4% critical). The judge is sandboxed, has **zero tools**, and **cannot write its own score file**. See `04-security-design.md`.
3. **Static generation.** Reports are rendered from JSON by trusted plain code — **never** written by an agent. This keeps the LLM's blast radius at a JSON verdict and prevents script injection into the published site.

## 4. Scope

**In scope (MVP):** deterministic static scoring + sandboxed LLM judge for qualitative dimensions + JSON data model + static HTML reports + dashboard + human-review queue.

**Out of scope (optional Tier-2, only if time allows):** sandboxed dynamic execution of submissions; "Skill Lift" A/B measurement. Cut this first if behind schedule.

**Explicitly out of scope:** running untrusted submission code in the static phase; any public-internet AI API; any form of telemetry to external hosts.

## 5. Non-functional requirements

| Requirement | Target |
|---|---|
| Reproducibility | Same input + same `rubric_version`/`prompt_version`/`model_version` ⇒ same score |
| Auditability | Every score carries cited evidence + full provenance |
| Resumability | Pipeline can be killed and resumed without recomputation |
| Idempotency | Re-running an unchanged submission is a no-op (skipped) |
| Air-gap safety | Zero external network egress except the single internal LLM endpoint |
| Report portability | Generated HTML references **no** external URL, font, script, or stylesheet |
| Scale | 150+ submissions within the run window using a bounded worker pool |

## 6. Open decisions (lock BEFORE writing any prompt)

| # | Decision | Options | Default stance |
|---|---|---|---|
| D1 | Rubric weights | see `03-scoring-rubric.md` | Use the published weight profiles as-is |
| D2 | Business-value scoring | LLM judgment vs. structured checklist | **Structured `hackathon.yaml` checklist** (deterministic) |
| D3 | Track handling | single blended ranking vs. per-type sub-leaderboards | **Both**: overall + per-type sub-boards |
| D4 | Dynamic Tier-2 | include / defer | **Defer** unless static is fully done and reviewed |
| D5 | Human-review scope | gate failures only vs. gate + low-confidence | gate failures + low-confidence + top-N |
| D6 | Judge model + version | which internal endpoint | Pin ONE model + version for the whole run |
| D7 | Ensemble count | 1 vs. 2 vs. 3 judge passes | **2** (median), escalate if divergent |
| D8 | LLM endpoint concurrency | — | Measure in week 0; do not assume |

## 7. Step-one checklist (assemble before building)

1. **Frozen manifest** — 150+ repo URLs + type + team + submission commit SHA/tag.
2. **Rubric sign-off** — `03-scoring-rubric.md` weights locked by judges/stakeholders.
3. **Questionnaire template** — `hackathon-questionnaire-template.yaml` distributed with a deadline.
4. **Calibration set** — 10–15 repos across quality tiers × types, hand-scored by 2 humans.
5. **Internal LLM endpoint** — model id/version pinned; concurrency tested.
6. **InfoSec sign-off** — judge-isolation design (`04-security-design.md`) approved.
7. **Frozen schemas** — `/schemas/*.json` v1.
8. **GH Pages host confirmed** — serves static-only, no-CDN pages under current policy.

## 8. Acceptance criteria

- [ ] All 150+ submissions processed; every one has a `project_result` JSON and an HTML report.
- [ ] Hard-fail gate runs deterministically; identical on re-run.
- [ ] No report HTML contains any external URL reference.
- [ ] Every dimension score > 0 carries at least one cited evidence entry.
- [ ] Calibration set: LLM judge agrees with human judges within one score band.
- [ ] Judge process has no tools, no write path to score files, and default-deny egress.
- [ ] Dashboard loads standalone, sorts/filters client-side, and lists gate failures separately.
