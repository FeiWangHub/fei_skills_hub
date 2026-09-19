---
name: codecup-eval-deepseek
description: Use when designing, specifying, or building an AI-assisted judging/scoring system for an internal hackathon ("CodeCup") that evaluates AI Agent, Agent Skill, and source-code project submissions at a bank or enterprise. Provides a complete, code-free requirements pack — official Agent/Skill schema references (Claude, GitHub Copilot, OpenCode), a deterministic-first weighted scoring rubric with per-artifact-type weight profiles, a judge-isolation security design, LLM-as-judge methodology, JSON schemas, pipeline architecture, and HTML/GitHub Pages report requirements. Contains no executable code — intended to be handed to an internal/air-gapped AI coding assistant for implementation.
---

# CodeCup Eval (DeepSeek variant) — AI 黑客松评分系统需求包

**Domain**: tooling / ai
**Status**: Draft — Requirements Pack (no implementation code)
**Last Updated**: 2026-09-13
**Author**: Fei Engineering (drafted with Sisyphus / DeepSeek)
**Variant note**: Sibling to `codecup-eval-sonnet5`. This variant is opinionated toward **deterministic-first scoring** (≈70% of the score computed without any LLM) and **judge isolation** (the LLM judge has zero tools and cannot write its own score). See `references/01-requirements.md` §"Design stance".

## What It Does

This skill packages the **complete, code-free requirements** for building an AI-assisted judging system ("CodeCup Eval") that scores 150+ internally submitted hackathon projects — AI Agents (GitHub Copilot / OpenCode), Agent Skills, or plain source-code repositories — against a weighted rubric. It defines:

- The **three official artifact standards** to validate submissions against (Claude Agent Skill, GitHub Copilot custom agent, OpenCode agent) plus a **normalized cross-tool schema**.
- A **deterministic-first scoring engine** with hard-fail security gates and a sandboxed LLM judge for the qualitative remainder.
- **JSON schemas** (project result + leaderboard + manifest + questionnaire) and **format files** (manifest + business-value questionnaire templates).
- **Report requirements** for a per-project HTML page and a sortable summary dashboard on GitHub Pages.

This package is **safe to transmit over email or internal messaging into an air-gapped AI coding assistant** because it contains zero executable scripts and zero application code — only Markdown specifications, JSON Schemas, and illustrative YAML/JSON templates.

### Use Cases

- Kicking off implementation of the CodeCup judging pipeline with an internal LLM / coding agent
- Onboarding a second engineer or vendor to build the scoring backend without re-deriving the rubric
- Briefing judges / compliance reviewers on how AI-assisted scoring works before rollout
- Comparing two rubric-design philosophies (this DeepSeek variant vs. the sibling Sonnet5 variant)
- Handing off to procurement/security review before any code is written

## Input Parameters (for the internal AI that implements this)

| Parameter | Type | Required | Description |
|---|---|---|---|
| `submission_manifest` | file (YAML) | Yes | List of the 150+ submissions: repo URL, type, track, contact, pinned commit SHA. See `templates/submission-manifest-template.yaml` and `schemas/submission_manifest.schema.json`. |
| `hackathon_questionnaire` | file (YAML, per submission) | Yes | Structured business-value inputs supplied by each team. See `templates/hackathon-questionnaire-template.yaml`. |
| `llm_endpoint` | internal endpoint config | Yes | Private/internal-only LLM inference endpoint used by the judge. Must NOT be a public internet AI API. |
| `artifact_type_override` | enum per submission | No | Manual override when auto-classification (see `references/08`) is ambiguous. |
| `dynamic_eval_enabled` | boolean | No (default: false) | Whether to run the optional Tier-2 sandboxed execution pass. |

## What You'll Get

- A deterministic **hard-gate result** (schema conformance + security red flags) for every submission
- A **static score** (0–100, 7 weighted dimensions with per-type weight profiles and evidence citations) for every submission that passes the gate
- An optional **dynamic score** (bonus/penalty modifier, not a base component) for the top slice only
- A **per-project HTML report page** and a **sortable/filterable summary dashboard**, both statically generated and GitHub-Pages-ready, with zero external (CDN) references
- A **human-review queue** listing gate failures and low-confidence / score-boundary cases

## Reference Documents (read in this order)

