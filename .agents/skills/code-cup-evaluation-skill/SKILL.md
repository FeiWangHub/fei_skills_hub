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
  last_updated: "2026-09-20"
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

`compatibility` declares the runtime needs: Python 3.9+, optional `PyYAML` for YAML manifests, and a reachable internal LLM endpoint for the optional judge stage.

`allowed-tools` is deliberately omitted. This skill ships Python modules that the user runs explicitly; it does not need to invoke tools on the user's behalf, so declaring tool permissions would over-ask.

## What It Does

An actionable playbook for building an AI-assisted judging pipeline for a large internal hackathon — the scale it targets is around 150 teams and 300–400 participants, with submissions that may be AI Agent Skills, Copilot/OpenCode agent definitions, source-code repositories, or a mix of all three.

The pipeline it describes classifies each submission by artifact type, runs security and compliance gates with no LLM involvement, applies a deterministic weighted rubric, uses a constrained judge only for the qualitative dimensions, aggregates into structured JSON, and renders static HTML reports.

It is intended for enterprise/intranet use and prioritizes reproducibility, auditability, safe isolation, and cost control over agentic free-form planning.

### Use Cases

- Designing an architecture for a bank or enterprise internal hackathon scoring system
- Evaluating AI Agent, Agent Skill, and repository submissions in bulk
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
| `submission_manifest` | file | Yes | Frozen list of repos, commit SHAs, team metadata, artifact classification |
| `artifact_types` | enum list | Yes | `skill`, `copilot_agent`, `opencode_agent`, `source_project` |
| `repo_snapshots` | directory | Yes | Local read-only checkouts, one folder per submission id |
| `rubric_version` | string | Yes | Versioned scoring rubric; frozen and hashed |
| `report_target` | path | Yes | Where the static HTML reports are written |
| `llm_endpoint` | internal config | No | **Not needed** when running inside a host agent. Only for the optional headless transport. |
| `artifact_type_override` | map | No | Manual override if the classifier is uncertain |

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

Reference the official specs as validation sources, but prefer locally stored copies or extracted excerpts when the environment is air-gapped:

- Anthropic / Claude — Skill schema and agent conventions, for artifact validation and quality checks
- GitHub Copilot — custom agent and instruction-file schema, for classification and structure validation
- OpenCode — agent definition structure and tool/metadata rules, for artifact-type detection

Treat these as specification inputs, not runtime network dependencies. If the environment cannot reach them, use a local copy or an internal documentation mirror.

## Static Security Scan Requirements

Every submission passes a deterministic static scan before any LLM evaluation. The scanner must detect hard-coded credentials (API keys, OAuth tokens, cloud keys, JWTs, private keys), suspicious URLs and outbound calls to non-approved domains, insecure network behaviour in config/scripts/CI, prompt-injection patterns in README or skill metadata, PII and internal-host leakage, and dangerous shell or package-install commands.

Layer external tooling on top for recall: `gitleaks` for credentials, `trufflehog` for secret detection, `semgrep` for risky patterns, plus custom checks for internal-domain restrictions and `.env` / CI secret files.

The scan must be non-invasive: it reads source files and metadata but never executes submission code and never connects to arbitrary external websites.

### Context matters for severity

The same string is a genuine risk in executable code but routine elsewhere — a test fixture is expected to contain fake credentials, a security document describes the patterns it detects, and a JSON Schema `$schema` value is an identifier rather than an egress attempt. Treating all of these as hard failures makes the gate unusable on any repository that documents security. Severity is therefore resolved by file context; see `references/deterministic-scoring.md` and the module docstring in `code/static_scanner.py`.

### Required gate behavior

The static gate must fail closed:

- a credential in executable code or config → `hard-failed`
- an unapproved external destination in executable code or config → `hard-failed`
- prompt injection in README / skill / agent metadata → escalate to human review
- the same patterns in tests, documentation, or templates → review, never silently dropped

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

## Judge Rules

The judging model is the host agent's own model, so it cannot be pinned the way an endpoint can. The constraint is applied through the contract instead:

