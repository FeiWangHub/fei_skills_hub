# Main-Agent + Sub-Agent Architecture (for GitHub Copilot)

This document evaluates whether the Code Cup evaluation should run as a
main-agent/sub-agent hierarchy instead of the shipped Skill + program design,
and specifies the hierarchy if it is adopted.

## The framing problem

"Skill or main/sub-agent" is not a real either/or. They answer different
questions:

| Mechanism | Answers |
|---|---|
| Skill | *How does the agent know what to do?* (packaged instructions, rubric, templates) |
| Sub-agent | *How is work distributed and context isolated?* |

A Skill can instruct the main agent to delegate. The real question is narrower:
**does delegating the work to sub-agents help at this scale?**

## What the program already owns

Before any agent is involved, `orchestrator.py prepare` has already produced,
for every submission:

- the static security gate result
- four of seven dimension scores, from repository facts
- the evidence bundle, written to `judge-requests/<id>.md`
- the state file and run timestamp

That work is exact, fast (86 ms for three submissions), and free of model cost.
**None of it should be delegated to a sub-agent.** A sub-agent would add
latency and tokens while reducing precision.

The only delegation candidate is the scoring of D3, D6, and D7.

## Real cost arithmetic

Measured from the committed three-skill run:

```text
judge bundle sizes      117,349 + 88,319 + 103,173 = 308,841 bytes
per submission          ~102,947 bytes ~= 25.7k tokens
extrapolated to 150     150 x 25.7k = 3.86M tokens
```

Three ways to distribute that work:

| Distribution | Bundle volume | Note |
|---|---|---|
| One agent, sequential | 3.86M tokens | current design |
| **Split by dimension** (3 scorers, each reads the full bundle) | **11.6M tokens** | 3× cost |
| **Split by submission** (3 scorers, ~50 submissions each) | 3.86M tokens | same cost |

**Splitting by dimension triples the input cost**, because each scorer must read
the same bundle to judge its own dimension. Splitting by submission does not.

## The throughput assumption does not hold in VS Code Copilot

In VS Code, `runSubagent` is blocking — the caller waits for each result. There
is no fan-out parallelism to gain. Any argument for sub-agents based on
"score 150 submissions in parallel" is not available in this host.

Where sub-agents *do* pay off is **context isolation**, which is a different
problem.

## Why context isolation matters at scale

One bundle is ~25.7k tokens. A nominal 128k-200k context holds roughly five to
seven submissions before overflow. At 150 submissions, a single agent
reading bundles sequentially will exhaust its context long before finishing —
and degrade steadily on the way there.

So at 150 scale, sub-agents (or explicit context resets between batches) are
**not an optimisation, they are required**. The reason is context capacity, not
speed.

Two secondary benefits follow from the same mechanism:

- **Injection containment.** A poisoned submission can affect the sub-agent
  that read it, but not the orchestrator's context or the following
  submissions.
- **Reduced anchoring.** Each scorer works without seeing prior scores, so
  earlier results cannot bias later ones.

## The cost of isolation: comparability

Splitting by submission weakens cross-submission comparability. Three scorers
each applying "is this innovative?" to a different slice of the cohort will
drift apart, which is precisely the score-compression problem the rubric exists
to prevent.

Mitigations, in order of strength:

1. keep splitting to a minimum (2-3 scorers, not 150)
2. ship the same hashed prompt and the same calibration examples to every scorer
3. run a shared gold set through every scorer and check band agreement
4. route any scorer whose gold-set results diverge to manual review

## The architecture, if adopted

Three agent definitions ship with this skill, under `.agents/agents/`:

| Agent | Role | Tools |
|---|---|---|
| `codecup-eval-orchestrator` | decomposes, dispatches, merges | agent, todo, read, execute, search |
| `codecup-eval-scorer` | scores D3/D6/D7 for one batch | read, edit |
| `codecup-eval-verifier` | adversarially checks scores | read |

```text
                    +--------------------------+
                    |  codecup-eval-orchestrator |
                    |  role: orchestrator        |
                    |  tools: agent, todo, read, |
                    |         execute, search    |
                    +-------------+--------------+
                                  |
        program first:  prepare -> scan, classify, gate, score D1/D2/D4/D5,
                                  write judge-requests/<id>.md
                                  |
             +--------------------+--------------------+
             |                    |                    |
    +--------v--------+  +--------v--------+  +--------v--------+
    | scorer (batch 1)|  | scorer (batch 2)|  | verifier        |
    | <=5 submissions |  | <=5 submissions |  | adversarial     |
    | D3 / D6 / D7    |  | D3 / D6 / D7    |  | spot-check      |
    +--------+--------+  +--------+--------+  +--------+--------+
             |                    |                    |
             +--------------------+--------------------+
                                  |
                    orchestrator collects judge-scores.json
                                  |
        program last:  merge -> validate, combine, total, rank, render HTML
```

Four rules keep this honest:

1. **The program runs first and last.** No agent computes a total or a rank.
2. **Scorers write only their own batch's entries**, merging into the shared
   scores file rather than overwriting it. One writer at a time.
3. **The verifier may not score.** It only checks whether cited evidence exists
   at the cited location, and flags unsupported bands.
4. **No agent gets the `web` tool.** The allowlist policy is unchanged.

Note the batch size: **at most 5 submissions per scorer**. One bundle is roughly
25.7k tokens, so five is about as much as fits comfortably alongside the rubric
and the scorer's own reasoning. Batches also stay small to limit drift between
scorers — the fewer scorers, the more comparable their bands.

## Where the two designs are actually equivalent

- Both use the same rubric, bands, and evidence contract.
- Both leave security, structure, documentation, and testing scores to the
  program.
- Both render reports the same way.
- At 1-5 submissions, they produce the same result, and the hierarchy only adds
  overhead.

## Decision guide

| Submissions | Recommended |
|---|---|
| 1-5 | Skill + program only. Sub-agents add cost and nothing else. |
| 6-30 | Skill + program, batched with explicit context resets. Sub-agents optional. |
| 31-100 | Program + 2-3 scorers split by submission, plus a verifier. |
| 100+ | Same, and a verifier becomes mandatory rather than optional. |

## Honest summary

The current Skill + program design is correct for the common case and should
stay the default. The hierarchy is worth adopting for one reason only:
**context capacity at 150 submissions**, where a single agent cannot hold the
work.

It is not worth adopting for speed (unavailable in this host) or for cost
(equal at best, triple if split by dimension).

The strongest hybrid is therefore: keep the Skill as the unit of knowledge, keep
the program as the deterministic spine, and add sub-agents only as batch
scorers when the cohort outgrows a single context.
