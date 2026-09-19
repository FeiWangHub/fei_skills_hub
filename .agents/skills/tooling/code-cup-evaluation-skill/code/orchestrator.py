"""Deterministic orchestrator for the Code Cup evaluation pipeline.

Design stance:
- the orchestrator owns flow control, state, and scoring arithmetic
- the LLM judge only scores the qualitative dimensions of an evidence bundle
- network egress is restricted to the allowlist before any request is made

Usage:
    python orchestrator.py --manifest ../templates/submission-manifest-template.yaml \
                           --allowlist ../templates/allowlist.json \
                           [--repo-root ./submissions] [--out ./out]
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from aggregator import rank_results
from allowlist import NetworkAllowlist
from artifact_classifier import classify
from manifest_loader import load_manifest, normalize_submissions, validate_manifest
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

DEFAULT_WEIGHTS = {
    "skill": 0.15,
    "copilot_agent": 0.15,
    "opencode_agent": 0.15,
    "source_project": 0.15,
}


def aggregate(total_weighted: float) -> float:
    """Normalize a weighted sum into an anchored 0-100 scale."""
    return round(total_weighted, 2)


def compute_confidence(static_passed: bool, review_issue_count: int) -> str:
    """Derive a coarse confidence label from deterministic signals only."""
    if not static_passed:
        return "low"
    if review_issue_count == 0:
        return "high"
    if review_issue_count <= 2:
        return "medium"
    return "low"


def evaluate_submission(
    submission,
    repo_root: Path,
    allowlist: NetworkAllowlist,
    output_root: Path,
) -> dict[str, object]:
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
        }
        record["scores"] = {**{key: 0 for key in SCORE_KEYS}, "total": 0}
        record["confidence"] = "low"
        record["human_review_required"] = True
        record["evidence"] = []
        record["provenance"] = {
            "rubric_version": "unversioned",
            "prompt_version": "unversioned",
            "model_version": "not-run",
            "scanned_at": datetime.now(timezone.utc).isoformat(),
        }
        return record

    detected_type, rationale = classify(repo_path)
    record["classification"] = {
        "detected": detected_type,
        "declared": submission.artifact_type,
        "rationale": rationale,
        "mismatch": detected_type != submission.artifact_type,
    }

    scan_result = scan_repository(repo_path, allowlist)
    record["static_gate"] = scan_result.as_dict()

    if not scan_result.passed:
        record["state"] = "hard-failed"
        record["scores"] = {**{key: 0 for key in SCORE_KEYS}, "total": 0}
        record["confidence"] = "low"
        record["human_review_required"] = False
        record["evidence"] = []
        record["provenance"] = {
            "rubric_version": "unversioned",
            "prompt_version": "unversioned",
            "model_version": "not-run",
            "scanned_at": datetime.now(timezone.utc).isoformat(),
        }
        return record

    # Static gate passed. Qualitative scoring is deferred to the judge stage,
    # which must run through the allowlist-enforced internal transport.
    record["state"] = "awaiting-judge"
    record["scores"] = {**{key: 0 for key in SCORE_KEYS}, "total": 0}
    record["confidence"] = compute_confidence(
        scan_result.passed, len(scan_result.findings)
    )
    record["human_review_required"] = record["confidence"] == "low"
    record["evidence"] = []
    record["provenance"] = {
        "rubric_version": "unversioned",
        "prompt_version": "unversioned",
        "model_version": "not-run",
        "scanned_at": datetime.now(timezone.utc).isoformat(),
    }
    return record


def run_pipeline(manifest_path: str, allowlist_path: str, repo_root: str, out_dir: str) -> dict:
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
        evaluate_submission(s, repo_root_path, allowlist, output_root)
        for s in submissions
    ]

    state = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(results),
        "hard_failed": sum(1 for r in results if r.get("state") == "hard-failed"),
        "awaiting_judge": sum(1 for r in results if r.get("state") == "awaiting-judge"),
        "failed": sum(1 for r in results if r.get("state") == "failed"),
    }

    bundle = {"state": state, "results": results}

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
    bundle = run_pipeline(manifest_path, allowlist_path, repo_root, out_dir)

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
    parser = argparse.ArgumentParser(description="Code Cup evaluation orchestrator")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--allowlist", required=True)
    parser.add_argument("--repo-root", default="./submissions")
    parser.add_argument("--out", default="./out")
    parser.add_argument("--rubric", default=None, help="Path to score-rubric.yaml")
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip static HTML report generation",
    )
    args = parser.parse_args()

    bundle = run_full_pipeline(
        args.manifest,
        args.allowlist,
        args.repo_root,
        args.out,
        rubric_path=args.rubric,
        report=not args.no_report,
    )
    print(json.dumps(bundle["state"], indent=2))


if __name__ == "__main__":
    main()
