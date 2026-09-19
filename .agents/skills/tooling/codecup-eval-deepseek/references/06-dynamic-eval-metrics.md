# 06 — Dynamic Evaluation Metrics (Tier-2, optional)

**Status: optional / stretch. Cut this first if behind schedule.** Dynamic execution of 150+ unknown repos is the highest-risk, lowest-necessity phase. Static scoring is defensible and auditable on its own.

## 1. Purpose

Dynamic evaluation actually *runs* a skill/agent to measure whether it helps an agent perform a task — i.e., it measures **Skill Lift**, not just form quality.

## 2. Scope

- Applies to `skill`, `copilot_agent`, `opencode_agent` only (not arbitrary source projects).
- **Only** the top slice of static scores (e.g. top 20%) to bound cost and risk.
- **Only** inside an ephemeral, network-isolated sandbox.

## 3. Method (reused from NVIDIA SkillEvaluator)

A/B trial per eval case:
- **Arm A:** agent **with** the skill/agent.
- **Arm B:** baseline **without** it.
- Same task, same model, N attempts.
- Grader (LLM) scores each arm blind against the case's expected output/assertions.
- `Skill Lift = score(with) − score(baseline)`.

**Bands:** `≥ +5%` PASS · `−10%..+5%` NEUTRAL · `≤ −10%` FAIL.

## 4. Metric definitions

| Metric | Definition | Score band |
|---|---|---|
| Task Success Rate (TCR) | fraction of eval cases whose output passes assertions | 0–15 |
| Token Cost Efficiency | tokens per resolved task; context-expansion ratio; cohort percentile | 0–10 |
| Stability | `pass@k` (any-of-k succeeds) and `pass^k` (all-of-k succeed); tool-call error rate | 0–5 |
| Skill Lift | delta vs. baseline (above) | modifier only |

**Static quality weights** (for the qualitative sub-scores, reused): Correctness 0.35 / Discoverability 0.25 / Reliability 0.25 / Efficiency 0.15.

## 5. Application rule

- Tier-2 is a **modifier**, not a base component: it can adjust the final score within a bounded window, never replace the static score.
- `dynamic_modifier` and its inputs are recorded separately in `project_result.json` so the static score remains comparable across all submissions.
- Submissions not evaluated dynamically get `tier2.evaluated = false` and no modifier.

## 6. Sandbox requirements (mandatory)

- Ephemeral container, destroyed after run.
- **Zero network egress.**
- CPU / memory / wall-clock limits.
- Dedicated low-privilege service account.
- No visibility into other submissions.
- Judge/isolation controls from `04-security-design.md` apply here too.

## 7. Key metrics to report

- Token consumption per run and per resolved task.
- Correctness (assertion pass rate).
- Stability across repeated runs (variance).
- Relative lift vs. baseline.
