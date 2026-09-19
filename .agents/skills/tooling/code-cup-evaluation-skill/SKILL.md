---
name: code-cup-evaluation-skill
description: Use when designing, implementing, or auditing an AI-assisted evaluation system for internal hackathons or Code Cup competitions, especially when scoring 100+ submissions across mixed artifact types such as Skills, Copilot agents, OpenCode agents, and source-code projects. Provides a deterministic-first rubric, static security gate, allowlist-enforced network policy, concurrency model, LLM judge design, evidence requirements, JSON schema contract, and static reporting workflow for enterprise-scale evaluation. Also use when the user asks to scan a repository for hardcoded secrets or unapproved outbound endpoints.
license: MIT
compatibility: Requires Python 3.9+ for the bundled runtime scaffold. YAML manifests need PyYAML; a JSON manifest works with no third-party dependency. The optional judge stage requires a reachable internal/private LLM endpoint on the approved allowlist.
metadata:
  version: "0.1.0"
  author: Fei Engineering
  organization: Fei Engineering
  date: September 2026
  last_updated: "2026-09-19"
  status: draft
  domain: tooling / ai
  maturity: reference-implementation
  abstract: A security-first, deterministic evaluation framework for large-scale internal hackathon judging. Covers artifact classification, a no-LLM static security gate, an allowlist-enforced network policy, a constrained LLM judge with mandatory evidence, weighted aggregation with confidence scoring, and static HTML reporting. Ships a dependency-free Python reference implementation of the ingest and static-gate layers, with a standard-library test suite.
  keywords:
    - hackathon-judging
    - llm-as-judge
    - evaluation-rubric
    - secret-scanning
    - prompt-injection
    - network-allowlist
    - artifact-classification
    - code-cup
  applies_to:
    - internal-hackathon
    - code-cup
    - submission-evaluation
  language: markdown
  entrypoint: SKILL.md
  implementation: code/
  templates: templates/
  tested_with: Python 3.9 and 3.14
---

# Code Cup Evaluation Skill

**Domain**: tooling / ai  
**Version**: 0.1.0  
**Status**: Draft — evaluation architecture & requirements  
**Author**: Fei Engineering  
**Last Updated**: 2026-09-19  
**License**: MIT

## Skill Metadata

Frontmatter follows the official skill spec. Only these top-level keys are permitted — `name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility`. `version`, `author`, and similar fields must be nested under `metadata`, because a top-level `version` or `author` is rejected by the validator.

| Field | Value |
|---|---|
| `name` | `code-cup-evaluation-skill` (kebab-case, ≤64 chars) |
| `license` | MIT |
| `metadata.version` | 0.1.0 |
| `metadata.author` | Fei Engineering |
| `metadata.status` | draft |
| `metadata.maturity` | reference-implementation |
| `metadata.testing` | `code/tests/`, standard library only |

`compatibility` declares the runtime needs: Python 3.9+, optional `PyYAML` for YAML manifests, and a reachable internal LLM endpoint for the optional judge stage.

`allowed-tools` is deliberately omitted. This skill ships Python modules that the user runs explicitly; it does not need to invoke tools on the user's behalf, so declaring tool permissions would over-ask.

## What It Does

This skill turns the Code Cup evaluation design document into an actionable internal playbook for building an AI-assisted judging pipeline for a large internal hackathon. It is designed for scenarios with around 150 teams and 300–400 participants, where submissions may include:

- AI Agent Skills
- Copilot / OpenCode agent definition files
- Source-code repositories
- Mixed artifact types in the same competition

The skill guides the construction of a batch evaluation system that:

- classifies each submission by artifact type
- runs security and compliance gates with no LLM involvement
- applies a deterministic, weighted rubric
- uses a constrained LLM judge only for qualitative dimensions
- aggregates results into structured JSON output
- renders final scores into static HTML reports

This skill is intended for enterprise/intranet use and prioritizes reproducibility, auditability, safe isolation, and cost control over agentic free-form planning.

### Use Cases

