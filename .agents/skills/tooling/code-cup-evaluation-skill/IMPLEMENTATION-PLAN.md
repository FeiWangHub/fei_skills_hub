# Code Cup Evaluation Skill — Complete Implementation Plan

## 1. Objective

Build an internal, security-first evaluation pipeline for a large-scale Code Cup or internal hackathon. The pipeline must evaluate mixed artifact submissions including Skills, Copilot agents, OpenCode agents, and source-code projects, while enforcing deterministic gates, auditability, and a strict internal-only network policy.

## 2. Scope

In scope:

- submission manifest intake
- artifact classification
- static security scanning
- schema validation
- rubric scoring
- LLM judge pass with evidence constraints
- aggregate scoring and confidence checks
- static HTML/generate report output
- audit provenance and human review flow

Out of scope:

- arbitrary autonomous agent planning
- unrestricted public network access
- execution of submitted code without sandboxing
- free-form LLM-generated HTML or ranking logic

## 3. Security Boundaries (Hard Requirements)

### 3.1 Network policy

Default deny all outbound traffic except:

- internal/private LLM endpoint
- internal Git host
- internal report host
- approved `.example` internal domains

Any destination outside the allowlist must be blocked before the request is sent. No arbitrary public domain access is permitted.

### 3.2 Static scan first

The first gate is purely static and must run before LLM evaluation. It must inspect repository contents only and never execute code.

Required checks:

- secret / token detection
- credential pattern detection
- PII leakage detection
- prompt-injection detection
- suspicious outbound URL detection
- CI or shell script exfiltration pattern detection

### 3.3 LLM constraints

The LLM judge has no tools, no write access, and no ranking authority. It only scores the provided evidence bundle and returns strict JSON.

## 4. Execution Pipeline

### Phase 0 — Governance and freeze

Deliverables:

- approved scoring rubric version
- approved prompt version
- approved model version
- submission manifest with frozen commit SHAs
- allowlist config file

Outputs:

- `rubric_version`
- `prompt_version`
- `model_version`
- `allowlist.json`

### Phase 1 — Ingest and manifest intake

Tasks:

- read submission manifest
- verify repo URL and contact metadata
- pin commit SHA for each submission
- create state record per team

State transitions:

- `pending`
- `running`
- `done`
- `failed`
- `hard-failed`

### Phase 2 — Artifact classification

Classify each repo into one of:

- `skill`
- `copilot_agent`
- `opencode_agent`
- `source_project`

Deterministic rules:

- `SKILL.md` / `skill.md` => skill
- `.github/agents/*.agent.md` => copilot agent
- `.opencode/...` or `opencode.json` => opencode agent
- otherwise => source project

Ambiguous cases go to manual override before batch scoring starts.

### Phase 3 — Static security gate

Required implementation:

- repository scan on file contents only
- secret scan using gitleaks / trufflehog equivalent
- risky pattern detection using semgrep / custom rules
- external domain detection with allowlist comparison
- prompt injection detection across README / skill metadata / agent metadata

Hard fail if:

- credential or token found
- external non-approved domain found
- malicious prompt-injection phrase found
- private key material found

### Phase 4 — Artifact conformance and metadata validation

Validate:

- expected file presence
- structure compliance for Skill / agent patterns
- required metadata fields
- readme and project summary presence
- basic test or verification signal presence

### Phase 5 — Judge preparation and gold set calibration

Tasks:

- create 10–15 benchmark repos spanning quality bands
- establish gold set with human scoring
- calibrate rubric anchors
- freeze prompt and evidence bundle policy

Calibration outputs:

- human score cross-check
- score band alignment
- prompt version hash
- judge confidence baseline

### Phase 6 — LLM judge pass

Only after static gate passes.

Judge rules:

- zero tools
- zero write access
- zero ranking logic
- strict JSON output
- evidence mandatory for any positive score
- exactly one judge pass per dimension or two-pass ensemble with median selection

Evidence contract:

- `file_path`
- `line_or_range`
- `note`

