# Code Cup Evaluation — Two-Phase Host-Agent Workflow

Reference for `code/judge_io.py` and the `prepare` / `merge` commands.

## Why two phases

The skill runs **inside** a host agent — GitHub Copilot, OpenCode, or similar.
The model that judges a submission is the host agent's own model, so there is no
endpoint to configure and no API key to hold.

The program cannot call the host's model, and the host's model cannot run the
deterministic pipeline. Splitting the run into two phases lets each side do what
it is good at:

```text
Phase 1  prepare   program scans repos, writes judge-requests/<id>.md
   ↓
         host agent reads each request and produces scores as JSON
   ↓
Phase 2  merge     program validates, combines, totals, ranks, renders
```

## Phase 1 — prepare

```bash
PYTHONPATH=. python3 orchestrator.py prepare \
  --manifest ../templates/submission-manifest-template.yaml \
  --allowlist ../templates/allowlist.json \
  --repo-root /path/to/repo-snapshots \
  --out ./out \
  --rubric ../templates/score-rubric.yaml
```

Writes:

| Path | Contents |
|---|---|
| `out/judge-requests/<submission_id>.md` | judge prompt + evidence bundle + deterministic scores |
| `out/execution-state.json` | full pipeline state, all records in `awaiting-judge` |
| `out/.run-started-at` | timestamp used to measure the agent phase later |

Only submissions that cleared the static gate get a request file. Hard-failed
submissions are already terminal and need no judging.

## Phase 2 — the agent scores

The host agent reads each request and writes `out/judge-scores.json`. Either
shape is accepted:

```json
{
  "TEAM_001": {
    "scores": {
      "d1_security_and_compliance": 3, "d2_structure_and_conformance": 5,
      "d3_code_quality": 5, "d4_documentation": 5,
      "d5_testing_and_reliability": 3, "d6_business_value": 5, "d7_innovation": 5
    },
    "evidence": [
      {"file_path": "code/scanner.py", "line_or_range": "1-60", "note": "..."}
    ],
    "confidence": "high",
    "tokens": {"prompt_tokens": 12000, "completion_tokens": 800, "total_tokens": 12800}
  }
}
```

```json
[
  {"submission_id": "TEAM_001", "scores": { }, "evidence": [ ], "confidence": "high"}
]
```

`tokens` is optional. Supply it only if the host exposes usage; otherwise the
judge stage records the figure as unavailable rather than guessing.

All seven score keys are required. Bands must be `1`, `3`, or `5` (or `0`), and
any positive score must carry at least one evidence item.

## Phase 3 — merge

```bash
PYTHONPATH=. python3 orchestrator.py merge --out ./out --rubric ../templates/score-rubric.yaml
```

Merge:

1. validates every entry against the contract, rejecting the whole file on a violation
2. overwrites the judge-owned dimensions with the agent's bands
3. recomputes every weighted total from those bands, using per-artifact weights
4. re-ranks, routing low-confidence top-slice results to human review
5. attributes the agent phase's time and tokens
6. renders `reports/index.html` and one page per submission

**Merge is idempotent.** Re-running it replaces the judge stage and the judge's
evidence rather than appending them, so totals do not drift. This is covered by
`test_merge_is_idempotent`.

## Measuring the agent phase

The program can time its own phases exactly. It cannot time the agent, so that
stage is **derived** from the `.run-started-at` stamp and the moment `merge`
runs, and is labelled as derived in the output rather than presented as a
measurement.

Token usage for the agent phase:

| Situation | Result |
|---|---|
| the agent supplied a `tokens` object | recorded as `measured` |
| the agent did not report usage | estimated from the judge request and response sizes on disk, recorded as `estimated` |
| neither is possible | `none` |

The estimate uses the same characters-per-token heuristic as the static scan,
so it is comparable with the other stages but is **not** provider billing. Both
the request file and the agent's response are real artefacts with measurable
size, so the figure rests on observed data rather than a guess. Because it is
recomputed from the files, re-running `merge` produces the same number.

## Failure behaviour

| Condition | Result |
|---|---|
| `judge-scores.json` missing | `FileNotFoundError`, no partial merge |
| an entry has a positive score with no evidence | whole file rejected |
| an entry has a score outside the bands | whole file rejected |
| an entry is missing a dimension | whole file rejected |
| a submission has no entry | left in `awaiting-judge`, reported in `state` |