- Designing the architecture for a bank or enterprise internal hackathon scoring system
- Evaluating AI Agent, Agent Skill, and repository submissions in bulk
- Implementing a batch scoring system for 100+ submissions
- Defining a rubric with evidence-based scoring and JSON output contracts
- Building risk controls to prevent prompt injection, credential leakage, and model bias
- Creating static leaderboard and per-team report pages without unsafe LLM-generated HTML

## Core Design Philosophy

### Deterministic-first pipeline

The system should be structured as a strict, fixed pipeline instead of a free-form autonomous planner:

1. Ingest manifest and freeze commit SHA
2. Static classification and security gating
3. Optional artifact validation and structure checks
4. LLM judge only for qualitative dimensions
5. Aggregation, confidence, ranking, and filtering
6. Static report generation

Do not allow the judge model to decide the pipeline or perform arbitrary planning. The orchestrator is responsible for flow control, state, retries, and output persistence.

### LLM judge is not a worker pool

The scoring system should not create 150 agents or 150 CLI processes as the primary concurrency model. Instead, use:

- one deterministic orchestrator
- a bounded worker pool for static analysis
- a token-bucket-limited LLM judge layer
- idempotent state files and resumable processing

The LLM should act as a constrained judge, not as a mini-ecosystem.

## Inputs to Ask For

| Parameter | Type | Required | Description |
|---|---|---|---|
| `submission_manifest` | file | Yes | A frozen list of all repos, commit SHAs, team metadata, and artifact classification info |
| `artifact_types` | enum list | Yes | Supported types such as `skill`, `copilot_agent`, `opencode_agent`, `source_project` |
| `llm_endpoint` | internal config | Yes | Private/internal LLM endpoint only; no public internet AI API |
| `rubric_version` | string | Yes | Versioned scoring rubric; frozen and hashed |
| `report_target` | string | Yes | Internal static host / GitHub Pages / enterprise HTML publishing target |
| `dynamic_eval_enabled` | boolean | No | Whether to enable optional sandboxed execution pass for a small subset |
| `artifact_type_override` | map | No | Manual override if classifier is uncertain |

## Expected Outputs

- A batch evaluation manifest with state transitions such as `pending`, `running`, `done`, `failed`, `hard-failed`
- Per-submission static evaluation results with evidence fields and confidence metadata
- A JSON leaderboard and project result bundle complying with a schema contract
- A static HTML report for each project
- A summary dashboard for ranking and filtering
- A human review queue for gate failures and low-confidence outputs

## Main Architecture

```text
L0 Ingest
  manifest(150 repos @ frozen SHA) -> read-only snapshot

L1 Static Gate
  artifact classification -> spec validation -> secret/PII scan -> license check
  injection pre-screen -> test presence check -> business value checklist
  no LLM involved

L2 Judge
  isolated LLM judge for qualitative dimensions only
  tools = none
  egress = internal LLM endpoint only
  strict JSON output

L3 Aggregate
  deterministic score + LLM partial score -> confidence -> hard-fail cap -> ranking
  weights live in config, not in LLM logic

L4 Report
  static HTML generation from JSON only
  no LLM-generated HTML
```

## Scoring Model

### Evaluation dimensions

The design document recommends a 7-dimension rubric for final scoring:

- D1 Security and compliance
- D2 Standards and structure conformity
- D3 Code and content quality
- D4 Documentation and discoverability
- D5 Testing and reliability
- D6 Business value and impact
- D7 Innovation and differentiation

A simplified 5-dimension mapping may also be used, but the 7-dimension version is more usable for mixed artifact types.

### Weighting

Use artifact-specific weight profiles:

- skill
- copilot agent
- opencode agent
- source project

Weights must be versioned and stored in config so the scoring is reproducible and auditable.

### Anchored scoring

Use a fixed anchor scheme instead of free-form 0–100 scoring. Recommended approach:

- 1-point band for weak
- 3-point band for acceptable
- 5-point band for strong

This reduces variance between reviewers and makes LLM output more stable.

## Critical Security Rules