- the prompt fixes the rubric, the bands, and the output shape
- strict JSON only — no prose, no markdown fences
- evidence required for any positive score
- no tools, no file writes, no ranking logic
- one result per submission, covering only the dimensions the request lists
- the program owns all arithmetic, ranking, and confidence — never the model

The model is asked not to decide rankings or compute totals. Even if it tries, `merge` recomputes every total from the bands, so a self-assigned score has no effect.

### Evidence rule

For any score greater than zero in a dimension, cite at least one evidence item:

- `file_path`
- `line_or_range`
- `note`

`merge` rejects any entry where a positive score carries no evidence, so an unevidenced submission fails loudly rather than being scored. Where evidence is genuinely absent, the band must be the lowest valid one.

### Confidence

Confidence reflects how much of the result is model-derived versus fact-derived:

- `high`: all dimensions evidenced, no review-severity findings
- `medium`: pre-judge state, or judge confidence reported as `medium`
- `low`: judge reported `low`, or more than two review-severity findings

Entities with low confidence and a high rank must be routed to a human review queue.

## Concurrency and Throughput Design

### Concurrency limit should be driven by the host, not by raw CPU

Do not scale by launching 150 independent agent processes. The static scan and ingestion can use a bounded worker pool, but the judging stage is bounded by the host agent's context, not by CPU or by a remote endpoint's rate limits.

### Required queue behaviors

- idempotent keys for resumed runs
- state persistence across crash and restart
- exponential backoff and jittered retry
- dead-letter queue for permanent failures
- provenance metadata appended to each result: repo identifier, commit SHA, `scanned_at`, `model_id`, `model_version`, `prompt_version`, `rubric_version`, `orchestrator_version`, `tool_versions`

### Skill + program, or main agent + sub-agents?

Both, tiered by cohort size. A Skill packages *what to do*; sub-agents distribute *where the work runs*. They are not alternatives.

Up to roughly 30 submissions the Skill + program design is right and sub-agents only add overhead. Beyond that, context capacity forces delegation: one judge bundle is about 25.7k tokens, so an agent runs out of room after a handful of submissions.

Two measured cost facts shape the design:

- Splitting scoring **by dimension** triples input cost, because each scorer reads the same bundle to judge its own dimension. Splitting **by submission** does not.
- Sub-agents can run in parallel (both VS Code and OpenCode support it), so batching also buys wall-clock time. Cost per submission is unchanged either way.

Three agent definitions ship under `.agents/agents/`: `codecup-eval-orchestrator` (dispatches, never scores), `codecup-eval-scorer` (D3/D6/D7, at most three submissions), `codecup-eval-verifier` (adversarial evidence check, never scores). See `references/main-subagent-architecture.md`.

## Data and Output Contract

Each result must carry submission metadata, classification, gate outcome, dimension scores, confidence, rank, and provenance. The full field-level contract lives in `templates/result.schema.json`; the runtime emits it as `execution-state.json`, which `report_generator.py` renders without any LLM involvement.

Only submissions that clear the static gate and complete a judge pass are ranked. Hard-failed and failed submissions are excluded from ranking entirely and must never be presented as scored entries.

## Runtime Scaffold (`code/`)

A dependency-free Python implementation ships with this skill. It performs no network calls and never executes submitted code.

| File | Purpose |
|---|---|
| `code/orchestrator.py` | CLI entry point: `prepare`, `merge`, `scan-only` |
| `code/judge_io.py` | The two-phase workflow: emit judge requests, merge agent scores |
| `code/judge_adapter.py` | Prompt assembly, evidence bundling, JSON contract validation |
| `code/manifest_loader.py` | Load and validate the frozen submission manifest |
| `code/artifact_classifier.py` | Deterministic artifact-type classification |
| `code/allowlist.py` | Default-deny network allowlist decisions |
| `code/static_scanner.py` | Secret, injection, dangerous-script, external-host scanning |
| `code/deterministic_scorer.py` | Scores D1/D2/D4/D5 from repository facts, no LLM |
| `code/aggregator.py` | Weighted scoring, partial totals, confidence, ranking |
| `code/metrics.py` | Per-stage timing and token accounting |
| `code/efficiency.py` | Read-only cost/time/efficiency report for a finished run |
| `code/report_generator.py` | Deterministic, escaped, CDN-free HTML reports |
| `code/judge_transport.py` | Optional headless transport (not the primary path) |
| `code/tests/` | Six standard-library test suites |

