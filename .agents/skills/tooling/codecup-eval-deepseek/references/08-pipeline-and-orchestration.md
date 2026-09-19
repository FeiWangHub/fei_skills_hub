# 08 — Pipeline & Orchestration

## 1. Architecture (deterministic-first, agent-outside)

```
L0  Ingest     manifest(150+ repos @ frozen SHA) → read-only mirror (no execution)
L1  Static     artifact classifier → spec linters → secret/PII scan → license →
   (no LLM)    trigger-collision (Jaccard) → test presence → business-value checklist
               ≈70% of the score; deterministic; gates hard-fails
L2  Judge      sandboxed LLM judge on qualitative dimensions only
   (isolated)  tools = none; egress = only internal LLM endpoint; returns JSON text
L3  Aggregate  merge deterministic + LLM subscores → confidence → hard-fail cap →
   (no LLM)    needs_human_review → ranks
L4  Report     trusted static generator renders JSON → HTML (never LLM-written)
```

## 2. Decide: orchestrator vs. agent vs. skill

| Concern | Use | Why |
|---|---|---|
| The 150+ batch run, caching, resume, write-to-disk | **Deterministic program (orchestrator)** | reproducibility, scale, audit |
| The rubric / evidence rules / output contract | **A versioned Skill / prompt spec** | knowledge packaging, versioning, human reuse |
| Per-call ensembling (2×), isolated dynamic sandboxes | **Sub-agents (isolated calls)** | need independent context/isolation |

**Do NOT drive the 150-item loop with a main-agent+sub-agent chat.** That is non-deterministic, expensive (~10–50× token cost), not resumable, and hard to audit. The agent surface is for development/calibration and one-off deep reviews, not production batch scoring.

## 3. Orchestration rules

- **Fixed pipeline**, not free-form planning: `classify → static → gate → (if clear) judge → merge → write`.
- **Stateless judge calls**, one per submission, no shared memory (prevents cross-contamination; enables parallelism).
- **Concurrency:** worker pool sized to the internal endpoint's measured safe limit (start 8–16; measure in week 0).
- **Idempotency key:** `hash(commit_sha + rubric_version + prompt_version + model_version)`; unchanged ⇒ skip.
- **Resumability:** `manifest_state.json` tracks `pending | running | done | failed | hard-failed` per repo; safe to kill/restart.
- **Provenance:** each result embeds `{repo, commit_sha, scanned_at, model_id, model_version, prompt_version, rubric_version, orchestrator_version, tool_versions}`.
- **Raw transcripts** stored separately (audit-only; never published).

## 4. Batching & throughput

- Process in batches; persist state after each batch so a crash loses at most one batch.
- Run the deterministic layer across all 150+ first (cheap), then spend LLM calls only on the qualitative dimensions and (optionally) only after the gate.
- Cache deterministic results keyed by file hashes so a re-scan after a rubric tweak only re-runs changed rules.

## 5. Artifact-type classification (deterministic)

```
if exists <repo>/<...>/SKILL.md (or skill.md)     → skill
elif exists .github/agents/*.agent.md             → copilot_agent
elif exists .opencode/agent(s)/*.md or opencode.json agent block → opencode_agent
else                                               → source_project
```
Ambiguous cases → `artifact_type_override` in the manifest, resolved by a human before the run.

## 6. Failure handling

| Failure | Action |
|---|---|
| Malformed JSON from judge | retry ×2, then mark `failed` + human review |
| Endpoint timeout / rate limit | back off, requeue; never silently drop |
| Discriminating power zero (a dimension = same score for all) | flag rubric issue for review |
| Injection pre-screen hit | `security_flag=true` + human review, regardless of judge output |