1. Never run submission code in the default pipeline without a hardened sandbox.
2. Never allow the judge model to access arbitrary UAT links directly; use orchestrator-based probe checks only.
3. Replace team names, countries, flags, and region labels with anonymized tokens before LLM evaluation.
4. Do not allow network egress for dynamic execution; isolate it with zero outbound access.
5. Treat prompt-injection and malicious README content as a real threat vector.
6. Keep all raw prompts, responses, and submission content within internal boundaries and sensitive-data handling procedures.
7. Enforce a strict outbound allowlist: the evaluation system must only contact the internal/private LLM endpoint and approved internal hosts. No public internet domains, no arbitrary external APIs, and no outbound requests to non-`.example` hosts unless explicitly approved by security policy.
8. For any static scanning pass on a repository, the tool must read files locally and never exfiltrate source code or secrets beyond the internal evaluation environment.

## Official Standards to Reference

This skill should reference the relevant official specs as validation sources, but the implementation should prefer local copies or extracted excerpts when the environment is air-gapped. The primary references are:

- Anthropic / Claude: Skill schema and agent conventions, used as a reference for artifact validation and quality checks
- GitHub Copilot: custom agent and instruction-file schema conventions, used for repository classification and structure validation
- OpenCode: agent definition structure and tool/metadata rules, used for artifact-type detection and compatibility checks

These references should be treated as specification inputs, not as runtime network dependencies. If the environment cannot reach those external sites directly, the skill should rely on a locally stored extracted copy or an internal documentation mirror.

## Static Security Scan Requirements

Before any LLM evaluation, every submission should pass a deterministic static scan. The scanner should at minimum detect:

- hard-coded credentials and secrets (API keys, OAuth tokens, cloud keys, JWTs, private keys)
- suspicious URLs and outbound calls to non-approved domains
- insecure network behavior in config files, scripts, CI pipelines, and app settings
- prompt-injection patterns in README or skill metadata
- PII and internal-host leakage
- dangerous shell or package-install commands that could exfiltrate data or reach unknown endpoints

Recommended tooling for a first pass:

- `gitleaks` for credential scanning
- `trufflehog` or equivalent secret detection
- `semgrep` for risky patterns and injection signatures
- custom regex / YAML / JSON checks for internal-domain restrictions and suspicious endpoints
- repository-level checks for `.env`, credentials files, CI secrets, and embedded tokens

The static scan must be non-invasive: it reads source files and metadata but does not execute submission code and does not connect to arbitrary external websites.

### Required gate behavior

The static gate must fail closed:

- if a credential is found, mark `hard-failed`
- if a suspicious external domain is found, mark `hard-failed` unless it is explicitly on the approved allowlist
- if prompt injection content is found in README / skill / agent metadata, escalate to human review
- if the repository contains telemetry or network calls to unapproved domains, block the submission before the LLM stage

## Network Egress Policy

The evaluation system should implement an explicit allowlist policy:

- Allowed: internal/private LLM endpoint, internal artifact storage, internal Git host, internal static report host, approved `.example` domains
- Allowed only when explicitly approved: internal UAT / test endpoints used by the judge, but only via orchestrator-controlled probes
- Blocked by default: public internet domains, arbitrary external HTTP calls, unapproved SaaS APIs, and any domains outside the approved `.example` internal estate unless explicitly authorized by security policy

This rule should be enforced at the orchestrator level before the judgment stage runs. In other words, the pipeline should fail closed: if a repo tries to reach an unapproved domain, it should be flagged for review or blocklisted before LLM scoring is attempted.

### Network policy rule

The implementation should enforce the following logic:

```text
if destination_host not in allowlist and destination_host not in approved_internal_example_list:
    block_request
else:
    allow_request
```

The default posture is: no network egress outside the approved internal boundary.

## Baseline Output Contract (JSON)

Every submission produces one result object covering submission metadata, the static gate outcome, seven dimension scores, a total, confidence, a review flag, cited evidence, and provenance.

The authoritative field-level contract is `templates/result.schema.json` — read it before changing the output shape. It is not duplicated inline here, because a second copy would drift.

The orchestrator must reject any result object that violates the contract, or that reports a positive score without accompanying evidence.

## LLM Judge Rules

The judge must be constrained and deterministic:

- fixed model and version for the whole run
- temperature at or near zero
- strict JSON schema output only
- evidence required for any positive score
- no tools, no file writes, no ranking logic
- one result per submission and per rubric dimension, with confidence attributes

### Evidence rule

