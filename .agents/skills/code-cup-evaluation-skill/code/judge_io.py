"""Two-phase judge workflow for host-agent execution.

This skill runs inside GitHub Copilot, OpenCode, or a similar host agent. The
judging model is the host agent's own model — there is no separate LLM API to
configure, and the pipeline never calls an endpoint on the primary path.

Phase 1 — `prepare`
    Scan every submission, write `judge-requests/<submission_id>.md` containing
    the prompt and a bounded evidence bundle, and stamp the run time. The host
    agent then reads those files and produces scores.

Phase 2 — `merge`
    Read the agent's scores, validate them against the contract, combine them
    with the deterministic dimensions, recompute totals, re-rank, and render
    the reports.

Timing and token accounting
---------------------------
The program can measure its own phases exactly. The agent's judging phase
cannot be measured directly, so it is derived from the timestamp written by
`prepare` and the time `merge` runs, and labelled as such. Token usage for the
agent phase is only recorded when the agent reports it; otherwise it is
recorded as unavailable rather than guessed.

This module performs no network calls.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from aggregator import (
    DEFAULT_WEIGHTS,
    compute_partial_total,
    load_weights,
    rank_results,
)
from judge_adapter import (
    JudgeRequest,
    JudgeValidationError,
    build_evidence_bundle,
    build_prompt,
    load_prompt_template,
    parse_and_validate,
)
from metrics import (
    CHARS_PER_TOKEN,
    SOURCE_ESTIMATED,
    SOURCE_MEASURED,
    SOURCE_NONE,
    TokenUsage,
)
from orchestrator import SCORE_KEYS, run_pipeline

AGENT_STAGE_NAME = "judge_wall_clock"

REQUESTS_DIR = "judge-requests"
AGENT_SCORES_FILE = "judge-scores.json"
RUN_STAMP_FILE = ".run-started-at"

PROMPT_TEMPLATE = "judge-prompt-template.md"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def prepare(
    manifest_path: str,
    allowlist_path: str,
    repo_root: str,
    out_dir: str,
    rubric_path: str | None = None,
    prompt_template_path: str | None = None,
) -> dict:
    """Phase 1: run the deterministic pipeline and emit judge requests."""
    bundle = run_pipeline(manifest_path, allowlist_path, repo_root, out_dir, rubric_path)

    out = Path(out_dir)
    requests_dir = out / REQUESTS_DIR
    requests_dir.mkdir(parents=True, exist_ok=True)

    template_path = Path(prompt_template_path) if prompt_template_path else None
    if template_path is None or not template_path.exists():
        template_path = Path(__file__).resolve().parents[1] / "templates" / PROMPT_TEMPLATE
    template = load_prompt_template(template_path)

    repo_root_path = Path(repo_root)
    prepared = 0

    for record in bundle["results"]:
        if record.get("state") != "awaiting-judge":
            continue

        submission_id = str(record["submission_id"])
        repo_path = repo_root_path / submission_id

        evidence, included = build_evidence_bundle(
            repo_path, str(record.get("artifact_type", "source_project"))
        )

        request = JudgeRequest(
            submission_id=submission_id,
            artifact_type=str(record.get("artifact_type", "")),
            repo_name=submission_id,
            commit_sha=str(record.get("commit_sha", "")),
            team_alias=submission_id,
            rubric_version=str((record.get("provenance") or {}).get("rubric_version", "1")),
            prompt_version="1",
            evidence_bundle=evidence,
            deterministic_scores=dict(record.get("scores") or {}),
            dimensions_to_score=list(record.get("judge_dimensions_pending") or []),
        )

        prompt = build_prompt(template, request)

        header = (
            f"<!-- submission_id: {submission_id} -->\n"
            f"<!-- dimensions_to_score: {', '.join(request.dimensions_to_score)} -->\n"
            f"<!-- files_included: {len(included)} -->\n\n"
        )

        (requests_dir / f"{submission_id}.md").write_text(header + prompt, encoding="utf-8")
        record["judge_request"] = str(requests_dir / f"{submission_id}.md")
        record["evidence_files_included"] = included
        prepared += 1

    (out / RUN_STAMP_FILE).write_text(_now(), encoding="utf-8")
    bundle["state"]["judge_requests_prepared"] = prepared
    bundle["state"]["next_step"] = (
        f"Have the host agent score each file in {REQUESTS_DIR}/ and write the "
        f"results to {AGENT_SCORES_FILE}, then run: orchestrator.py merge"
    )

    (out / "execution-state.json").write_text(
        json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return bundle


def load_agent_scores(path: str | Path) -> dict[str, dict[str, object]]:
    """Read the host agent's scores and validate every entry.

    Accepts either a mapping of submission id to result, or a list of results
    each carrying `submission_id`. Every entry is validated against the judge
    contract, so a malformed or evidence-free response is rejected rather than
    silently scored.
    """
    scores_path = Path(path)
    if not scores_path.exists():
        raise FileNotFoundError(f"Agent scores not found: {scores_path}")

    raw = json.loads(scores_path.read_text(encoding="utf-8"))

    if isinstance(raw, dict):
        entries = []
        for submission_id, value in raw.items():
            if isinstance(value, dict):
                entries.append({**value, "submission_id": submission_id})
    elif isinstance(raw, list):
        entries = raw
    else:
        raise JudgeValidationError("judge-scores.json must be an object or an array")

    validated: dict[str, dict[str, object]] = {}

    for entry in entries:
        if not isinstance(entry, dict):
            raise JudgeValidationError("Each score entry must be an object")
        submission_id = str(entry.get("submission_id", ""))
        if not submission_id:
            raise JudgeValidationError("Each score entry needs a submission_id")

        payload = json.dumps(
            {
                "scores": entry.get("scores"),
                "evidence": entry.get("evidence", []),
                "confidence": entry.get("confidence", "medium"),
            }
        )
        parsed = parse_and_validate(payload)
        parsed["submission_id"] = submission_id
        parsed["tokens"] = entry.get("tokens")
        validated[submission_id] = parsed

    return validated


def merge(
    out_dir: str,
    scores_path: str | None = None,
    rubric_path: str | None = None,
    report: bool = True,
) -> dict:
    """Phase 2: merge the agent's scores into the results and render reports."""
    out = Path(out_dir)
    state_path = out / "execution-state.json"
    if not state_path.exists():
        raise FileNotFoundError(f"No run found at {state_path}; run prepare first")

    bundle = json.loads(state_path.read_text(encoding="utf-8"))
    scores_file = Path(scores_path) if scores_path else out / AGENT_SCORES_FILE
    agent_scores = load_agent_scores(scores_file)

    # The agent phase cannot be timed from inside the program, so it is derived
    # from the stamp written by prepare. Labelled explicitly so it is not
    # confused with a measured stage.
    agent_elapsed_s = None
    stamp_path = out / RUN_STAMP_FILE
    if stamp_path.exists():
        try:
            started = datetime.fromisoformat(stamp_path.read_text(encoding="utf-8").strip())
            agent_elapsed_s = round((datetime.now(timezone.utc) - started).total_seconds(), 3)
        except ValueError:
            agent_elapsed_s = None

    merged = 0
    for record in bundle["results"]:
        submission_id = str(record.get("submission_id", ""))
        agent = agent_scores.get(submission_id)
        if agent is None:
            continue

        judge_scores = agent.get("scores") or {}
        combined = dict(record.get("scores") or {})

        for key in SCORE_KEYS:
            if key in judge_scores:
                combined[key] = judge_scores[key]

        weights = (
            load_weights(rubric_path, str(record.get("artifact_type", "")))
            if rubric_path
            else DEFAULT_WEIGHTS
        )

        weighted = sum(
            float(combined.get(key, 0) or 0) * weights.get(key, 0.0) for key in SCORE_KEYS
        )
        combined["total"] = round((weighted / 5.0) * 100, 2)

        record["scores"] = combined
        # Keep the two evidence sources separate so re-running merge replaces
        # the judge contribution instead of appending it again.
        deterministic_evidence = list(record.get("deterministic_evidence") or [])
        if not deterministic_evidence:
            deterministic_evidence = list(record.get("evidence") or [])
            record["deterministic_evidence"] = deterministic_evidence
        record["judge_evidence"] = list(agent.get("evidence") or [])
        record["evidence"] = deterministic_evidence + record["judge_evidence"]
        record["confidence"] = agent.get("confidence", record.get("confidence", "medium"))
        record["state"] = "done"
        record["scoring_status"] = compute_partial_total(combined, weights, [])
        record["human_review_required"] = (
            record["confidence"] == "low" or bool(record.get("human_review_required"))
        )

        # Attribute the agent phase. Tokens are only claimed if the agent
        # reported them; otherwise the figure is unavailable, not zero-guessed.
        metrics = record.get("metrics") or {}
        stages = [
            s
            for s in (metrics.get("stages") or [])
            if isinstance(s, dict) and s.get("name") != AGENT_STAGE_NAME
        ]
        reported = agent.get("tokens")
        if isinstance(reported, dict):
            token_usage = TokenUsage.from_provider_usage(reported, "host-agent")
            token_source = SOURCE_MEASURED
            token_note = "reported by the host agent"
        else:
            # The host agent does not expose its own usage to the program, but
            # the judging inputs and outputs are on disk, so the volume is
            # measured rather than invented. Labelled `estimated` because the
            # characters-per-token ratio is a heuristic, not provider billing.
            request_path = record.get("judge_request")
            prompt_bytes = 0
            if request_path:
                try:
                    prompt_bytes = Path(str(request_path)).stat().st_size
                except OSError:
                    prompt_bytes = 0

            completion_bytes = len(
                json.dumps(
                    {
                        "scores": agent.get("scores"),
                        "evidence": agent.get("evidence"),
                        "confidence": agent.get("confidence"),
                    },
                    ensure_ascii=False,
                )
            )

            prompt_tokens = int(prompt_bytes / CHARS_PER_TOKEN)
            completion_tokens = int(completion_bytes / CHARS_PER_TOKEN)
            token_usage = TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                source=SOURCE_ESTIMATED,
                model="host-agent",
                calls=1,
            )
            token_source = SOURCE_ESTIMATED
            token_note = (
                "estimated from the judge request and response sizes; "
                "the host agent does not expose its own usage"
            )

        # Replacing any prior judge stage keeps merge idempotent: re-running it
        # must not double-count the same judging pass. Because the estimate is
        # recomputed from the files, re-running is naturally stable.
        stages.append(
            {
                "name": AGENT_STAGE_NAME,
                "elapsed_ms": round((agent_elapsed_s or 0) * 1000, 2),
                "elapsed_s": agent_elapsed_s or 0,
                "tokens": token_usage.as_dict(),
                "timing_source": (
                    "wall-clock from prepare to merge, including idle time; "
                    "an upper bound, not model compute time"
                ),
                "token_source_note": token_note,
            }
        )
        metrics["stages"] = stages
        # Only program-measured stages contribute to the run total. The agent
        # phase is excluded because its wall-clock span includes time the agent
        # spent idle, which is not compute cost and would misrepresent the run.
        measured_stages = [s for s in stages if s.get("name") != AGENT_STAGE_NAME]
        metrics["total_elapsed_s"] = round(
            sum(float(s.get("elapsed_s", 0) or 0) for s in measured_stages), 3
        )
        metrics["total_elapsed_ms"] = round(metrics["total_elapsed_s"] * 1000, 2)
        metrics["agent_wall_clock_s"] = agent_elapsed_s or 0

        # Re-aggregate tokens across *all* stages. Recomputing from the stage
        # list rather than merging into the previous total avoids dropping the
        # estimated volume already recorded by the static scan.
        stage_totals = TokenUsage.unavailable()
        for stage in stages:
            token_info = stage.get("tokens") or {}
            stage_totals = stage_totals.merge(
                TokenUsage(
                    prompt_tokens=int(token_info.get("prompt_tokens", 0) or 0),
                    completion_tokens=int(token_info.get("completion_tokens", 0) or 0),
                    total_tokens=int(token_info.get("total_tokens", 0) or 0),
                    source=str(token_info.get("source", SOURCE_NONE)),
                    model=str(token_info.get("model", "")),
                    calls=int(token_info.get("calls", 0) or 0),
                )
            )
        metrics["total_tokens"] = stage_totals.as_dict()
        record["metrics"] = metrics

        merged += 1

    rank_results(bundle["results"])

    from metrics import summarize

    bundle["cost"] = summarize([r.get("metrics", {}) for r in bundle["results"]])
    bundle["state"]["judge_merged"] = merged
    bundle["state"]["awaiting_judge"] = sum(
        1 for r in bundle["results"] if r.get("state") == "awaiting-judge"
    )
    bundle["state"]["done"] = sum(1 for r in bundle["results"] if r.get("state") == "done")

    if report:
        from report_generator import generate_reports

        bundle["reports"] = generate_reports(bundle, out / "reports")

    state_path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    return bundle
