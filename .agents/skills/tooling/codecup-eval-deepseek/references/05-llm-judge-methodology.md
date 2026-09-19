# 05 — LLM-as-Judge Methodology

The judge LLM is used **only** for the qualitative dimensions (D3 nuance, D4 readability, D7 innovation). Everything else is deterministic. This file defines how to keep the judge trustworthy and reproducible.

## 1. Evidence-required scoring (the core rule)

Borrowed from Anthropic's `grader.md`: **the burden of proof is on the claim.**

- Any dimension score **> 0 MUST cite ≥ 1 evidence entry** `{file_path, line/range, note}`.
- If the judge cannot cite evidence, the score is capped at the lowest band.
- The judge must quote, not paraphrase, when citing.
- Reject the response and retry (max 2×) if `evidence` is empty on a positive score, or if the output violates the JSON schema.

## 2. Prompt construction

- **System prompt = the matching `templates/judge-prompt-*.md`**, filled with: the rubric table, the artifact-type weight profile, and 2–3 **worked few-shot examples** with target scores.
- **Only relevant excerpts** are fed (entry file, key support files, README/test listing) — never a whole repo. Keeps prompts small, cheap, and reduces injection surface.
- Every excerpt is wrapped in `<UNTRUSTED_SUBMISSION_CONTENT>` per `04-security-design.md` C2.
- The prompt asks for strict JSON matching the `judge_output` shape (`07`).
- The prompt is **versioned and content-hashed** (`prompt_version`). Any wording change = new version + re-calibration.

## 3. Reproducibility controls

| Control | Setting |
|---|---|
| Model | One pinned model + version for the whole run |
| Temperature | `0` (or the endpoint's deterministic minimum) |
| Output | Strict JSON schema; reject+retry on violation |
| Versioning | `rubric_version`, `prompt_version`, `model_version` recorded on every result |
| Idempotency key | `hash(commit_sha + rubric_version + prompt_version + model_version)` |

## 4. Calibration set (do this before the run)

1. Pick 10–15 repos spanning quality tiers × all four artifact types.
2. Two humans independently score them; reconcile to a gold set (`calibration_gold.json`).
3. Tune prompt wording until LLM-vs-human agreement is **within one score band** on every dimension.
4. Then **freeze and hash the prompt.** Do not edit mid-run. Re-run calibration periodically to detect endpoint model drift.

## 5. Ensembling and confidence

- Run each LLM-judged dimension **2×** (same prompt, or a paraphrase) and take the **median**.
- If the two passes differ by more than a threshold (e.g. > 15/100 overall, or > 1 band on a dimension), set `confidence = "low"`.
- `confidence` values: `high` (agreement within 0.5 band), `medium` (within 1 band), `low` (> 1 band).
- **Low-confidence + high-rank combos MUST go to human review.** Never let an uncertain score decide a top prize.

## 6. Anti-patterns the judge must avoid (and the pipeline must detect)

| Anti-pattern | Countermeasure |
|---|---|
| Self-grading bias | Submission code never participates in judging (structural) |
| Rubric-satisficing / Goodhart | Evidence-required scoring + adversarial calibration (buzzword-stuffed weak submissions must score low) |
| Halo effect | "Score each dimension only on its own evidence — no halo from other dimensions" |
| Central tendency | Anchored 1/3/5 bands, not free 0–100 guessing |
| Verbosity reward | Length is not a quality signal; cap description/body scoring on token economy |

## 7. Output contract

The judge returns, per submission, a `judge_output` object (`07-data-model-and-schemas.md` §2): per-dimension `{band, score, reasoning, evidence[]}`, `strengths`, `weaknesses`, `observations_not_scored`, and the model/version/timestamp. It **never** sets `needs_human_review`, `rank`, or the final score — those are computed by the orchestrator.