For any score greater than zero in a dimension, the model must cite at least one evidence item:

- `file_path`
- `line_or_range`
- `note`

If no evidence is provided, cap the score at the lowest valid band.

### Ensembling and confidence

Run two judge calls per dimension and take the per-dimension median. Confidence is derived from the widest disagreement across dimensions, not from the model's self-report:

- `high`: no disagreement, and at least two passes
- `medium`: disagreement of one band, or only a single pass
- `low`: disagreement exceeds one band

Entities with low confidence and a high rank must be routed to a human review queue.

## Concurrency and Throughput Design

### Concurrency limit should be endpoint-driven, not CPU-driven

The LLM judge is not meant to scale by launching 150 independent agent processes. Instead:

- static scan and ingestion can use a bounded worker pool
- LLM evaluation uses a rate-limited queue
- concurrency is set from endpoint quotas such as RPM / TPM, not from raw machine capacity

A practical starting point is around 8–16 parallel LLM workers for a 150-submission run.

### Required queue behaviors

- idempotent keys for resumed runs
- state persistence across crash and restart
- exponential backoff and jittered retry
- dead-letter queue for permanent failures
- provenance metadata appended to each result

### Provenance fields

Each output should include:

- repo name or identifier
- commit SHA
- scanned_at
- model_id
- model_version
- prompt_version
- rubric_version
- orchestrator_version
- tool_versions

## Data and Output Contract

Each result must carry submission metadata, classification, gate outcome, dimension scores, confidence, rank, and provenance. The full field-level contract lives in `templates/result.schema.json`; the runtime emits it as `execution-state.json`, which `report_generator.py` renders without any LLM involvement.

Only submissions that clear the static gate and complete a judge pass are ranked. Hard-failed and failed submissions are excluded from ranking entirely and must never be presented as scored entries.

## Runtime Scaffold (`code/`)

A dependency-free reference implementation of the L0/L1 layer ships with this skill. It enforces the allowlist, classifies artifacts, runs the static gate, and validates judge output. It performs no network calls and never executes submitted code.

| File | Purpose |
|---|---|
| `code/manifest_loader.py` | Load and validate the frozen submission manifest |
| `code/artifact_classifier.py` | Deterministic artifact-type classification |
| `code/allowlist.py` | Default-deny network allowlist decisions |
| `code/static_scanner.py` | Secret, injection, dangerous-script, and external-host scanning |
| `code/judge_adapter.py` | Judge prompt assembly and strict JSON contract validation |
| `code/judge_transport.py` | The only module allowed to open a connection; refuses non-allowlisted hosts |
| `code/aggregator.py` | Weighted scoring, median reconciliation, confidence, ranking |
| `code/report_generator.py` | Deterministic, escaped, CDN-free HTML reports |
| `code/orchestrator.py` | Pipeline entry point and aggregate state output |
| `code/tests/test_gates.py` | Standard-library tests for the gates |
| `code/tests/test_pipeline.py` | Standard-library tests for aggregation, egress, and reports |

### Running it

```bash
cd code
PYTHONPATH=. python3 tests/test_gates.py
PYTHONPATH=. python3 tests/test_pipeline.py
PYTHONPATH=. python3 orchestrator.py \
  --manifest ../templates/submission-manifest-template.yaml \
  --allowlist ../templates/allowlist.json \
  --repo-root /path/to/repo-snapshots \
  --out ./out \
  --rubric ../templates/score-rubric.yaml
```

Output is written to `out/execution-state.json`, with HTML in `out/reports/` (`index.html` plus one page per submission). Pass `--no-report` to skip rendering.

### Wiring in the judge stage

`orchestrator.py` deliberately stops at the static gate and leaves passing records in `awaiting-judge`. Supplying a score without a real judge call would fabricate results, so the judge stage is wired in explicitly by the caller:

```python
from allowlist import NetworkAllowlist
from judge_transport import JudgeTransport, TransportConfig

transport = JudgeTransport(
    TransportConfig(endpoint_url="https://llm.internal.example/v1/chat/completions",
                    model="<internal-model-id>"),
    allowlist=NetworkAllowlist.from_file("../templates/allowlist.json"),
    api_key=None,  # supply from the platform's secret store, never hardcode
)
```

