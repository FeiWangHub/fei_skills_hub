---
name: codecup-eval-sonnet5
description: Use when designing, specifying, or building an AI-assisted judging/scoring system for an internal hackathon ("CodeCup") that evaluates AI Agent, Agent Skill, and source-code project submissions at a bank or enterprise. Provides the complete non-code requirements pack — official Agent/Skill schema references (Claude, GitHub Copilot, OpenCode), a weighted scoring rubric with anchored point scales, a zero-execution security checklist, LLM-as-judge prompt templates, JSON output schemas, pipeline architecture, and HTML/GitHub Pages report requirements. Contains no executable code — intended to be handed to an internal/air-gapped AI coding assistant for implementation.
---

# CodeCup Eval (Sonnet5) — AI 黑客松评分系统需求包

**Domain**: tooling / ai
**Status**: Draft — Requirements Pack (no implementation code)
**Last Updated**: 2026-09-13
**Author**: Fei Engineering (drafted with Sisyphus / Claude Sonnet 5)

## What It Does

This skill packages the **complete, code-free requirements** for building an AI-assisted judging system ("CodeCup Eval") that scores 150+ internally submitted hackathon projects — AI Agents (GitHub Copilot / OpenCode), Agent Skills, or plain source-code repositories — against a weighted rubric covering business value, technical architecture, security/compliance, engineering rigor, and documentation/schema conformance. Final output is a set of static HTML reports (one per project) plus a summary dashboard, published on GitHub Pages.

This package is **safe to transmit over email or internal messaging into an air-gapped AI coding assistant** because it contains zero executable scripts, zero application code — only Markdown specifications, illustrative YAML/JSON schema snippets, and LLM prompt templates.

### Use Cases

- Kicking off implementation of the CodeCup judging pipeline with an internal LLM / coding agent
- Onboarding a second engineer or vendor to build the scoring backend without re-deriving the rubric
- Briefing judges / compliance reviewers on how AI-assisted scoring works before rollout
- Re-running or auditing the rubric methodology in a future hackathon cycle
- Handing off to procurement/security review before any code is written

## Input Parameters (for the internal AI that implements this)

| Parameter | Type | Required | Description |
|---|---|---|---|
| `submission_manifest` | file (YAML/CSV) | Yes | List of the 150+ submissions: repo URL, type, track, contact. See `templates/submission-manifest-template.yaml`. |
| `llm_endpoint` | internal endpoint config | Yes | Private/internal-only LLM inference endpoint used for judging. Must NOT be a public internet AI API. |
| `artifact_type_override` | enum per submission | No | Manual override when auto-classification (see `references/09`) is ambiguous. |
| `tier2_enabled` | boolean | No (default: false) | Whether to run the optional dynamic/sandboxed execution pass. |

## What You'll Get

- A deterministic **hard-gate validator** report (schema conformance + security red flags) for every submission
- A structured **Tier 1 static score** (0-100, 5 weighted dimensions, with evidence citations) for every submission that passes the gate
- An optional **Tier 2 dynamic score** (+30 bonus points) for the top slice of submissions
- A **per-project HTML report page** and a **summary Dashboard page**, both statically generated and GitHub-Pages-ready
- A **human-review queue** listing gate failures and score-boundary cases requiring judge attention

## Reference Documents (read in this order)

| # | File | Purpose |
|---|---|---|
| 1 | `references/01-standard-claude-skill-spec.md` | Official Anthropic/Claude Agent Skill schema (SKILL.md frontmatter, size limits, quality bar) |
| 2 | `references/02-standard-github-copilot-agent-spec.md` | Official GitHub Copilot custom agent / instructions schema |
| 3 | `references/03-standard-opencode-agent-skill-spec.md` | Official OpenCode agent / skill / AGENTS.md schema |
| 4 | `references/04-scoring-rubric.md` | Full weighted rubric with 1/3/5-point anchors for every dimension, all 4 submission types |
| 5 | `references/05-security-static-checklist.md` | Zero-execution security/compliance scan checklist (pattern categories, not code) |
| 6 | `references/06-llm-judge-methodology.md` | LLM-as-judge best practices this system must follow |
| 7 | `references/07-dynamic-eval-metrics.md` | Tier 2 (optional, stretch) dynamic execution metrics definitions |
| 8 | `references/08-json-output-schema.md` | Canonical JSON schemas for judge output, per-project data, dashboard aggregate |
| 9 | `references/09-pipeline-and-architecture.md` | End-to-end pipeline, component responsibilities, data flow (no code) |
| 10 | `references/10-html-report-requirements.md` | Functional/content requirements for the HTML report site (no code) |
| 11 | `references/11-product-requirements-and-open-questions.md` | PRD-style summary, decisions needed, rollout plan, acceptance criteria |