Run the suites with:

```bash
cd code
for t in test_gates test_pipeline test_deterministic_scorer test_metrics test_judge_io test_efficiency; do
  PYTHONPATH=. python3 tests/$t.py
done
```

## How It Runs (Two-Phase, Host-Agent Native)

This skill runs **inside** a host agent — GitHub Copilot, OpenCode, or similar. The model that judges a submission is the host agent's own model. **There is no separate LLM API to configure, and the pipeline never calls an endpoint on the primary path.**

```text
Phase 1  prepare   program scans repos, writes judge-requests/<id>.md
   ↓
         host agent reads each request and produces scores as JSON
   ↓
Phase 2  merge     program validates, combines, totals, ranks, renders HTML
```

```bash
# Phase 1 — program
PYTHONPATH=. python3 orchestrator.py prepare \
  --manifest ../templates/submission-manifest-template.yaml \
  --allowlist ../templates/allowlist.json \
  --repo-root /path/to/repo-snapshots --out ./out \
  --rubric ../templates/score-rubric.yaml

# Phase 2 — after the host agent writes out/judge-scores.json
PYTHONPATH=. python3 orchestrator.py merge --out ./out --rubric ../templates/score-rubric.yaml
```

`prepare` writes one request file per submission that cleared the static gate, containing the prompt, a bounded evidence bundle, and the deterministic scores already computed. `merge` validates the agent's scores against the contract, combines them with the deterministic dimensions, recomputes every total from the bands, re-ranks, and renders the reports. **Merge is idempotent** — re-running replaces the judge contribution rather than appending it.

Use `scan-only` to exercise the deterministic layer with no judge pass; records then stay `awaiting-judge` and totals render as pending.

Full command reference, the `judge-scores.json` shape, and failure behaviour are in `references/two-phase-workflow.md`.

### Evidence bundle

`judge_adapter.build_evidence_bundle` selects only what a judge needs: entry files first (`SKILL.md`, `README`, `AGENTS.md`, `opencode.json`, manifests), then agent definitions, then remaining source. Vendored directories (`.git`, `node_modules`, `dist`, …) are skipped, and the bundle is capped at 40 files / 120 KB total / 20 KB per file. Content is wrapped in explicit untrusted markers declaring it data, not instructions.

### Optional headless transport

`code/judge_transport.py` and `judge_adapter.run_judge` exist **only** for an optional headless/batch deployment where an endpoint is configured. They are not the primary path and are unnecessary when the skill runs inside a host agent.

### Where results are written

Everything lands under `--out` (default `./out`): `execution-state.json` is the machine-readable source of truth, and `reports/` holds `index.html` (dashboard) plus one `<submission_id>.html` per submission, linked from the dashboard. The HTML is rendered deterministically from the JSON, so the two cannot disagree. Point `--out` at a folder under `code-cup-eval-artifacts/` to keep a run in the repository.

Reports are self-contained — no CDN, no external fonts, no network needed to view them — and every interpolated value is HTML-escaped, so a hostile repository or team name cannot inject markup.

### Cost and timing metrics

Every run records what each stage cost. `execution-state.json` carries a batch `cost` block plus a `metrics` block per submission, and each report page renders a "Cost and timing" table.

Token figures are never conflated: `measured` was reported by the model, `estimated` is a character heuristic for stages that call no model, and `none` means no figure was produced. Batch totals are summed **per stage**, so genuinely measured tokens are never hidden behind a submission's weakest label.

The host-agent judging phase is timed by deriving it from the `prepare` and `merge` timestamps and is labelled as derived. Its token usage is estimated from the judge request and response sizes on disk when the agent does not report usage, so every report carries a cost figure for the judging pass — clearly marked `estimated` rather than presented as provider billing.

Counts and durations are formatted for reading: thousands grouped (`36,866`), sub-second durations in milliseconds (`31.0ms`), longer ones in seconds or minutes.

### Retrospective efficiency report

