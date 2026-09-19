# 03 — Scoring Rubric

Two rubrics: **Static (mandatory, base 100 pts)** and **Dynamic (optional, modifier only)**. Dimension weights differ by artifact type via **weight profiles**.

---

## 1. Static rubric — dimensions and weights

| # | Dimension | Skill | Agent | Source | Method | Hard-fail gate? |
|---|---|:-:|:-:|:-:|---|---|
| D1 | Security & Compliance | 15 | 15 | 15 | Deterministic | **YES (caps score)** |
| D2 | Spec / Structural Compliance | 15 | 15 | 10 | Deterministic | Partial (fixed deduction) |
| D3 | Code / Content Quality | 20 | 20 | 25 | Hybrid (lint + LLM) | No |
| D4 | Documentation & Discoverability | 15 | 10 | 10 | Hybrid | No |
| D5 | Testing & Reliability | 10 | 15 | 20 | Deterministic | No |
| D6 | Business Value / Impact | 15 | 15 | 15 | Deterministic checklist | No |
| D7 | Innovation / Differentiation | 10 | 10 | 5 | LLM judge | No |
| | **Total** | **100** | **100** | **100** | | |

Weight profiles live in `templates/`-adjacent version `weight_profile` and are recorded in the result JSON. Adjust only via §5.

---

## 2. Dimension definitions and point anchors

Anchors are 1/3/5 bands mapped to the dimension's max points: `score = max × band/5` (rounded to 0.5). Every award > 0 requires ≥1 cited evidence entry.

### D1 — Security & Compliance (15)
- **Deterministic inputs:** secret/PII scan; license check; external-call detection in scripts; OWASP LLM/Agentic checklist (`04-security-design.md`); `allowed-tools`/`permission` least-privilege check.
- **5** — no secrets, no external calls, least-privilege tools, compliant license, no OWASP hits.
- **3** — minor issues (e.g., broad `bash: allow`, missing license file) with no exploitable pattern.
- **1** — clear risky pattern (data exfiltration, credential access, unpinned remote fetch).
- **Hard-fail (→ cap):** hardcoded credential, exfiltration pattern, prompt-injection payload embedded in the submission, license violation. Caps `overall_score` at ≤40 (F band) and sets `security_flag=true` → human review.

### D2 — Spec / Structural Compliance (15 skill & agent, 10 source)
- **Deterministic:** validate against `02-standards-and-formats.md`; name rules; description length; SKILL.md < 500 lines; L1/L2/L3 disclosure; for source: presence of build/manifest files.
- **5** — fully conformant, clean structure, references one level deep.
- **3** — required fields present but minor flaws (weak description, uppercased name, 500–800 lines).
- **1** — missing frontmatter/required fields, or monolithic > 800 lines.

### D3 — Code / Content Quality (20 skill & agent, 25 source)
- **Hybrid:** deterministic complexity/duplication/heading-hierarchy checks + LLM judge for clarity, instruction quality, correctness of examples.
- **5** — clear, actionable, no dead weight; every token earns its place.
- **3** — usable but requires interpretation; some redundancy or vague steps.
- **1** — confusing, contradictory, broken snippets.

### D4 — Documentation & Discoverability (15 skill, 10 agent/source)
- **Hybrid:** deterministic (description WHAT+WHEN; Jaccard trigger-collision vs. corpus; README/AGENTS.md presence) + LLM readability.
- **5** — precise triggers, distinct from sibling submissions, clear boundaries; README/usage docs present.
- **3** — present but generic; some overlap with other submissions.
- **1** — missing or unusable.

### D5 — Testing & Reliability (10 skill, 15 agent, 20 source)
- **Deterministic:** evals.json / test files / CI config presence; coverage number if reported; error-handling signals in scripts.
- **5** — meaningful tests + validation loops + CI.
- **3** — token tests or docs-only.
- **1** — none.

### D6 — Business Value / Impact (15)
- **Deterministic checklist against structured `hackathon.yaml`** (NOT LLM judgment). The LLM only *extracts* fields; the checklist *scores* them.
- **5** — quantified time/cost saved (a number), named target users, named sponsor, adoption evidence.
- **3** — qualitative value described, partial quantification.
- **1** — generic claim, no quantification, no stakeholder.

### D7 — Innovation / Differentiation (10 skill & agent, 5 source)
- **LLM judge**, rubric-anchored, scored relative to corpus anchors. Rewards genuine "knowledge delta" (non-obvious domain content) over boilerplate.
- **5** — non-obvious approach that materially changes the workflow.
- **3** — solid but incremental.
- **1** — trivial prompt wrapper / restates common knowledge.

---

## 3. Hard-fail gates (D1 only)

A gate failure does **not** zero visibility. It:
1. sets `hard_fail.triggered = true` with reasons,
2. caps `overall_score` at **≤ 40** (F band),
3. sets `security_flag = true`,
4. routes the submission to the **human-review queue** for InfoSec awareness.

---

## 4. Dynamic rubric (optional Tier-2 — modifier only)

Never a base-score component. Applied only to the top slice and only if static is fully done.

Reuse NVIDIA's published model:
- Static quality weights: **Correctness 0.35 / Discoverability 0.25 / Reliability 0.25 / Efficiency 0.15**.
- **Skill Lift** = `score(with_skill) − score(baseline)`: `≥ +5%` PASS, `−10%..+5%` NEUTRAL, `≤ −10%` FAIL.
- Metrics: task success rate, pass@k / pass^k stability, tool-call error rate, tokens per resolved task, context-expansion ratio.

Details in `06-dynamic-eval-metrics.md`.

---

## 5. Track-specific weight adjustments

Allowed only before the run starts and only with sign-off (recorded as a new `weight_profile` version). Procedure:
1. Propose a named profile (e.g., `research`, `data-science`).
2. Keep every dimension present; redistribute at most ±10 points total.
3. Re-run the calibration set and confirm judge–human agreement holds.
4. Freeze and version it; never edit mid-run.

---

## 6. Aggregation

```
overall_score = Σ (dimension_score)      # 0..100, per weight profile
final_score   = clamp(0, 100, overall_score [+ dynamic_modifier])
```
- Publish **per-type sub-leaderboards** (skill / copilot_agent / opencode_agent / source_project) **in addition to** one blended view.
- Each dimension carries `{score, max, method, evidence[], confidence}`.
- `needs_human_review` is computed **downstream** by the orchestrator — never set by the judge LLM itself.