`JudgeTransport` checks the allowlist before every request and raises `EgressBlockedError` if the endpoint is outside the approved boundary. For prompt assembly, evidence-bundle selection, and untrusted-content wrapping, see `references/judge-prompt-assembly.md`.

### Dependency note

YAML manifests require `PyYAML`. In a locked-down environment where `PyYAML` is unavailable, convert the manifest to JSON — the loader falls back to `json` with no third-party dependency. Python 3.9+ is sufficient.

`judge_adapter.run_judge` takes a caller-supplied `transport` callable rather than opening a connection itself, so the adapter cannot bypass the network policy.

## Recommended Workflow for Implementation

1. Freeze the submission manifest and identify the exact commit SHA for each repo.
2. Run classification and static validation in a read-only environment.
3. Hard-fail insecure or malformed submissions before any LLM evaluation.
4. Prepare a small gold set of benchmark repos for rubric calibration.
5. Use a fixed judge prompt version and score band schema.
6. Run two-pass judge calls with evidence enforcement.
7. Aggregate deterministic and LLM-derived components into the final score.
8. Check confidence and route low-confidence/high-rank cases to manual review.
9. Generate static HTML pages and summary dashboard from the JSON artifact.

## Important Edge Cases

### Git history matters

Do not use shallow clones for scoring that depends on collaboration metrics. `git shortlog` and `git log --numstat` analysis — used for "did everyone commit" and "was this cross-region" — are silently distorted by a shallow clone.

### Artifact type classification

Classify by file shape, deterministically:

- `SKILL.md` / `skill.md` → skill
- `.github/agents/*.agent.md` → Copilot agent
- `.opencode/agent(s)/*.md` or `opencode.json` → OpenCode agent
- otherwise → source project

Ambiguous cases should be manually overridden before batch scoring begins. `artifact_classifier.py` implements these rules and reports the rationale; a mismatch between the declared and detected type is recorded rather than silently resolved.

### Cross-team duplication and plagiarism

Add a deduplication layer using minhash or embedding similarity checks, because templates and starter code often produce near-duplicate artifacts within a large cohort.

### UAT access

Do not allow the LLM to browse UAT or internal systems directly. Use orchestrator-driven checks instead:

- HTTP status
- TLS validity
- latency / response time
- screenshot
- console error detection
- dead-link verification

## Practical Implementation Guidance

**Preferred stack pattern:** a deterministic orchestrator handling queueing, caching, and idempotency; a bounded worker pool for static checks; an isolated, rate-limited LLM judge; and a JSON + static HTML output layer.

**Prompt design:** feed only the relevant evidence bundle (entry files, README, key supporting docs) rather than the whole repository. Wrap untrusted content in explicit "not instructions" markers and version and hash every prompt.

**Report generation rule:** never let an LLM write the final HTML. Render it deterministically from validated JSON.

## Security / Compliance Checklist

- Internal/private LLM endpoint only
- No public API calls
- No credential parsing or storage in the scoring system
- No code execution in the default path
- No network egress in sandboxed execution
- Audit log kept for prompts, outputs, and provenance
- Sensitive submission data managed according to internal policy

## Troubleshooting

**Issue**: The team wants to use one massive autonomous agent to score all 150 projects  
**Solution**: Reject that pattern. For this scale, a deterministic orchestrator with bounded LLM calls is more reliable, cheaper, and easier to audit.

**Issue**: The scoring results are too noisy or inconsistent  
**Solution**: Freeze the rubric, add a gold set, enforce evidence requirements, and use anchor bands instead of free-form 0–100 scores.

**Issue**: The LLM judge appears to over-score weak projects  
**Solution**: Require evidence citations, use adversarial calibration, and push low-confidence/high-rank cases into human review.

**Issue**: There are many mixed artifact types  
**Solution**: Apply artifact-type-specific weight profiles and classification rules before scoring begins.

## Contributing

This skill is intended for internal hackathon design and evaluation architecture. Update the rubric, security gates, or output contract in a versioned way when the evaluation process changes.

---

**Tip**: This skill is intentionally designed to favor reproducible scoring, auditability, and safe enterprise deployment over open-ended autonomous agent behavior.