`prepare` and `merge` record cost as the run happens. To report it afterwards —
or to compare two runs — use the read-only `efficiency` command:

```bash
PYTHONPATH=. python3 orchestrator.py efficiency --out ./out --mode skill --write

# compare a Skill-mode run with an Agent-mode run over the same cohort
PYTHONPATH=. python3 orchestrator.py efficiency --out <agent-run> --compare <skill-run>
```

It reports wall-clock split by program vs agent, tokens split by stage, the
deterministic share of the work, the dispatch shape, quality/outcome metrics,
and a list of flags for anything that would make the numbers misleading. It
never writes to the run except for `efficiency.md` under `--write`.

Three measurement traps are corrected rather than papered over: the agent
wall-clock is one shared span (not per-submission, and not model compute time),
and unmeasured tokens stay labelled as a heuristic rather than being presented
as cost. Dispatch shape is the one input the program cannot derive — record it
in `<out>/run-meta.json`. See `references/efficiency-reporting.md`.

### Run directory naming

`--out` has no default directory beyond `./out`, so **name it explicitly** and keep every run in one place. The convention is:

```text
code-cup-eval-artifacts/<cohort>-eval-<mode>/
```

| Part | Meaning | Examples |
|---|---|---|
| `<cohort>` | what was scored | `codecup`, `caveman`, `pptx-skill` |
| `<mode>` | how it was scored | `sample`, `agent`, `skill` |

Examples: `codecup-eval-sample`, `caveman-eval-sample`, `codecup-eval-agent`.

This matters because the two modes are meant to be compared. `efficiency --compare` takes two run directories, and a mode-suffixed name makes the pairing obvious. Name the mode from the **scoring mechanism**, not the model:

- `sample` — a small committed run kept to show the output shape
- `agent` — the orchestrator dispatched scorer sub-agents
- `skill` — the Skill ran inside a single host-agent context, no sub-agents

**Never reuse a directory for a second run of a different cohort.** `prepare` overwrites `execution-state.json`, `judge-requests/`, and the reports in place, and `merge` replaces the judge contribution rather than appending it. Two cohorts sharing one `--out` silently merge into one leaderboard.

Sample runs committed under `code-cup-eval-artifacts/` at the repository root show the shape of a completed evaluation.

#### What lands in the run directory

```text
code-cup-eval-artifacts/<cohort>-eval-<mode>/
├── execution-state.json      machine-readable source of truth
├── judge-scores.json         the host agent's scores (input to merge)
├── run-meta.json             optional; dispatch shape for the efficiency report
├── efficiency.md             optional; written by `efficiency --write`
├── .run-started-at           timestamp used to derive the agent phase
├── judge-requests/
│   └── <submission_id>.md    one prompt + evidence bundle per submission
└── reports/
    ├── index.html            dashboard, links to each page
    └── <submission_id>.html  one page per submission
```

Report file names are derived from `submission_id` by `report_generator.report_filename`, which keeps alphanumerics, `-`, and `_` and replaces everything else with `_`. The dashboard and the per-submission writer share that function, so links cannot drift from file names.

### What the orchestrator computes without an LLM

Four of the seven dimensions are scored from repository facts before the judge is ever asked: D1 security (from gate findings), D2 structure (from artifact markers), D4 documentation, and D5 testing. Only D3, D6, and D7 — the genuine judgement calls — go to the host agent.

Deterministic scores carry evidence and a rationale, so the merged result satisfies the same evidence contract the judge must meet. Pre-judge confidence is capped at `medium`; any review-severity finding (prompt injection, PII) forces `human_review_required` regardless of the label.

Per-dimension thresholds and the known weaknesses of these heuristics are in `references/deterministic-scoring.md`.

### Dependency note

YAML manifests require `PyYAML`. Where `PyYAML` is unavailable, convert the manifest to JSON — the loader falls back to `json` with no third-party dependency. Python 3.9+ is sufficient.

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

Do not allow the LLM to browse UAT or internal systems directly. Use orchestrator-driven checks instead: HTTP status, TLS validity, latency, a headless screenshot, console error detection, and dead-link verification. The screenshot can then be handed to a multimodal reviewer as an artefact.

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
