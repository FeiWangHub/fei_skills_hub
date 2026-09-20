# Code Cup Evaluation Skill

A deterministic-first evaluation framework for large internal hackathon judging,
with a static security gate, an allowlist-enforced network policy, and a
constrained judge that cannot compute its own totals.

- **Full instructions**: [`SKILL.md`](./SKILL.md)
- **Delivery plan**: [`IMPLEMENTATION-PLAN.md`](./IMPLEMENTATION-PLAN.md)
- **Runnable code**: [`code/`](./code)

## Where this belongs

Put the evaluation findings in `SKILL.md`, not here.

`SKILL.md` is what a model reads when the skill triggers, so anything a model
must act on has to live there. This README is for a human deciding whether to
use the skill. Duplicating rules across the two would let them drift, which is
the failure mode this repository has already hit once with its own index.

The split used here:

| Content | Location |
|---|---|
| Rules, contract, architecture a model must follow | `SKILL.md` |
| Decision guidance, comparison, rationale for a human | this README |
| Detail too long for either | `references/` |
| Executable logic | `code/` |

## How it runs

Two phases, with the host agent judging in between. There is no external LLM
endpoint on the primary path.

```text
prepare   program scans repos, writes judge-requests/<id>.md
   ↓
          host agent reads each request and produces scores
   ↓
merge     program validates, combines, totals, ranks, renders HTML
```

## Skill + program, or main agent + sub-agents?

Both, tiered by cohort size. They answer different questions: a Skill packages
*what to do*; sub-agents distribute *where the work runs*.

| Submissions | Recommended |
|---|---|
| 1-5 | Skill + program only. Sub-agents add cost and nothing else. |
| 6-30 | Skill + program, batched with explicit context resets. Sub-agents optional. |
| 31-100 | Program + 2-3 scorers split by submission, in parallel, plus a verifier. |
| 100+ | Same, and the verifier becomes mandatory. |

### Why the tier exists

Two measured facts drive it, both from the committed runs:

- One judge bundle is ~103 KB, about **25.7k tokens**. Three bundles already cost
  ~77k, so a 128k context holds roughly three submissions once the rubric,
  prompt, and the agent's own reasoning are accounted for. At 150 submissions a
  single agent cannot hold the work.
- Splitting scoring **by dimension** triples input cost, because each scorer must
  read the same bundle to judge its own dimension. Splitting **by submission**
  does not.

Sub-agents run in parallel in both VS Code and OpenCode, so batching also buys
wall-clock time. It does not reduce cost per submission.

**The hierarchy is worth adopting for context capacity and latency. It is not
worth adopting to save money.**

## What ships

| Path | Purpose |
|---|---|
| `code/orchestrator.py` | CLI: `prepare`, `merge`, `scan-only` |
| `code/deterministic_scorer.py` | Scores D1/D2/D4/D5 from repository facts, no LLM |
| `code/static_scanner.py` | Secret, injection, and unapproved-host scanning |
| `code/judge_io.py` | The two-phase workflow, including score validation |
| `code/report_generator.py` | Escaped, CDN-free static HTML |
| `code/tests/` | Five standard-library test suites |

Agent definitions for the delegated tier live at the repository root:
`.github/agents/codecup-eval-*.agent.md` (VS Code format) and
`.agents/agents/codecup-eval-*/` (portable format).

## Quick start

```bash
cd code
for t in test_gates test_pipeline test_deterministic_scorer test_metrics test_judge_io test_efficiency; do
  PYTHONPATH=. python3 tests/$t.py
done

PYTHONPATH=. python3 orchestrator.py prepare \
  --manifest ../templates/submission-manifest-template.yaml \
  --allowlist ../templates/allowlist.json \
  --repo-root /path/to/snapshots --out ./out \
  --rubric ../templates/score-rubric.yaml
```

Then have the host agent write `out/judge-scores.json` and run `merge`. Requires
Python 3.9+. `PyYAML` is needed for YAML manifests; JSON works without it.

### Where a run is written

Every run goes under `code-cup-eval-artifacts/` at the repository root, in a
directory named `<cohort>-eval-<mode>`:

| Part | Meaning | Examples |
|---|---|---|
| `<cohort>` | what was scored | `codecup`, `caveman`, `pptx-skill` |
| `<mode>` | how it was scored | `sample`, `agent`, `skill` |

`mode` describes the **scoring mechanism**, not the model: `agent` means the
orchestrator dispatched scorer sub-agents, `skill` means the Skill ran inside a
single host-agent context.

Sample completed runs are committed under `code-cup-eval-artifacts/`
(`codecup-eval-sample`, `caveman-eval-sample`).

Do not reuse one directory for two cohorts — `prepare` overwrites in place and
`merge` replaces the judge contribution, so a shared `--out` silently merges
both into one leaderboard.

## Reference documents

| Document | Covers |
|---|---|
| `references/two-phase-workflow.md` | Command reference, scores format, failure behaviour |
| `references/deterministic-scoring.md` | Per-dimension thresholds and their weaknesses |
| `references/cost-and-timing.md` | How timing and token figures are measured vs estimated |
| `references/main-subagent-architecture.md` | Full comparison, cost arithmetic, host differences |
| `references/judge-prompt-assembly.md` | Evidence bundling and untrusted-content handling |

## Honest limitations

- The judge stage is not invoked by the program. Records stay `awaiting-judge`
  until a host agent produces scores.
- Deterministic D4/D5 use file counts and byte sizes as proxies and could be
  gamed with filler files.
- The static scanner is regex-based. `gitleaks` and `semgrep` should be layered
  on top for recall.
- Token figures for the judging phase are estimates derived from on-disk file
  sizes, not provider billing, and are labelled as such.
