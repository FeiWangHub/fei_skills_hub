# LLM-as-Judge Methodology — Requirements for the Judge Agent

These are non-negotiable behavioral requirements for whatever internal LLM/agent implements Tier 1 scoring. They exist to make the AI-assisted scores **defensible to human judges and auditors**.

**Sources**: *Prometheus* (Kim et al. 2023), *MT-Bench/Chatbot Arena* (Zheng et al., NeurIPS 2023), *G-Eval* (Liu et al. 2023), *Large Language Models are not Fair Evaluators* (Wang et al. 2023), *ChatEval* (Chan et al. 2023).

---

## 1. Rubric-Anchored Scoring, Not Free-Form Numbers

The Judge must **never** be asked "rate this 1-10" without anchor definitions. Every dimension's prompt must embed the 1/3/5-band descriptions from `04-scoring-rubric.md` §2 verbatim. Free numeric guessing without anchors is the single biggest source of judge inconsistency in the literature.

## 2. Mandatory Chain-of-Thought Before the Score

The output schema (see `08-json-output-schema.md`) places `reasoning` **before** `score` in field order, and the prompt instructs the model to write reasoning first. Generating a number before reasoning causes the model to rationalize backward from an arbitrary first token — this is a well-documented failure mode.

## 3. Evidence Citation Is Mandatory, Not Optional

Every non-zero-deduction and every score must cite at least one `{file_path, line_or_range}` reference. A reasoning string with **no** evidence citation is treated as **invalid output** by the pipeline (should trigger a re-ask, not silent acceptance) — this is what makes the AI score auditable/trustworthy to human judges later.

## 4. Absolute (Single-Item) Scoring, Not Pairwise Comparison

With 150+ submissions, pairwise comparison is combinatorially infeasible and reintroduces position/order bias. Score each submission **independently against the fixed rubric**, never "is A better than B".

## 5. Bias Mitigations

- **Verbosity bias**: Explicit prompt instruction: *"Longer code, longer README, or more files does NOT indicate higher quality. Judge substance, not volume."*
- **Self-enhancement / style bias**: If a submission happens to be built with the same tool/model family as the Judge itself, this must not influence scoring — instruct the Judge to ignore which AI tool produced the artifact and focus only on the artifact's own merits per rubric.
- **Length-of-prompt bias in Dimension 5 (docs)**: A long README is not automatically band-5; band-5 requires the *specific* checklist items in `04-scoring-rubric.md`, not just word count.

## 6. Determinism & Reproducibility

- All Judge calls run at **temperature 0 to 0.1**.
- Given the same inputs (submission content + injected static-scan facts), two runs should produce scores within a small tolerance (±3 points per dimension). This is testable and should be spot-checked during rollout (run 10 submissions twice, compare).

## 7. Multi-Judge Ensembling for Boundary Cases

For submissions whose `final_score` lands within ±5 points of an award cutoff (see `04-scoring-rubric.md` §5), run a **second independent Judge pass** (either a different model, or the same model with an independently-sampled reasoning path at slightly higher temperature, e.g. 0.3, run twice and take the median). If the two `tier1_total` scores disagree by more than 8 points, escalate to human review rather than auto-averaging — an 8+ point disagreement signals the rubric application itself is ambiguous for that submission, which is a judge-quality signal worth a human look, not just noise to average away.

## 8. Structured Output Enforcement

The Judge call must use **constrained/structured decoding** (JSON schema-constrained generation, or strict schema validation + automatic re-ask on failure) against the schema in `08-json-output-schema.md`. Free-text responses that "mostly look like JSON" are not acceptable — malformed output must trigger an automatic retry (max 2 retries), then fall to human-review queue if still malformed.

## 9. What the Judge Is Explicitly Told NOT To Do

- Do not re-run your own security scan from scratch — use the injected `security_scan_result` facts (see `05-security-static-checklist.md` §"How This Feeds the Pipeline").
- Do not execute, simulate execution of, or "trace through" the submitted code as if running it — Tier 1 is static-only. (Tier 2, if enabled, is a separate sandboxed process, not something the Judge LLM does itself.)
- Do not give partial credit "just because effort is visible" — score against the band descriptions only.
- Do not penalize a submission for using a different AI tool/model than the Judge's own family.

## 10. Judge Prompt Assembly Order (applies to all `templates/judge-prompt-*.md`)

1. Role & scope statement (static-review-only, no execution)
2. Relevant official standard reference, injected inline (from `01`/`02`/`03` — whichever matches the detected artifact type)
3. Pre-computed facts block: gate result, security scan findings, contributor/commit stats, test-presence stats (all computed deterministically upstream — never left for the LLM to compute itself)
4. Rubric with band anchors (from `04`)
5. Explicit output schema (from `08`) with instruction to reason-then-score, cite evidence, and follow the bias-mitigation rules above
6. The actual submission content (README, SKILL.md/agent definition, selected source excerpts)
