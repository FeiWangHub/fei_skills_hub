# Code Cup Evaluation — Deterministic Scoring

Reference for `code/deterministic_scorer.py`.

## Why this exists

The design stance is deterministic-first: most of the rubric can be judged from repository facts without any LLM call. This is cheaper, reproducible, and auditable. The judge is reserved for what genuinely needs judgement.

## Dimension split

| Dimension | Scored by | Signal |
|---|---|---|
| D1 Security and compliance | deterministic | static gate findings |
| D2 Structure and conformance | deterministic | artifact markers for the declared type |
| D3 Code and content quality | judge | requires judgement |
| D4 Documentation | deterministic | documentation files and their depth |
| D5 Testing and reliability | deterministic | test file presence and count |
| D6 Business value and impact | judge | requires judgement |
| D7 Innovation and differentiation | judge | requires judgement |

Four of seven dimensions are deterministic. The judge-only dimensions stay at `0` with the record in `awaiting-judge` until a judge pass runs — the orchestrator never invents a value for them.

## Band mapping

Scores use the same anchored bands as the judge, so merged results are comparable:

| Band | Meaning |
|---|---|
| 1 | weak |
| 3 | acceptable |
| 5 | strong |

## Per-dimension rules

### D1 Security and compliance
- any `hard_fail` finding → 1
- any `review` finding → 3
- clean → 5

A hard failure is already fatal upstream, so in practice D1 is only scored for submissions that passed the gate.

### D2 Structure and conformance
- declared artifact markers present → 5
- `source_project` → 3 (no fixed shape is mandated, so it is not penalised)
- declared type not reflected in the repository → 1

### D4 Documentation
- README present and total documentation ≥ 2000 bytes → 5
- README present, or total ≥ 500 bytes → 3
- no documentation → 1

### D5 Testing and reliability
- ≥ 5 test files → 5
- 1–4 test files → 3
- none → 1

Test detection matches path hints such as `test/`, `tests/`, `spec/`, `__tests__/`, `test_`, `_test.`, `.test.`, `.spec.`.

## Evidence requirement

Every deterministic score emits evidence (`file_path`, `line_or_range`, `note`) and a rationale string. This matters because the merged result must satisfy the same evidence contract the judge is held to — a deterministic score with no traceable basis would break the audit trail.

## Ignored paths

`.git`, `node_modules`, `dist`, `build`, `.venv`, `venv`, `__pycache__`, `.next`, and `target` are skipped, so vendored tests or docs cannot inflate a score.

## Known weakness

D4 and D5 use file counts and byte sizes as proxies. A submission could in principle inflate them with empty or filler files. Byte-size thresholds make this somewhat harder but do not eliminate it. If this becomes a concern, add a content-quality check (for example, requiring test files to contain assertions) before trusting the D5 band.