| # | File | Purpose |
|---|---|---|
| 1 | `references/01-requirements.md` | Product requirements, design stance, scope, open decisions, acceptance criteria |
| 2 | `references/02-standards-and-formats.md` | Official Claude Skill / Copilot agent / OpenCode agent schemas + normalized cross-tool schema |
| 3 | `references/03-scoring-rubric.md` | Full weighted rubric, per-type weight profiles, anchored point scales, hard-fail gates, static vs dynamic |
| 4 | `references/04-security-design.md` | Threat model (incl. ToxicSkills/prompt-injection-via-submission), judge isolation controls, OWASP checklist |
| 5 | `references/05-llm-judge-methodology.md` | LLM-as-judge rules: evidence-required, calibration set, ensembling, confidence, prompt versioning |
| 6 | `references/06-dynamic-eval-metrics.md` | Tier-2 (optional) dynamic execution metrics: correctness, stability, token efficiency, Skill Lift |
| 7 | `references/07-data-model-and-schemas.md` | Explains the JSON schemas in `/schemas` and the field-level contract between stages |
| 8 | `references/08-pipeline-and-orchestration.md` | End-to-end pipeline, deterministic orchestrator vs. agents, batching, caching, resumability, provenance |
| 9 | `references/09-reporting-and-github-pages.md` | Per-project report + dashboard requirements, static-generation rule, no-CDN rule |
| 10 | `references/10-industry-rubrics-and-sources.md` | Benchmark of 9 existing skill-evaluation tools + industry frameworks and citations |

## Schemas (machine-readable contracts)

| File | Purpose |
|---|---|
| `schemas/project_result.schema.json` | One aggregated result record per submission |
| `schemas/leaderboard.schema.json` | The dashboard/leaderboard aggregate |
| `schemas/submission_manifest.schema.json` | The frozen submission list |
| `schemas/hackathon_questionnaire.schema.json` | Structured business-value inputs |

## Prompt & Format Templates

| File | Purpose |
|---|---|
| `templates/judge-prompt-skill.md` | System-prompt template for grading Agent Skill submissions |
| `templates/judge-prompt-copilot-agent.md` | System-prompt template for grading GitHub Copilot agent submissions |
| `templates/judge-prompt-opencode-agent.md` | System-prompt template for grading OpenCode agent submissions |
| `templates/judge-prompt-source-project.md` | System-prompt template for grading plain source-code projects |
| `templates/submission-manifest-template.yaml` | Example frozen submission list |
| `templates/hackathon-questionnaire-template.yaml` | Business-value questionnaire (filled by each team) |
| `templates/project-report-data-template.json` | Example data backing one project's HTML report |
| `templates/leaderboard-data-template.json` | Example data backing the dashboard page |

## How It Works (Implementation Workflow for the Internal AI)

1. Read all reference docs (01–10) to build full context.
2. Implement the **deterministic static layer first** (`references/03`, `references/04`): artifact-type classifier, spec linters for the three standards, secret/PII scan, license check, trigger-collision (Jaccard), test-presence check, business-value checklist. **These MUST run with no LLM and no execution of submission code.**
3. Implement the **hard-fail gate** and route failures to the human-review queue.
4. Implement the **sandboxed LLM judge** (`references/05`) for the qualitative dimensions only, using the matching `templates/judge-prompt-*.md`. The judge returns JSON text and **has no tools and no write access**.
5. Implement **aggregation + ranking** producing data conforming to `/schemas`.
6. Implement **static report generation** (`references/09`) from the JSON — never let an LLM write HTML.
7. (Optional/Stretch) Implement **Tier-2 dynamic sandboxed execution** (`references/06`) for the top slice only, inside a network-isolated sandbox.
8. Wire up the **human-review queue** for gate failures and low-confidence cases.

## Prerequisites

- An **internal/private LLM inference endpoint** (no calls to public internet AI APIs — hard requirement; see `references/04`)
- Read access to the 150+ submission repositories (internal Git hosting)
- A GitHub Pages-capable repo (or internal equivalent static host) to publish reports
- Stakeholder sign-off on the "Open Decisions" in `references/01-requirements.md` before implementation starts
- InfoSec sign-off on the judge-isolation design in `references/04-security-design.md`

## Security Requirements (Non-Negotiable — this skill's own output must comply)

1. No external network calls or public AI API invocations anywhere in the implementation — internal/private LLM endpoints only.
2. No credential storage, no hardcoded tokens, in either the judging system or in what it flags inside submissions.
3. No data exfiltration — submission content must never leave the internal network boundary.
4. Sandboxed dynamic execution (Tier 2, if built) must run with **zero network egress**.
5. This requirements pack intentionally contains **no executable code** so it can be transmitted over email/internal messaging without triggering DLP/code-scanning policies.

## Troubleshooting

**Issue**: The internal AI cannot reach the official Claude/GitHub/OpenCode doc URLs cited in `references/02`.
**Solution**: `references/02-standards-and-formats.md` contains the full extracted schema inline — no live internet access is required.

**Issue**: Rubric weights feel wrong for a specific track (e.g., pure research/data-science projects).
**Solution**: See `references/03-scoring-rubric.md` §"Track-Specific Weight Adjustments" for the allowed re-weighting procedure.

**Issue**: 150+ submissions is too many for synchronous LLM calls.
**Solution**: See `references/08-pipeline-and-orchestration.md` §"Batching & Throughput".

**Issue**: A judge gives implausibly high scores.
**Solution**: See `references/04-security-design.md` §"Anomaly detection" and `references/05-llm-judge-methodology.md` §"Confidence & escalation".

## Contributing

This is a project-specific internal skill for the CodeCup hackathon. Update reference docs directly via PR; do not fork without renaming.
