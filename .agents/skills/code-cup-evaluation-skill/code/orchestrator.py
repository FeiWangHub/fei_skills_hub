"""Deterministic orchestrator for the Code Cup evaluation pipeline.

Design stance:
- the orchestrator owns flow control, state, and scoring arithmetic
- dimensions that can be judged from repository facts are scored with no LLM
- the LLM judge scores only the qualitative remainder
- network egress is restricted to the allowlist before any request is made

Usage:
    python orchestrator.py --manifest ../templates/submission-manifest-template.yaml \
                           --allowlist ../templates/allowlist.json \
                           [--repo-root ./submissions] [--out ./out]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from aggregator import (
    DEFAULT_WEIGHTS,
    compute_partial_total,
    load_weights,
    rank_results,
)
from allowlist import NetworkAllowlist
from artifact_classifier import classify
from deterministic_scorer import DETERMINISTIC_DIMENSIONS, score_deterministic
from manifest_loader import load_manifest, normalize_submissions, validate_manifest
from metrics import (
    RunMetrics,
    TokenUsage,
    summarize,
    timed_stage,
)
from static_scanner import scan_repository

SCORE_KEYS = (
    "d1_security_and_compliance",
    "d2_structure_and_conformance",
    "d3_code_quality",
    "d4_documentation",
    "d5_testing_and_reliability",
    "d6_business_value",
    "d7_innovation",
)


def _empty_scores() -> dict[str, int]:
    return {**{key: 0 for key in SCORE_KEYS}, "total": 0}


def _provenance(model_version: str = "not-run") -> dict[str, str]:
    return {
        "rubric_version": "unversioned",
        "prompt_version": "unversioned",
        "model_version": model_version,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
    }


def evaluate_submission(
    submission,
    repo_root: Path,
    allowlist: NetworkAllowlist,
    rubric_path: str | None = None,
) -> dict[str, object]:
    """Run the deterministic stages for one submission.

    Returns a record in one of the states: `failed`, `hard-failed`, or
    `awaiting-judge`. Dimensions that can be scored from repository facts are
    filled in here; the judge-only dimensions remain at 0 until the judge runs.

    Each stage records its own elapsed time and token accounting under
    `metrics`, so two scoring variants can be compared directly.
    """
    metrics = RunMetrics()

    record: dict[str, object] = {
        "submission_id": submission.submission_id,
        "team_name": submission.team_name,
        "artifact_type": submission.artifact_type,
        "commit_sha": submission.commit_sha,
        "state": "running",
    }

    repo_path = repo_root / submission.submission_id

    if not repo_path.exists():
        record["state"] = "failed"
        record["error"] = f"repository snapshot not found at {repo_path}"
        record["static_gate"] = {
            "passed": False,
            "hard_failed": True,
            "issues": ["repository snapshot missing"],
            "findings": [],
        }
        record["scores"] = _empty_scores()
        record["confidence"] = "low"
        record["human_review_required"] = True
        record["evidence"] = []
        record["provenance"] = _provenance()
        record["metrics"] = metrics.as_dict()
        return record

    with timed_stage(metrics, "classify"):
        detected_type, rationale = classify(repo_path)

    record["classification"] = {
        "detected": detected_type,
        "declared": submission.artifact_type,
        "rationale": rationale,
        "mismatch": detected_type != submission.artifact_type,
    }

    with timed_stage(metrics, "static_scan"):
        scan_result = scan_repository(repo_path, allowlist)

    record["static_gate"] = scan_result.as_dict()

    # The scanner reads the whole repository, so the volume it processed is the
    # meaningful cost signal for this stage. This is a character-based estimate
    # tagged `estimated`: no model is called, so it is not provider usage.
    #
    # For comparison, this is the same volume a naive "send the repo to the LLM"
    # approach would have to pay for.
    metrics.stages[-1].tokens = TokenUsage.estimated_from_text(
        "x" * int(scan_result.bytes_read)
    )

    if not scan_result.passed:
        record["state"] = "hard-failed"
        record["scores"] = _empty_scores()
        record["confidence"] = "low"
        record["human_review_required"] = False
        record["evidence"] = []
        record["provenance"] = _provenance()
        record["metrics"] = metrics.as_dict()
        return record

    # Static gate passed. Score every dimension that does not require judgement,
    # so the deterministic share of the rubric is computed without any LLM call.
    with timed_stage(metrics, "deterministic_scoring"):
        scored = score_deterministic(repo_path, submission.artifact_type, scan_result.findings)

    scores: dict[str, object] = dict(scored.scores)
    for key in SCORE_KEYS:
        scores.setdefault(key, 0)
    scores["total"] = 0

    record["state"] = "awaiting-judge"
    record["scores"] = scores
    record["deterministic_rationales"] = scored.rationales
    record["judge_dimensions_pending"] = list(scored.judge_dimensions)
    record["evidence"] = scored.evidence

    # A bare `total: 0` reads as "scored zero" when it actually means "not
    # scored yet". Record the partial contribution explicitly so reports can
    # say which it is.
    record["scoring_status"] = compute_partial_total(
        scores,
        load_weights(rubric_path, submission.artifact_type) if rubric_path else DEFAULT_WEIGHTS,
        list(scored.judge_dimensions),
    )

    # No model has been called at this point. The judge stage is deliberately
    # absent from `metrics.stages` rather than recorded as a zero-duration
    # stage, because it did not run. A caller that runs the judge appends its
    # own stage with real elapsed time and provider-reported usage.

    # Pre-judge confidence cannot be `high`: judge agreement has not been
    # demonstrated yet, and a single unverified pass is never enough. Suspicious
    # static findings downgrade it further.
    review_findings = [f for f in scan_result.findings if f.get("severity") == "review"]
    if len(review_findings) > 2:
        record["confidence"] = "low"
    else:
        record["confidence"] = "medium"

    # Any review-severity finding requires a human look, independently of the
    # confidence label. This is the escalation path the scan checklist defines
    # for prompt-injection and PII findings.
    record["human_review_required"] = bool(review_findings) or record["confidence"] == "low"
    record["provenance"] = _provenance()
    record["metrics"] = metrics.as_dict()
    return record


def run_pipeline(
    manifest_path: str,
    allowlist_path: str,
    repo_root: str,
    out_dir: str,
    rubric_path: str | None = None,
) -> dict:
    manifest = load_manifest(manifest_path)
    problems = validate_manifest(manifest)
    if problems:
        raise ValueError("Manifest validation failed: " + "; ".join(problems))

    allowlist = NetworkAllowlist.from_file(allowlist_path)
    submissions = normalize_submissions(manifest)

    repo_root_path = Path(repo_root)
    output_root = Path(out_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    results = [
        evaluate_submission(s, repo_root_path, allowlist, rubric_path)
        for s in submissions
    ]

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(results),
        "hard_failed": sum(1 for r in results if r.get("state") == "hard-failed"),
        "awaiting_judge": sum(1 for r in results if r.get("state") == "awaiting-judge"),
        "failed": sum(1 for r in results if r.get("state") == "failed"),
        "deterministic_dimensions": list(DETERMINISTIC_DIMENSIONS),
    }

    bundle = {
        "state": state,
        "cost": summarize([r.get("metrics", {}) for r in results]),
        "results": results,
    }

    (output_root / "execution-state.json").write_text(
        json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return bundle



def run_full_pipeline(
    manifest_path: str,
    allowlist_path: str,
    repo_root: str,
    out_dir: str,
    rubric_path: str | None = None,
    report: bool = True,
) -> dict:
    """Run L0/L1 gating, then rank and optionally render static reports.

    The judge stage is intentionally not invoked here: it requires a live
    internal endpoint and API credentials, so it is wired in by the caller
    via `judge_transport.JudgeTransport`. Until then, records remain in the
    `awaiting-judge` state rather than being given an invented score.
    """
    bundle = run_pipeline(manifest_path, allowlist_path, repo_root, out_dir, rubric_path)

    results = bundle["results"]
    rank_results(results)

    if report:
        from report_generator import generate_reports

        written = generate_reports(bundle, Path(out_dir) / "reports")
        bundle["reports"] = written

    output_root = Path(out_dir)
    (output_root / "execution-state.json").write_text(
        json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return bundle


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Code Cup evaluation pipeline. Runs inside a host agent (GitHub "
            "Copilot, OpenCode, ...); the judging model is the host's own model."
        )
    )
    sub = parser.add_subparsers(dest="command")

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--out", default="./out")
        p.add_argument("--rubric", default=None, help="Path to score-rubric.yaml")

    prepare_parser = sub.add_parser(
        "prepare",
        help="Scan submissions and emit judge requests for the host agent",
    )
    prepare_parser.add_argument("--manifest", required=True)
    prepare_parser.add_argument("--allowlist", required=True)
    prepare_parser.add_argument("--repo-root", default="./submissions")
    prepare_parser.add_argument("--prompt-template", default=None)
    add_common(prepare_parser)

    merge_parser = sub.add_parser(
        "merge",
        help="Merge the host agent's scores and render reports",
    )
    merge_parser.add_argument(
        "--scores",
        default=None,
        help="Path to judge-scores.json (default: <out>/judge-scores.json)",
    )
    merge_parser.add_argument("--no-report", action="store_true")
    add_common(merge_parser)

    # Backwards-compatible single-shot mode: scan, rank and report without a
    # judge pass. Useful for checking the deterministic layer alone.
    scan_parser = sub.add_parser("scan-only", help="Deterministic layer only, no judge")
    scan_parser.add_argument("--manifest", required=True)
    scan_parser.add_argument("--allowlist", required=True)
    scan_parser.add_argument("--repo-root", default="./submissions")
    scan_parser.add_argument("--no-report", action="store_true")
    add_common(scan_parser)

    # Read-only cost/time reporting for a finished run. Useful for comparing a
    # Skill-mode run against an Agent-mode run on the same cohort.
    eff_parser = sub.add_parser(
        "efficiency",
        help="Report time, token cost and efficiency ratios for a finished run",
    )
    eff_parser.add_argument("--mode", default=None, help="Run mode label, e.g. skill or agent")
    eff_parser.add_argument("--label", default=None, help="Human label for this run")
    eff_parser.add_argument("--compare", default=None, help="Another --out to compare against")
    eff_parser.add_argument("--json", action="store_true", help="Emit JSON instead of markdown")
    eff_parser.add_argument(
        "--write", action="store_true", help="Also write efficiency.md into --out"
    )
    add_common(eff_parser)

    args = parser.parse_args()

    if args.command == "prepare":
        from judge_io import prepare

        bundle = prepare(
            args.manifest,
            args.allowlist,
            args.repo_root,
            args.out,
            rubric_path=args.rubric,
            prompt_template_path=args.prompt_template,
        )
        print(json.dumps(bundle["state"], indent=2))
        return

    if args.command == "merge":
        from judge_io import merge

        bundle = merge(
            args.out,
            scores_path=args.scores,
            rubric_path=args.rubric,
            report=not args.no_report,
        )
        print(json.dumps(bundle["state"], indent=2))
        return

    if args.command == "scan-only":
        bundle = run_full_pipeline(
            args.manifest,
            args.allowlist,
            args.repo_root,
            args.out,
            rubric_path=args.rubric,
            report=not args.no_report,
        )
        print(json.dumps(bundle["state"], indent=2))
        return

    if args.command == "efficiency":
        from efficiency import collect, compare_runs, render_markdown

        report = collect(args.out, mode=args.mode, label=args.label)

        if args.compare:
            output = compare_runs(collect(args.compare), report)
        elif args.json:
            output = json.dumps(report, indent=2, ensure_ascii=False)
        else:
            output = render_markdown(report)

        print(output)

        if args.write:
            target = Path(args.out) / "efficiency.md"
            target.write_text(render_markdown(report), encoding="utf-8")
            print(f"written: {target}", file=sys.stderr)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