### Phase 7 — Aggregate scoring

The orchestrator computes:

- deterministic static score
- LLM qualitative score
- confidence level
- final weighted score
- manual review triggers

Rules:

- weights stored in config, not in model logic
- total score only computed by orchestrator
- low-confidence, high-rank cases go to human review

### Phase 8 — Static reporting

Generate:

- per-project HTML report
- summary leaderboard page
- human review queue

Rules:

- no LLM writes HTML
- render from validated JSON only
- static output only
- internal hosting only

## 5. Evaluation Rubric

### 7-dimensional rubric

- D1 Security and compliance
- D2 Standards and structure conformity
- D3 Code and content quality
- D4 Documentation and discoverability
- D5 Testing and reliability
- D6 Business value and impact
- D7 Innovation and differentiation

Use anchored bands: 1, 3, 5.

### Weighting by artifact type

- skill
- copilot agent
- opencode agent
- source project

Weights must be versioned and applied by the orchestrator.

## 6. Outputs to Produce

Per submission:

- static gate result
- evidence bundle
- judge JSON output
- final weighted score
- confidence level
- review flag

Repository-level:

- aggregate leaderboard JSON
- per-project report page
- summary dashboard
- human review listing

## 7. Deliverable Set

### 7.1 Shipped in this skill

| File | Status |
|---|---|
| `skill.md` | shipped — architecture, security model, output contract |
| `IMPLEMENTATION-PLAN.md` | shipped — this plan |
| `templates/submission-manifest-template.yaml` | shipped |
| `templates/judge-prompt-template.md` | shipped |
| `templates/static-scan-checklist.md` | shipped |
| `templates/score-rubric.yaml` | shipped — 7 dimensions, per-artifact weights |
| `templates/result.schema.json` | shipped — per-submission result contract |
| `templates/allowlist.json` | shipped — default-deny domain policy |
| `code/manifest_loader.py` | shipped — load + validate manifest |
| `code/artifact_classifier.py` | shipped — deterministic classification |
| `code/allowlist.py` | shipped — allowlist decisions |
| `code/static_scanner.py` | shipped — secret / injection / host scanning |
| `code/deterministic_scorer.py` | shipped — D1/D2/D4/D5 scored from repository facts, no LLM |
| `code/judge_adapter.py` | shipped — judge prompt + JSON contract validation |
| `code/judge_transport.py` | shipped — allowlist-enforced HTTP transport, the only egress point |
| `code/aggregator.py` | shipped — weighted scoring + median reconciliation + ranking |
| `code/report_generator.py` | shipped — escaped, CDN-free static HTML rendering |
| `code/orchestrator.py` | shipped — pipeline entry point |
| `code/tests/test_gates.py` | shipped — stdlib test suite |
| `code/tests/test_pipeline.py` | shipped — stdlib test suite |
| `code/tests/test_deterministic_scorer.py` | shipped — stdlib test suite |
| `code/README.md` | shipped — usage notes |

### 7.2 Not yet implemented

| File | Status |
|---|---|
| `templates/leaderboard.schema.json` | pending — dashboard aggregate contract |
| `templates/report-template.html` | pending — external layout override (reports are currently styled in `report_generator.py`) |
| Judge invocation inside `orchestrator.py` | pending — requires a live internal endpoint and credentials; wired by the caller today |

### 7.3 Verified behavior

The shipped `code/` layer was executed locally against purpose-built fixtures. Observed results:

- a repo containing an AWS key and a call to `api.someexternalvendor.com` was marked `hard-failed` with 2 hard-fail findings and did not reach the judge stage
- a clean repo referencing only `llm.internal.example` passed the gate with zero findings and was queued as `awaiting-judge`
- a repo containing prompt-injection text passed the hard gate but was downgraded and routed to review
- deterministic scoring separates quality: a complete clean skill scored 5/5/5/5 on D1/D2/D4/D5, while a bare source project with no docs and no tests scored 5/3/1/1 on the same dimensions
- every deterministic score carries evidence and a rationale (9 evidence items vs 4 for the two fixtures)
- allowlist decisions correctly permitted `.example` hosts and denied `github.com`, `pypi.org`, and `api.evil.com`
- `JudgeTransport` raised `EgressBlockedError` for both a non-approved host and an explicit blocklist entry, and permitted an approved internal endpoint
- the judge contract rejected responses with a positive score and no evidence, an out-of-band score of 100, markdown-fenced JSON, and non-JSON text
- a two-pass judge disagreement of 4 bands produced a median score with `low` confidence and a mandatory review flag
- a single judge pass was capped at `medium` confidence, since one pass cannot demonstrate agreement
- report rendering escaped a hostile `<script>` team name and emitted no `http://` or `https://` references
- an unpinned submission (missing `commit_sha`) was rejected at manifest validation with a named error
- a YAML manifest without `PyYAML` failed with an explicit remediation message rather than silently proceeding

### 7.4 Defects found and fixed during verification

**Defect 1 — blocked submissions were ranked as review candidates.** A submission `hard-failed` by the static gate carried `total: 0` and `confidence: low`, and the top-slice review rule then flagged it as "low confidence within the top-ranked slice", presenting a blocked submission as a ranked entry awaiting manual review. Fix: ranking now partitions records into scored and non-scored; hard-failed and failed submissions receive no rank and are never subject to the top-slice rule. Regression test: `test_ranking_excludes_non_scored_submissions`.

**Defect 2 — the deterministic-first design was not implemented.** The orchestrator set all seven dimensions to `0` and deferred everything to the judge, contradicting the core design stance that roughly 70% of the score needs no LLM. Fix: added `deterministic_scorer.py`, which scores D1/D2/D4/D5 from repository facts, leaving only D3/D6/D7 to the judge.

**Defect 3 — dead and duplicated code in the orchestrator.** `aggregate()`, `DEFAULT_WEIGHTS`, and the `asdict` import were unused, and `compute_confidence()` duplicated `aggregator.derive_confidence()` with different semantics. Fix: removed the dead code and unified on the aggregator's confidence function.

**Defect 4 — pre-judge confidence semantics.** Calling `derive_confidence(0, 0, n)` before any judge pass always returned `medium`, and review-severity findings no longer forced escalation. Fix: pre-judge confidence is now explicitly capped at `medium`, and any review-severity finding sets `human_review_required` independently of the confidence label.

### 7.5 Known limitations

- the judge stage is not invoked by `orchestrator.py`; it requires a live internal endpoint and credentials. D3/D6/D7 stay at `0` with the record in `awaiting-judge` rather than being assigned a fabricated score.
- the static scanner is regex-based and self-contained by design; `gitleaks` / `semgrep` should be layered on top as a second pass for higher recall
- `postinstall` and CI detection is pattern-based and will not catch obfuscated scripts
- reports are rendered by `report_generator.py`; there is no external HTML template override yet
- no deduplication or cross-team similarity layer is implemented
- concurrency and the rate-limited worker pool described in §4 are not implemented; the pipeline currently runs sequentially
- deterministic heuristics for D4/D5 use file counts and byte sizes as proxies, which a submission could in principle game by adding empty files

## 8. Completion Criteria

The project is complete when all of the following are true:

- all submissions can be processed through the static gate
- all non-compliant submissions are blocked before LLM evaluation
- only approved internal and `.example` destinations are reachable
- LLM judge outputs are JSON-only and evidence-backed
- aggregate results match the schema
- report pages render cleanly without LLM generation
- human review queue captures low-confidence or borderline outcomes

## 9. Recommended Rollout Sequence

1. implement static gating only
2. validate with a small benchmark set
3. freeze rubric + prompt + model version
4. run partial batch evaluation
5. review low-confidence outputs
6. generate report pages
7. move to full batch run

## 10. Final Principle

This system must favor deterministic behavior, strong security gates, and auditable evidence over free-form autonomous handling. The orchestrator owns the flow; the LLM judge owns only the qualitative scoring of the evidence bundle.
