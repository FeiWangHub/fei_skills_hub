# Code Cup Evaluation — Efficiency Reporting

Reference for `code/efficiency.py` and the `orchestrator.py efficiency` command.

## Why this exists

`metrics.py` records what each stage consumed while a run happens. This module
answers the question afterwards: **how long did the run take, how many tokens did
it cost, and how much of that cost was the model rather than the program?**

It exists so that "deterministic-first is cheaper" and "sub-agents are
cost-neutral when split by submission" can be checked against a finished run
instead of argued from prompt volume.

## It is read-only

`efficiency.py` reads a finished `--out` directory and never writes to it. The
only exception is `--write`, which drops `efficiency.md` alongside the reports.
It is safe to run against an archived run at any time, and safe to run twice.

## Command

```bash
# per-run report
PYTHONPATH=. python3 orchestrator.py efficiency --out <out> --mode skill --write

# two runs, same cohort
PYTHONPATH=. python3 orchestrator.py efficiency --out <agent-run> --compare <skill-run>

# machine-readable
PYTHONPATH=. python3 orchestrator.py efficiency --out <out> --json
```

## What it reports

| Block | Contents |
|---|---|
| `run` | out dir, mode label, human label, generation timestamp |
| `cohort` | submissions, done / awaiting-judge / hard-failed / failed, human review, ranked |
| `wall_clock` | program time, agent span, end-to-end, agent share, mean program time per submission |
| `tokens` | program vs agent tokens, total, measured vs estimated, per submission, per stage |
| `deterministic_share` | repository bytes scanned, program token share, bytes kept out of the prompt per agent token |
| `dispatch` | judge requests, score entries, scorers, batches, mean batch size, re-dispatches, verifier findings |
| `quality` | mean/min/max total, confidence distribution, evidence items, mean score per 1k tokens |
| `data_quality` | flags for anything that would make the numbers misleading |

## Recording the dispatch shape

The program cannot see how the work was partitioned, so it cannot derive the
scorer count or batch sizes. Write `<out>/run-meta.json`:

```json
{
  "mode": "agent",
  "label": "3 scorers, batches of 3",
  "scorers": 3,
  "batches": 3,
  "mean_batch_size": 3,
  "re_dispatches": 0,
  "verifier_findings": 0
}
```

All keys are optional. Anything absent is reported as `not recorded`, and the
report raises a data-quality flag saying so.

## The three measurement traps

This module encodes three corrections. Getting any of them wrong produces a
number that looks precise and is wrong.

### 1. The agent span is shared, not per-submission

`merge` derives the agent phase from a single `prepare` → `merge` timestamp and
stamps the same value on every record. It is therefore **one wall-clock span**,
not N spans.

- Correct: take the maximum (they are identical).
- Wrong: sum them. Three submissions at 161 s is 161 s of work, not 484 s.

The report sets `wall_clock.agent_span_is_shared` and raises a flag when this
applies. The per-stage table marks the figure `(span)`.

### 2. The agent span includes idle time

It measures elapsed wall-clock between the two program phases, which includes
every moment the agent was not computing. It is an **upper bound** on model
compute, never an estimate of it. Do not present it as compute time.

### 3. Unmeasured tokens are a heuristic, not cost

If the host agent did not supply a `tokens` object in `judge-scores.json`, the
agent figure is `bytes / 4`. It is comparable to the other stages, because they
use the same heuristic, but it is **not provider billing**.

When `tokens.measured` is `0`, the report raises a flag. The comparison view
refuses to declare a winner on tokens in that case, because it would be
comparing two heuristics with the same known bias.

**To get a real figure**, the host agent must add `tokens` to each entry:

```json
{
  "TEAM_001": {
    "scores": { "...": 0 },
    "evidence": [],
    "confidence": "high",
    "tokens": {"prompt_tokens": 25000, "completion_tokens": 900, "total_tokens": 25900}
  }
}
```

`merge` then labels that stage `measured` instead of `estimated`.

## Comparing two modes

The intended use is a Skill-mode run and an Agent-mode run over the **same
cohort, rubric, and prompt version**. The comparison view:

- shows baseline, variant, and percentage change per metric
- warns when the cohort sizes differ
- warns when neither run captured measured usage
- refuses to treat a score delta as a win on its own

It deliberately does **not** print a single "winner". Fewer tokens at a lower
mean score is not an efficiency improvement.

## Adding an efficiency gate

`collect()` returns a plain dict, so a run can be asserted against a budget:

```python
from efficiency import collect

report = collect("out")
assert report["tokens"]["measured"] > 0, "no measured usage; cost is unverifiable"
assert report["wall_clock"]["agent_share_pct"] < 90, "agent dominates wall-clock"
assert not report["data_quality"], report["data_quality"]
```

The third assertion is the useful one: it fails when the run produced numbers
that cannot be quoted safely.

## Known limitations

- the character heuristic (`chars / 4`) is English-prose tuned and will
  under-count for dense code or CJK
- `program_tokens` is a volume proxy for work the program did **without** a
  model; it is not a cost and should never be summed with agent tokens to imply
  a total bill
- there is no per-submission agent timing, because the program has no way to
  observe the agent's internal schedule
- the report reads only files under `--out`; a run whose `judge-requests/` was
  pruned will report fewer requests than it judged
