# Code Cup Evaluation Runtime

Reference implementation of the Code Cup evaluation pipeline: ingest, artifact
classification, the static security gate, judge output validation, weighted
aggregation, and static report rendering.

## Security policy

- no public network access
- no execution of submitted code in the default path
- only internal/private endpoints are allowed
- any destination outside the approved allowlist is refused before a request is sent

## Files

| File | Purpose |
|---|---|
| `manifest_loader.py` | Parse and validate the frozen submission manifest |
| `artifact_classifier.py` | Deterministic artifact-type classification |
| `allowlist.py` | Default-deny network allowlist decisions |
| `static_scanner.py` | Secret, injection, dangerous-script, and external-host scanning |
| `deterministic_scorer.py` | Scores D1/D2/D4/D5 from repository facts, no LLM |
| `judge_adapter.py` | Judge prompt assembly and strict JSON contract validation |
| `judge_transport.py` | The only module permitted to open a connection |
| `aggregator.py` | Weighted scoring, median reconciliation, confidence, ranking |
| `report_generator.py` | Deterministic, escaped, CDN-free HTML reports |
| `orchestrator.py` | Pipeline entry point |
| `metrics.py` | Per-stage timing and token accounting |
| `efficiency.py` | Read-only cost/time/efficiency report for a finished run |
| `tests/test_gates.py` | Tests for allowlist, classifier, scanner, judge contract |
| `tests/test_pipeline.py` | Tests for aggregation, egress enforcement, reports |
| `tests/test_deterministic_scorer.py` | Tests for the deterministic dimensions |
| `tests/test_metrics.py` | Tests for measured/estimated token labelling |
| `tests/test_judge_io.py` | Tests for the prepare/merge contract and idempotency |
| `tests/test_efficiency.py` | Tests for the efficiency report and its guard rails |

## Quick start

```bash
PYTHONPATH=. python3 tests/test_gates.py
PYTHONPATH=. python3 tests/test_pipeline.py
for t in test_gates test_pipeline test_deterministic_scorer test_metrics test_judge_io test_efficiency; do
  PYTHONPATH=. python3 tests/$t.py
done

# Phase 1 — scan and emit judge requests
PYTHONPATH=. python3 orchestrator.py prepare \
  --manifest ../templates/submission-manifest-template.yaml \
  --allowlist ../templates/allowlist.json \
  --repo-root /path/to/repo-snapshots \
  --out ./out \
  --rubric ../templates/score-rubric.yaml

# Phase 2 — merge the host agent's scores and render reports
PYTHONPATH=. python3 orchestrator.py merge --out ./out --rubric ../templates/score-rubric.yaml

# Report time and token cost for the finished run
PYTHONPATH=. python3 orchestrator.py efficiency --out ./out --mode skill --write
```

Requires Python 3.9+. `PyYAML` is needed for YAML manifests; a JSON manifest
needs no third-party dependency.

Four of the seven dimensions (D1, D2, D4, D5) are scored deterministically with
no LLM. D3, D6, and D7 are left to the judge and stay at `0` with the record in
`awaiting-judge` until a judge pass runs. The judge stage is not invoked by the
orchestrator — see `../SKILL.md` for how to wire in `JudgeTransport`.

