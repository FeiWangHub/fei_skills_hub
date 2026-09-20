"""Efficiency telemetry for a Code Cup evaluation run.

Purpose
-------
Answer, from what a finished run already wrote to disk: how long did it take,
how many tokens did it cost, and how much of that cost was the model rather
than the deterministic program?

Design stance
-------------
- **Read-only.** This module reads a finished run and never mutates it. It is
  safe to run against an archived `--out` directory at any time.
- **Stdlib only, no network, Python 3.9+.** Same constraints as the rest of the
  runtime scaffold.
- **Measured and estimated are never conflated.** A run whose judge usage was
  never reported says so, loudly, rather than presenting a character heuristic
  as if it were provider billing. `metrics.py` owns the labelling; this module
  only summarises it and refuses to launder it.
- **Every ratio carries its inputs.** A number that cannot be checked against
  the run files is not emitted.

Two-phase runs have one measurement gap this module cannot close on its own:
the host agent's own token usage. The program can see the request and response
files on disk but not the model's `usage` field, so the agent phase is labelled
`estimated` unless the agent supplied a `tokens` object. `data_quality` flags
that condition explicitly.

Usage:
    python efficiency.py --out <out>
    python efficiency.py --out <out> --mode agent --label "3 scorers"
    python efficiency.py --out <out> --json
    python efficiency.py --out <out> --compare <other-out>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

AGENT_STAGE = "judge_wall_clock"
PROGRAM_STAGES = ("classify", "static_scan", "deterministic_scoring")
META_FILE = "run-meta.json"

CONFIDENCE_ORDER = {"low": 0, "medium": 1, "high": 2}


def _load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _fmt_int(value) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return str(value)


def _fmt_s(value) -> str:
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        return str(value)
    if seconds >= 60:
        return f"{int(seconds // 60)}m {seconds - int(seconds // 60) * 60:.1f}s"
    if seconds >= 1:
        return f"{seconds:.2f}s"
    return f"{seconds * 1000:.1f}ms"


def _pct(part: float, whole: float) -> float:
    return round((part / whole) * 100, 1) if whole else 0.0


def _mean(values: list) -> float:
    return round(sum(values) / len(values), 2) if values else 0.0


def collect(out_dir: str | Path, mode: str | None = None, label: str | None = None) -> dict:
    """Summarise a finished run's time, tokens, and derived efficiency ratios.

    Returns a plain dict so the caller can print it as JSON or render it. Nothing
    here writes to the run directory.
    """
    out = Path(out_dir)
    bundle = _load_json(out / "execution-state.json")
    if bundle is None:
        raise FileNotFoundError(f"No readable run at {out / 'execution-state.json'}")

    results = list(bundle.get("results") or [])
    cost = dict(bundle.get("cost") or {})
    meta = _load_json(out / META_FILE) or {}

    # ---- cohort -----------------------------------------------------------
    def _count(state: str) -> int:
        return sum(1 for r in results if r.get("state") == state)

    cohort = {
        "submissions": len(results),
        "done": _count("done"),
        "awaiting_judge": _count("awaiting-judge"),
        "hard_failed": _count("hard-failed"),
        "failed": _count("failed"),
        "human_review": sum(1 for r in results if r.get("human_review_required")),
        "scored": sum(1 for r in results if r.get("rank") is not None),
    }

    # ---- wall clock -------------------------------------------------------
    # `total_elapsed_s` is recomputed by merge to exclude the agent phase, so it
    # is program compute only. The agent span is stored separately because it
    # includes time the agent spent idle and is therefore an upper bound.
    program_s = 0.0
    agent_s = 0.0
    agent_spans: list[float] = []
    per_submission_program: list[float] = []

    for record in results:
        metrics = record.get("metrics") or {}
        program_s += float(metrics.get("total_elapsed_s", 0) or 0)
        per_submission_program.append(float(metrics.get("total_elapsed_s", 0) or 0))
        span = float(metrics.get("agent_wall_clock_s", 0) or 0)
        if span > 0:
            agent_spans.append(span)

    # A single prepare -> merge span is stamped on every record, so the values
    # are identical by construction. Treating them as per-submission compute
    # time would overstate the model cost by the batch size.
    span_shared = len(agent_spans) > 1 and len(set(agent_spans)) == 1
    agent_s = max(agent_spans) if agent_spans else 0.0

    wall_clock = {
        "program_s": round(program_s, 3),
        "agent_s": round(agent_s, 3),
        "end_to_end_s": round(program_s + agent_s, 3),
        "agent_share_pct": _pct(agent_s, program_s + agent_s),
        "mean_program_per_submission_s": _mean(per_submission_program),
        "agent_span_is_shared": span_shared,
    }

    # ---- tokens -----------------------------------------------------------
    by_stage: dict[str, dict] = {}
    program_tokens = 0
    agent_tokens = 0
    measured_total = 0
    estimated_total = 0

    for record in results:
        metrics = record.get("metrics") or {}
        for stage in metrics.get("stages") or []:
            if not isinstance(stage, dict):
                continue
            name = str(stage.get("name", "unknown"))
            tokens = stage.get("tokens") or {}
            amount = int(tokens.get("total_tokens", 0) or 0)
            source = str(tokens.get("source", "none"))

            entry = by_stage.setdefault(
                name, {"tokens": 0, "elapsed_s": 0.0, "source": source, "calls": 0}
            )
            entry["tokens"] += amount
            stage_elapsed = float(stage.get("elapsed_s", 0) or 0)
            if name == AGENT_STAGE:
                # One prepare->merge span, repeated on every record. Take the
                # maximum so the cohort size does not multiply it.
                entry["elapsed_s"] = round(max(entry["elapsed_s"], stage_elapsed), 3)
            else:
                entry["elapsed_s"] = round(entry["elapsed_s"] + stage_elapsed, 3)
            entry["calls"] += int(tokens.get("calls", 0) or 0)
            # A stage's label can differ between submissions only if one run
            # reported usage and another did not; prefer the weaker label.
            if entry["source"] == "measured" and source != "measured":
                entry["source"] = source

            if source == "measured":
                measured_total += amount
            elif source == "estimated":
                estimated_total += amount

            if name == AGENT_STAGE:
                agent_tokens += amount
            else:
                program_tokens += amount

    total_tokens = int(cost.get("total_tokens", 0) or 0) or (program_tokens + agent_tokens)
    repo_bytes = sum(
        int((r.get("static_gate") or {}).get("bytes_read", 0) or 0) for r in results
    )

    tokens = {
        "total": total_tokens,
        "program": program_tokens,
        "agent": agent_tokens,
        "measured": measured_total,
        "estimated": estimated_total,
        "measured_share_pct": _pct(measured_total, total_tokens),
        "per_submission": round(total_tokens / len(results), 1) if results else 0.0,
        "agent_per_submission": round(agent_tokens / len(results), 1) if results else 0.0,
        "by_stage": by_stage,
    }

    # ---- deterministic share ---------------------------------------------
    # This is the headline efficiency claim of the design: how much of the
    # repository volume the program processed without paying a model for it.
    deterministic = {
        "repo_bytes_scanned": repo_bytes,
        "program_tokens": program_tokens,
        "agent_tokens": agent_tokens,
        "program_share_pct": _pct(program_tokens, total_tokens),
        "bytes_per_agent_token": (
            round(repo_bytes / agent_tokens, 2) if agent_tokens else 0.0
        ),
        "note": (
            "program_tokens are a character heuristic for stages that call no model; "
            "the byte volume is the same repository a naive whole-repo prompt would pay for"
        ),
    }

    # ---- dispatch ---------------------------------------------------------
    request_dir = out / "judge-requests"
    request_files = sorted(request_dir.glob("*.md")) if request_dir.is_dir() else []
    scores = _load_json(out / "judge-scores.json") or {}
    score_entries = len(scores) if isinstance(scores, (dict, list)) else 0

    dispatch = {
        "judge_requests_written": len(request_files),
        "judge_scores_entries": score_entries,
        "scorers": meta.get("scorers", "not recorded"),
        "batches": meta.get("batches", "not recorded"),
        "mean_batch_size": meta.get("mean_batch_size", "not recorded"),
        "re_dispatches": meta.get("re_dispatches", "not recorded"),
        "verifier_findings": meta.get("verifier_findings", "not recorded"),
        "tokens_per_request_byte": (
            round(agent_tokens / max(1, sum(f.stat().st_size for f in request_files)), 4)
            if request_files
            else 0.0
        ),
    }

    # ---- quality / outcome ------------------------------------------------
    totals = [
        float((r.get("scores") or {}).get("total", 0) or 0)
        for r in results
        if r.get("rank") is not None
    ]
    confidences = [str(r.get("confidence", "low")) for r in results]
    evidence_counts = [len(r.get("evidence") or []) for r in results]

    quality = {
        "mean_total": _mean(totals),
        "min_total": min(totals) if totals else 0.0,
        "max_total": max(totals) if totals else 0.0,
        "confidence_high": confidences.count("high"),
        "confidence_medium": confidences.count("medium"),
        "confidence_low": confidences.count("low"),
        "evidence_items_total": sum(evidence_counts),
        "evidence_per_submission": _mean(evidence_counts),
        "mean_score_per_1k_tokens": (
            round(_mean(totals) / (total_tokens / 1000), 3) if total_tokens and totals else 0.0
        ),
    }

    # ---- data quality -----------------------------------------------------
    flags: list[str] = []
    if total_tokens and measured_total == 0:
        flags.append(
            "no measured token usage: every token figure here is a character "
            "heuristic (chars / 4), not provider billing. The host agent did not "
            "supply a `tokens` object in judge-scores.json."
        )
    if span_shared:
        flags.append(
            "agent wall-clock is a single prepare->merge span repeated on every "
            f"record, not per-submission compute time; it includes idle time "
            f"({_fmt_s(agent_s)} for {len(agent_spans)} submissions)."
        )
    provenance = (results[0].get("provenance") or {}) if results else {}
    if str(provenance.get("rubric_version", "")).startswith("unversioned"):
        flags.append(
            "provenance is unversioned (rubric/prompt/model). Two runs are not "
            "comparable across a rubric change until this is populated."
        )
    if cohort["awaiting_judge"]:
        flags.append(f"{cohort['awaiting_judge']} submission(s) still awaiting the judge.")
    if meta.get("scorers", "not recorded") == "not recorded":
        flags.append(
            "dispatch shape not recorded: write run-meta.json into --out to capture "
            "scorer count, batch sizes, and re-dispatches for a mode comparison."
        )

    return {
        "run": {
            "out_dir": str(out),
            "mode": mode or meta.get("mode", "unspecified"),
            "label": label or meta.get("label", ""),
            "generated_at": (bundle.get("state") or {}).get("generated_at", ""),
        },
        "cohort": cohort,
        "wall_clock": wall_clock,
        "tokens": tokens,
        "deterministic_share": deterministic,
        "dispatch": dispatch,
        "quality": quality,
        "data_quality": flags,
    }


def render_markdown(report: dict) -> str:
    """Render the report as markdown for pasting into the run summary."""
    run = report["run"]
    cohort = report["cohort"]
    wall = report["wall_clock"]
    tokens = report["tokens"]
    det = report["deterministic_share"]
    dispatch = report["dispatch"]
    quality = report["quality"]

    title = f"Efficiency — {run['label']}" if run.get("label") else "Efficiency report"

    lines = [
        f"# {title}",
        "",
        f"- Mode: `{run['mode']}`",
        f"- Run: `{run['out_dir']}`",
        f"- Generated: {run.get('generated_at') or 'unknown'}",
        "",
        "## Time",
        "",
        "| Phase | Elapsed | Share |",
        "|---|---:|---:|",
        f"| Deterministic program | {_fmt_s(wall['program_s'])} | {round(100 - wall['agent_share_pct'], 1)}% |",
        f"| Agent judging | {_fmt_s(wall['agent_s'])} | {wall['agent_share_pct']}% |",
        f"| **End to end** | **{_fmt_s(wall['end_to_end_s'])}** | 100% |",
        "",
        f"Mean program time per submission: {_fmt_s(wall['mean_program_per_submission_s'])}",
        "",
        "## Tokens",
        "",
        "| Bucket | Tokens | Source |",
        "|---|---:|---|",
        f"| Program (no model) | {_fmt_int(tokens['program'])} | estimated |",
        f"| Agent judging | {_fmt_int(tokens['agent'])} | {'measured' if tokens['measured'] else 'estimated'} |",
        f"| **Total** | **{_fmt_int(tokens['total'])}** | measured {tokens['measured_share_pct']}% |",
        "",
        f"Per submission: {_fmt_int(tokens['per_submission'])} tokens "
        f"(agent {_fmt_int(tokens['agent_per_submission'])})",
        "",
        "### Per stage",
        "",
        "| Stage | Tokens | Elapsed | Source |",
        "|---|---:|---:|---|",
    ]

    for name, entry in sorted(tokens["by_stage"].items(), key=lambda kv: -kv[1]["tokens"]):
        elapsed = _fmt_s(entry["elapsed_s"])
        if name == AGENT_STAGE:
            elapsed += " (span)"
        lines.append(f"| `{name}` | {_fmt_int(entry['tokens'])} | {elapsed} | {entry['source']} |")

    lines += [
        "",
        "## Deterministic share",
        "",
        f"- Repository volume scanned: {_fmt_int(det['repo_bytes_scanned'])} bytes",
        f"- Program tokens (heuristic): {_fmt_int(det['program_tokens'])} ({det['program_share_pct']}% of total)",
        f"- Agent tokens: {_fmt_int(det['agent_tokens'])}",
        f"- Bytes the deterministic layer kept out of the prompt, per agent token: {det['bytes_per_agent_token']}",
        "",
        "## Dispatch",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Judge requests written | {dispatch['judge_requests_written']} |",
        f"| Scorers | {dispatch['scorers']} |",
        f"| Batches | {dispatch['batches']} |",
        f"| Mean batch size | {dispatch['mean_batch_size']} |",
        f"| Re-dispatches | {dispatch['re_dispatches']} |",
        f"| Verifier findings | {dispatch['verifier_findings']} |",
        "",
        "## Cohort and quality",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Submissions | {cohort['submissions']} |",
        f"| Scored and ranked | {cohort['scored']} |",
        f"| Blocked by static gate | {cohort['hard_failed']} |",
        f"| Awaiting judge | {cohort['awaiting_judge']} |",
        f"| Routed to human review | {cohort['human_review']} |",
        f"| Mean total | {quality['mean_total']} |",
        f"| Confidence h/m/l | {quality['confidence_high']} / {quality['confidence_medium']} / {quality['confidence_low']} |",
        f"| Evidence items | {quality['evidence_items_total']} ({quality['evidence_per_submission']} per submission) |",
        f"| Mean score per 1k tokens | {quality['mean_score_per_1k_tokens']} |",
        "",
    ]

    if report["data_quality"]:
        lines.append("## Data quality flags")
        lines.append("")
        for flag in report["data_quality"]:
            lines.append(f"- {flag}")
        lines.append("")

    return "\n".join(lines)


def _delta(before: float, after: float) -> str:
    if not before:
        return "n/a"
    change = ((after - before) / before) * 100
    sign = "+" if change > 0 else ""
    return f"{sign}{change:.1f}%"


def compare_runs(baseline: dict, variant: dict) -> str:
    """Render a side-by-side cost/time comparison of two runs of the same cohort.

    Deliberately refuses to declare a winner on tokens when neither run captured
    measured usage, because the comparison would then be between two heuristics
    with the same known bias, which flatters whichever run happens to have the
    larger byte volume.
    """
    b_run, v_run = baseline["run"], variant["run"]
    b_wall, v_wall = baseline["wall_clock"], variant["wall_clock"]
    b_tok, v_tok = baseline["tokens"], variant["tokens"]
    b_q, v_q = baseline["quality"], variant["quality"]

    both_unmeasured = b_tok["measured"] == 0 and v_tok["measured"] == 0

    lines = [
        "# Efficiency comparison",
        "",
        f"- Baseline: `{b_run['label'] or b_run['mode']}` — `{b_run['out_dir']}`",
        f"- Variant: `{v_run['label'] or v_run['mode']}` — `{v_run['out_dir']}`",
        "",
        "| Metric | Baseline | Variant | Change |",
        "|---|---:|---:|---:|",
        f"| Submissions | {baseline['cohort']['submissions']} | {variant['cohort']['submissions']} | — |",
        f"| Agent wall-clock | {_fmt_s(b_wall['agent_s'])} | {_fmt_s(v_wall['agent_s'])} | {_delta(b_wall['agent_s'], v_wall['agent_s'])} |",
        f"| Program wall-clock | {_fmt_s(b_wall['program_s'])} | {_fmt_s(v_wall['program_s'])} | {_delta(b_wall['program_s'], v_wall['program_s'])} |",
        f"| End to end | {_fmt_s(b_wall['end_to_end_s'])} | {_fmt_s(v_wall['end_to_end_s'])} | {_delta(b_wall['end_to_end_s'], v_wall['end_to_end_s'])} |",
        f"| Agent tokens | {_fmt_int(b_tok['agent'])} | {_fmt_int(v_tok['agent'])} | {_delta(b_tok['agent'], v_tok['agent'])} |",
        f"| Total tokens | {_fmt_int(b_tok['total'])} | {_fmt_int(v_tok['total'])} | {_delta(b_tok['total'], v_tok['total'])} |",
        f"| Tokens / submission | {_fmt_int(b_tok['per_submission'])} | {_fmt_int(v_tok['per_submission'])} | {_delta(b_tok['per_submission'], v_tok['per_submission'])} |",
        f"| Mean total score | {b_q['mean_total']} | {v_q['mean_total']} | {_delta(b_q['mean_total'], v_q['mean_total'])} |",
        f"| Human review | {baseline['cohort']['human_review']} | {variant['cohort']['human_review']} | — |",
        "",
    ]

    if baseline["cohort"]["submissions"] != variant["cohort"]["submissions"]:
        lines += [
            "> **Not comparable.** The two runs cover different cohort sizes, so the "
            "token and time deltas above mix the mode effect with the cohort effect.",
            "",
        ]

    if both_unmeasured:
        lines += [
            "> **Neither run captured measured token usage.** Both token columns are "
            "the same chars/4 heuristic, so the token delta reflects prompt volume "
            "only. Do not present it as provider cost.",
            "",
        ]

    lines += [
        "## Read this before quoting the numbers",
        "",
        "- Agent wall-clock includes idle time between `prepare` and `merge`; it is an "
        "upper bound on model compute, not model compute.",
        "- A score delta is only meaningful if the same rubric version and the same "
        "prompt version were used. Check `provenance` in both runs.",
        "- Fewer tokens at a lower mean score is not an efficiency win; report both.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report time and token cost for a finished Code Cup run."
    )
    parser.add_argument("--out", required=True, help="Run directory (with execution-state.json)")
    parser.add_argument("--mode", default=None, help="Label the run mode, e.g. skill or agent")
    parser.add_argument("--label", default=None, help="Human label for this run")
    parser.add_argument("--compare", default=None, help="Another --out to compare against")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of markdown")
    parser.add_argument("--write", action="store_true", help="Also write efficiency.md into --out")
    args = parser.parse_args()

    report = collect(args.out, mode=args.mode, label=args.label)

    if args.compare:
        other = collect(args.compare)
        output = compare_runs(other, report)
    elif args.json:
        output = json.dumps(report, indent=2, ensure_ascii=False)
    else:
        output = render_markdown(report)

    print(output)

    if args.write:
        target = Path(args.out) / "efficiency.md"
        target.write_text(render_markdown(report), encoding="utf-8")
        print(f"\nwritten: {target}", file=__import__("sys").stderr)


if __name__ == "__main__":
    main()
