# Code Cup Evaluation — Cost and Timing Metrics

Reference for `code/metrics.py`.

## Why this exists

To compare two scoring configurations on cost, each run must record what every
stage consumed. Without that, "deterministic-first is cheaper" is an assertion
rather than a measurement.

## Measured vs estimated

The two are never conflated. Every token figure carries a `source` field:

| Source | Meaning |
|---|---|
| `measured` | wall-clock time, and token counts reported by the endpoint's `usage` field |
| `estimated` | a character-ratio heuristic, for stages that call no model |
| `none` | the stage ran but produced no token figure |

An LLM total of `0` with `source: "measured"` is a **real zero**: the stage ran
and made no model call. A non-zero total with `source: "estimated"` is a volume
proxy, not billing data.

`TokenUsage.merge` keeps the **weakest** evidence source. Mixing measured and
estimated usage yields `estimated`, so a label always reflects the least reliable
component rather than flattering the total.

## What each stage records

| Stage | Time | Tokens |
|---|---|---|
| `classify` | measured | none — it reads filenames only |
| `static_scan` | measured | estimated, from bytes read |
| `deterministic_scoring` | measured | none — it inspects metadata and counts |
| `judge` | measured, by the caller | measured, from the endpoint's `usage` |

The `judge` stage is deliberately **absent** from `metrics.stages` when it does
not run. It is not recorded as a zero-duration stage, because it did not happen.

## Why static-scan volume is worth recording

The estimated figure for `static_scan` is the total bytes the scanner read —
which is the same repository volume a naive "send everything to the model"
approach would have to pay for. Comparing that estimate against the measured
judge usage shows what the deterministic layer saved.

## Wiring in real judge usage

`JudgeTransport` exposes two things for this:

- `last_usage` — the endpoint-reported usage from the most recent successful call
- `call_count` — how many successful calls have been made

A caller that runs the judge converts `last_usage` with
`TokenUsage.from_provider_usage(transport.last_usage, model)` and appends a
`judge` stage with the real elapsed time. If the endpoint reports no `usage`,
`last_usage` is an empty dict and the figure must be labelled `none` rather than
guessed.

## Batch output

`out/execution-state.json` carries:

```json
{
  "cost": {
    "submissions": 3,
    "total_elapsed_s": 0.074,
    "mean_elapsed_ms": 24.63,
    "total_tokens": 82903,
    "measured_tokens": 0,
    "estimated_tokens": 82903,
    "note": "measured_tokens come from the endpoint's usage field; ..."
  }
}
```

Each report page renders the same per-stage breakdown as a table.
