# Tier 2 — Dynamic Evaluation Metrics (Optional / Stretch Goal)

Tier 2 requires actually **running** the submitted Agent/Skill against a small set of predefined test scenarios, inside a sandboxed, network-isolated environment. This document defines *what to measure*, not *how to build the sandbox* (no code/infra specifics here — that belongs in an implementation plan, not this requirements pack).

**Sources**: SWE-bench (Jimenez et al., ICLR 2024), τ-bench (Sierra et al., 2024), HumanEval/Codex pass@k (Chen et al., OpenAI 2021).

---

## 1. Preconditions Before Any Dynamic Run

- Submission has already passed Layer 0 (schema + security gate) — never dynamically execute a submission that failed the security gate.
- Submission's Tier 1 static score places it in the organizer-defined top slice (recommended default: top 30%, or top 20 submissions per track, whichever is smaller).
- Execution sandbox has **zero network egress** and a hard wall-clock timeout per run.
- Test scenarios are **predefined by organizers per track**, not invented ad hoc per submission (fairness requirement).

## 2. Correctness & Stability Metrics

### 2.1 Task Completion Rate (TCR)
```
TCR = (tasks the submission completed successfully) / (total predefined test tasks) × 100%
```
"Successfully" is defined by a predefined verification check per task (organizer-authored expected-outcome assertions), not subjective judgment.

### 2.2 Pass@k (Sampling Success)
Probability that at least 1 of *k* repeated attempts at the same task succeeds. Useful when the agent's output has some randomness. Standard unbiased estimator (Chen et al. 2021):
```
Pass@k = E[ 1 - C(n-c, k) / C(n, k) ]
```
where *n* = total sampled trials, *c* = number of successful trials, *k* ≤ *n*.

### 2.3 Pass^k (Consistency / Stability)
Probability that **all** *k* repeated runs of the identical task succeed — measures flakiness, which matters more than raw pass@k for something a bank might actually deploy:
```
Pass^k = (c / n)^k
```
Recommended bar for CodeCup: `Pass^3 ≥ 0.85` to be considered "stable" in the report (informational label, not a hard cutoff).

### 2.4 Tool Call Error Rate (TCER)
```
TCER = (invalid tool calls: schema violations + exceptions) / (total tool call invocations)
```
Only applicable to Agent submissions with tool-use.

## 3. Token & Cost Efficiency Metrics

### 3.1 Total Tokens per Run
Input + output tokens consumed per completed task attempt, recorded per run (not aggregated away — the report should show distribution, not just mean).

### 3.2 Cost Per Resolved Task (CPRT)
```
CPRT = Σ(cost of all trials) / (number of resolved trials)
```
Penalizes agents that burn tokens on failed loops without succeeding. Use the internal LLM endpoint's actual per-token rate for the calculation (or a standardized reference rate if the internal endpoint doesn't expose cost).

### 3.3 Trajectory / Step Efficiency
```
Step Efficiency = (organizer-defined "reasonable" step count for the task) / (actual steps the agent took)
```
Flags agents that technically succeed but wander through excessive tool calls before doing so.

### 3.4 Context Expansion Ratio (CER)
```
CER = (peak prompt token length during the run) / (initial prompt token length)
```
High CER with no summarization/pruning strategy signals a context-overflow risk on larger real-world inputs than the test scenario used.

## 4. Tier 2 Point Mapping (feeds back into `04-scoring-rubric.md` §3)

| Sub-dimension | Points | Mapping Rule |
|---|---|---|
| Task Success Rate | 15 | `points = round(TCR / 100 × 15)` |
| Token & Cost Efficiency | 10 | Relative ranking within the evaluated cohort (top quartile = 10, bottom quartile = 2.5), not an absolute formula — token costs vary too much by task type for an absolute scale to be fair |
| Stability/Resilience | 5 | `Pass^3 ≥ 0.85` → 5; `0.6–0.85` → 3; `<0.6` → 0 |

## 5. What Tier 2 Explicitly Does NOT Do

- It does not re-score security (that stays static-only, Layer 0 + Dimension 3).
- It does not run against production data or any real internal system — test scenarios use synthetic/mock fixtures only.
- It does not penalize submissions that simply chose not to opt into Tier 2 — Tier 2 is bonus-only, never a deduction for absence.