## Prompt Templates (ready to paste into a Judge LLM call)

| File | Purpose |
|---|---|
| `templates/judge-prompt-skill-submission.md` | Full system-prompt template for grading Agent Skill submissions |
| `templates/judge-prompt-copilot-agent-submission.md` | Full system-prompt template for grading GitHub Copilot Agent submissions |
| `templates/judge-prompt-opencode-agent-submission.md` | Full system-prompt template for grading OpenCode Agent submissions |
| `templates/judge-prompt-source-project-submission.md` | Full system-prompt template for grading plain source-code projects |
| `templates/submission-manifest-template.yaml` | Data format for tracking the 150+ submissions |
| `templates/project-report-data-template.json` | Example structured data backing one project's HTML report |
| `templates/dashboard-aggregate-data-template.json` | Example structured data backing the summary Dashboard page |

## How It Works (Implementation Workflow for the Internal AI)

1. Read all reference docs (01-11) to build full context of standards, rubric, and pipeline.
2. Implement the **hard-gate validators** (schema conformance + security pattern scan) as described in `04` and `05` — these MUST run deterministically, with no LLM involved, before any LLM call.
3. Implement the **submission classifier** (Skill vs Copilot Agent vs OpenCode Agent vs source project) per detection rules in `09`.
4. Implement the **Tier 1 static Judge** using the matching prompt template (`templates/judge-prompt-*.md`), calling an **internal/private LLM endpoint only** (see Security Requirements below).
5. Implement **aggregation + ranking**, producing data conforming to `08`.
6. Implement **static HTML/GitHub Pages report generation** per `10`, consuming the JSON produced in step 5.
7. (Optional/Stretch) Implement **Tier 2 dynamic sandboxed execution** per `07`, gated to run only for the top-N% of Tier 1 scores, inside a network-isolated sandbox.
8. Wire up a **human-review queue** for gate failures and score-boundary cases per `06`.

## Prerequisites

- Access to an **internal/private LLM inference endpoint** (no calls to public internet AI APIs — hard security requirement, see `11`)
- Read access to the 150+ submission repositories (internal Git hosting)
- A GitHub Pages-capable repo (or internal equivalent static site host) to publish reports
- Stakeholder sign-off on the open questions in `references/11-product-requirements-and-open-questions.md` §"Open Decisions" before implementation starts

## Security Requirements (Non-Negotiable — this skill's own output must comply)

1. No external network calls or public AI API invocations anywhere in the implementation — internal/private LLM endpoints only.
2. No credential storage, no hardcoded tokens, in either the judging system itself or in what it flags inside submissions.
3. No data exfiltration — submission code/content must never leave the internal network boundary.
4. Sandboxed dynamic execution (Tier 2, if built) must run with **zero network egress**.
5. This requirements pack intentionally contains **no executable code** so it can be transmitted over email/internal messaging without triggering DLP/code-scanning policies.

## Troubleshooting

**Issue**: Internal AI cannot access the official Claude/GitHub/OpenCode doc URLs cited in references (air-gapped environment).
**Solution**: References `01`-`03` already contain the full extracted schema content inline — no live internet access is required to use them.

**Issue**: Rubric weights feel wrong for a specific track (e.g., pure research/data-science projects).
**Solution**: See `04-scoring-rubric.md` §"Track-Specific Weight Adjustments" for the allowed re-weighting procedure.

**Issue**: 150+ submissions is too many for synchronous LLM calls / review capacity.
**Solution**: See `09-pipeline-and-architecture.md` §"Batching & Throughput" for the recommended queued/batched processing design.

## Contributing

This is a project-specific internal skill for the CodeCup hackathon. Update reference docs directly via PR; do not fork without renaming.
