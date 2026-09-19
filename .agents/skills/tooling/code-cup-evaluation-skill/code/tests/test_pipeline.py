"""Tests for aggregation, egress enforcement, and static report rendering.

Run with:
    PYTHONPATH=. python3 tests/test_pipeline.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aggregator import (  # noqa: E402
    DEFAULT_WEIGHTS,
    aggregate,
    derive_confidence,
    load_weights,
    rank_results,
)
from allowlist import NetworkAllowlist  # noqa: E402
from judge_transport import EgressBlockedError, JudgeTransport, TransportConfig  # noqa: E402
from report_generator import render_dashboard, render_submission_report  # noqa: E402

FAILURES: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"PASS  {label}")
    else:
        print(f"FAIL  {label} {detail}")
        FAILURES.append(label)


def _pass(d1: int, d7: int, evidence=None) -> dict:
    return {
        "scores": {
            "d1_security_and_compliance": d1,
            "d2_structure_and_conformance": 3,
            "d3_code_quality": 3,
            "d4_documentation": 3,
            "d5_testing_and_reliability": 3,
            "d6_business_value": 3,
            "d7_innovation": d7,
        },
        "confidence": "high",
        "evidence": evidence
        if evidence is not None
        else [{"file_path": "SKILL.md", "line_or_range": "1", "note": "ok"}],
    }


def test_aggregation_median() -> None:
    result = aggregate([_pass(5, 1), _pass(1, 5)], DEFAULT_WEIGHTS)
    check("median reconciles disagreement", result.scores["d1_security_and_compliance"] == 3.0)
    check("spread reflects max disagreement", result.spread == 4)
    check("large spread forces low confidence", result.confidence == "low")
    check("low confidence requires review", result.human_review_required is True)


def _pass_all(value: int, evidence=None) -> dict:
    return {
        "scores": {key: value for key in DEFAULT_WEIGHTS},
        "confidence": "high",
        "evidence": evidence
        if evidence is not None
        else [{"file_path": "SKILL.md", "line_or_range": "1", "note": "ok"}],
    }


def test_aggregation_agreement() -> None:
    result = aggregate([_pass(5, 5), _pass(5, 5)], DEFAULT_WEIGHTS)
    check("agreement yields high confidence", result.confidence == "high")
    check("agreement needs no review", result.human_review_required is False)

    # Two dimensions at 5 with the rest at 3 averages 25/7, i.e. 71.43 on a 0-100 scale.
    check(
        "partial scores project onto the 0-100 scale",
        result.total == round((25 / 7) / 5 * 100, 2),
        str(result.total),
    )

    top = aggregate([_pass_all(5), _pass_all(5)], DEFAULT_WEIGHTS)
    check("all-top-band submissions reach 100", top.total == 100.0, str(top.total))

    bottom = aggregate([_pass_all(1), _pass_all(1)], DEFAULT_WEIGHTS)
    check("all-lowest-band submissions score 20", bottom.total == 20.0, str(bottom.total))


def test_single_pass_cannot_be_high() -> None:
    result = aggregate([_pass(5, 5)], DEFAULT_WEIGHTS)
    check(
        "single pass cannot claim high confidence",
        result.confidence == "medium",
        result.confidence,
    )


def test_confidence_rules() -> None:
    check("spread 0 with two passes is high", derive_confidence(0, 2, 0) == "high")
    check("spread 1 is medium", derive_confidence(1, 2, 0) == "medium")
    check("spread 2 is low", derive_confidence(2, 2, 0) == "low")
    check(
        "many review findings downgrade to medium",
        derive_confidence(0, 2, 5) == "medium",
    )


def test_weight_loading() -> None:
    rubric = Path(__file__).resolve().parents[2] / "templates" / "score-rubric.yaml"
    try:
        weights = load_weights(rubric, "skill")
    except Exception as exc:  # PyYAML may be absent in a restricted environment
        print(f"SKIP  rubric weight loading ({exc})")
        return

    check("weights load for skill", abs(sum(weights.values()) - 1.0) < 1e-9)
    check("all dimensions present", len(weights) == 7)

    missing = load_weights("/nonexistent/rubric.yaml", "skill")
    check("missing rubric falls back to defaults", missing == DEFAULT_WEIGHTS)


def test_ranking_flags_top_slice_low_confidence() -> None:
    records = [
        {"submission_id": "T1", "total": 90.0, "confidence": "low", "state": "done"},
        {"submission_id": "T2", "total": 80.0, "confidence": "high", "state": "done"},
        {"submission_id": "T3", "total": 70.0, "confidence": "high", "state": "done"},
        {"submission_id": "T4", "total": 60.0, "confidence": "high", "state": "done"},
    ]
    ranked = rank_results(records)
    check("ranking sorts by total", ranked[0]["submission_id"] == "T1")
    check("ranks are assigned", [r["rank"] for r in ranked] == [1, 2, 3, 4])
    check(
        "low confidence in top slice is flagged",
        ranked[0].get("human_review_required") is True,
    )
    check(
        "low confidence outside top slice is not force-flagged",
        "human_review_required" not in ranked[3],
    )


def test_ranking_excludes_non_scored_submissions() -> None:
    records = [
        {"submission_id": "BLOCKED", "total": 0, "confidence": "low", "state": "hard-failed"},
        {"submission_id": "SCORED", "total": 55.0, "confidence": "high", "state": "done"},
        {"submission_id": "PENDING", "total": 0, "confidence": "high", "state": "awaiting-judge"},
    ]
    ranked = rank_results(records)

    check("scored submission ranks first", ranked[0]["submission_id"] == "SCORED")
    check("scored submission gets rank 1", ranked[0]["rank"] == 1)
    check(
        "hard-failed submission is not ranked",
        "rank" not in ranked[1] or ranked[1]["submission_id"] != "BLOCKED",
    )

    blocked = next(r for r in ranked if r["submission_id"] == "BLOCKED")
    pending = next(r for r in ranked if r["submission_id"] == "PENDING")

    check("hard-failed submission receives no rank", "rank" not in blocked)
    check("awaiting-judge submission receives no rank", "rank" not in pending)
    check(
        "hard-failed submission is not flagged as top-slice review",
        "review_reason" not in blocked,
    )


def test_egress_is_blocked() -> None:
    al = NetworkAllowlist(
        allowed_domains=[".example", "llm.internal.example"],
        blocked_domains=["evil.com"],
    )

    blocked = JudgeTransport(
        TransportConfig(endpoint_url="https://api.evil.com/v1/chat", model="m"),
        al,
    )
    try:
        blocked("prompt")
        check("transport blocks non-approved endpoint", False)
    except EgressBlockedError:
        check("transport blocks non-approved endpoint", True)

    blocked_listed = JudgeTransport(
        TransportConfig(endpoint_url="https://evil.com/v1/chat", model="m"),
        al,
    )
    try:
        blocked_listed("prompt")
        check("transport blocks explicit blocklist entry", False)
    except EgressBlockedError:
        check("transport blocks explicit blocklist entry", True)

    allowed = JudgeTransport(
        TransportConfig(endpoint_url="https://llm.internal.example/v1/chat", model="m"),
        al,
    )
    try:
        allowed.assert_allowed()
        check("transport permits approved internal endpoint", True)
    except EgressBlockedError as exc:
        check("transport permits approved internal endpoint", False, str(exc))


def test_report_escapes_hostile_input() -> None:
    record = {
        "submission_id": "T1",
        "team_name": "<script>alert('xss')</script>",
        "artifact_type": "skill",
        "commit_sha": "abc123",
        "state": "done",
        "confidence": "high",
        "human_review_required": False,
        "total": 80.0,
        "rank": 1,
        "scores": {k: 3 for k in DEFAULT_WEIGHTS},
        "evidence": [{"file_path": "a<b>.md", "line_or_range": "1", "note": "n"}],
        "static_gate": {"passed": True, "hard_failed": False, "issues": [], "findings": []},
        "provenance": {
            "rubric_version": "1",
            "prompt_version": "1",
            "model_version": "m",
            "scanned_at": "2026-09-19T00:00:00Z",
        },
    }

    page = render_submission_report(record)
    check("report escapes script tag", "<script>alert" not in page)
    check("report keeps escaped form", "&lt;script&gt;" in page)
    check("report has no external asset references", "http://" not in page and "https://" not in page)
    check("report sets no-referrer", 'name="referrer"' in page)


def test_dashboard_renders() -> None:
    records = [
        {
            "submission_id": "T1",
            "team_name": "Alpha",
            "artifact_type": "skill",
            "total": 88.0,
            "rank": 1,
            "confidence": "high",
            "state": "done",
            "human_review_required": False,
            "static_gate": {"passed": True},
        },
        {
            "submission_id": "T2",
            "team_name": "Beta",
            "artifact_type": "source_project",
            "total": 0,
            "rank": 2,
            "confidence": "low",
            "state": "hard-failed",
            "human_review_required": False,
            "static_gate": {"passed": False},
        },
    ]
    page = render_dashboard(records, generated_at="2026-09-19T00:00:00Z")
    check("dashboard lists submissions", "Alpha" in page and "Beta" in page)
    check("dashboard counts blocked submissions", "1 blocked" in page)
    check("dashboard marks gate failure", "blocked</td>" in page)


def test_dashboard_links_to_each_report() -> None:
    records = [
        {
            "submission_id": "TEAM_001",
            "team_name": "Alpha",
            "artifact_type": "skill",
            "total": 88.0,
            "rank": 1,
            "confidence": "high",
            "state": "done",
            "human_review_required": False,
            "static_gate": {"passed": True},
        },
        {
            "submission_id": "TEAM/002 weird",
            "team_name": "Beta",
            "artifact_type": "source_project",
            "total": 0,
            "rank": 2,
            "confidence": "low",
            "state": "hard-failed",
            "human_review_required": False,
            "static_gate": {"passed": False},
        },
    ]
    page = render_dashboard(records, generated_at="2026-09-19T00:00:00Z")

    check("dashboard links to first report", 'href="TEAM_001.html"' in page)
    check(
        "dashboard sanitises unsafe characters in links",
        'href="TEAM_002_weird.html"' in page,
    )
    check(
        "dashboard does not emit a raw unsafe path",
        "TEAM/002" not in page,
    )
    check(
        "team name is the only link, avoiding a duplicate details column",
        page.count('href="TEAM_001.html"') == 1,
        str(page.count('href="TEAM_001.html"')),
    )


def test_report_filename_is_shared() -> None:
    from report_generator import report_filename

    check("filename is stable for safe ids", report_filename("TEAM_001") == "TEAM_001.html")
    check(
        "filename sanitises separators",
        report_filename("a/b\\c") == "a_b_c.html",
        report_filename("a/b\\c"),
    )
    check("filename handles empty ids", report_filename("") == "unknown.html")


def test_generate_reports_writes_linked_pages() -> None:
    from report_generator import generate_reports, report_filename

    bundle = {
        "state": {},
        "results": [
            {
                "submission_id": "TEAM_001",
                "team_name": "Alpha",
                "artifact_type": "skill",
                "commit_sha": "a" * 40,
                "state": "awaiting-judge",
                "confidence": "medium",
                "human_review_required": False,
                "total": 0,
                "scores": {k: 3 for k in DEFAULT_WEIGHTS},
                "evidence": [],
                "static_gate": {"passed": True, "hard_failed": False, "issues": [], "findings": []},
                "provenance": {
                    "rubric_version": "1",
                    "prompt_version": "1",
                    "model_version": "not-run",
                    "scanned_at": "2026-09-19T00:00:00Z",
                },
            }
        ],
    }

    with tempfile.TemporaryDirectory() as tmp:
        written = generate_reports(bundle, tmp)
        out = Path(tmp)

        check("dashboard was written", (out / "index.html").is_file())
        check(
            "per-submission report was written",
            (out / report_filename("TEAM_001")).is_file(),
        )

        dashboard = (out / "index.html").read_text(encoding="utf-8")
        target = report_filename("TEAM_001")
        check("dashboard references the written page", f'href="{target}"' in dashboard)
        check(
            "referenced page actually exists",
            (out / target).is_file(),
        )
        check("written map includes the dashboard", "dashboard" in written)


def test_number_formatting_is_human_readable() -> None:
    from report_generator import _format_int, _format_seconds

    check("thousands are grouped", _format_int(36866) == "36,866", _format_int(36866))
    check("small numbers unchanged", _format_int(7) == "7", _format_int(7))
    check("millions grouped", _format_int(1234567) == "1,234,567", _format_int(1234567))
    check("non-numeric falls back safely", _format_int("n/a") == "n/a")

    check("sub-second shown in ms", _format_seconds(0.031) == "31.0ms", _format_seconds(0.031))
    check("seconds shown with 2dp", _format_seconds(1.5) == "1.50s", _format_seconds(1.5))
    check("minutes broken out", _format_seconds(95.0) == "1m 35.0s", _format_seconds(95.0))
    check("non-numeric duration falls back", _format_seconds("x") == "x")


def test_dashboard_shows_formatted_cost() -> None:
    records = [
        {
            "submission_id": "TEAM_001",
            "team_name": "Alpha",
            "artifact_type": "skill",
            "total": 0,
            "confidence": "medium",
            "state": "awaiting-judge",
            "human_review_required": False,
            "static_gate": {"passed": True},
            "metrics": {
                "total_elapsed_s": 0.032,
                "total_tokens": {"total_tokens": 36866, "source": "estimated"},
            },
        }
    ]
    cost = {
        "total_elapsed_s": 0.074,
        "total_tokens": 82903,
        "measured_tokens": 0,
        "estimated_tokens": 82903,
    }
    page = render_dashboard(records, generated_at="2026-09-19T00:00:00Z", cost=cost)

    check("row tokens are grouped", "36,866" in page, "not found")
    check("row duration is readable", "32.0ms" in page)
    check("batch total is grouped", "82,903" in page)
    check("measured and estimated are split", "0 measured" in page and "82,903 estimated" in page)


def test_partial_total_excludes_pending_dimensions() -> None:
    from aggregator import compute_partial_total

    # Only D2 scores 5; the rest are pending or zero.
    scores = {"d2_structure_and_conformance": 5}
    pending = [
        "d1_security_and_compliance",
        "d3_code_quality",
        "d4_documentation",
        "d5_testing_and_reliability",
        "d6_business_value",
        "d7_innovation",
    ]
    result = compute_partial_total(scores, DEFAULT_WEIGHTS, pending)

    check("partial is not final while dimensions are pending", result["final"] is False)
    check("pending list is preserved", result["pending_dimensions"] == pending)
    check(
        "a single perfect dimension scores 100 on its own weight",
        result["partial_total"] == 100.0,
        str(result["partial_total"]),
    )

    # With nothing pending, the same input is diluted across all seven.
    complete = compute_partial_total(scores, DEFAULT_WEIGHTS, [])
    check("no pending means final", complete["final"] is True)
    check(
        "final total is diluted by the zero dimensions",
        complete["partial_total"] < result["partial_total"],
        f"{complete['partial_total']} vs {result['partial_total']}",
    )


def test_pending_report_does_not_show_zero_total() -> None:
    """A 0.0 total before judging reads as 'scored zero'. It must not be shown."""
    record = {
        "submission_id": "TEAM_001",
        "team_name": "Alpha",
        "artifact_type": "skill",
        "commit_sha": "a" * 40,
        "state": "awaiting-judge",
        "confidence": "medium",
        "human_review_required": False,
        "total": 0,
        "scores": {"d2_structure_and_conformance": 5},
        "scoring_status": {
            "partial_total": 100.0,
            "final": False,
            "pending_dimensions": ["d3_code_quality", "d6_business_value"],
        },
        "evidence": [],
        "static_gate": {"passed": True, "hard_failed": False, "issues": [], "findings": []},
        "provenance": {
            "rubric_version": "1",
            "prompt_version": "1",
            "model_version": "not-run",
            "scanned_at": "2026-09-19T00:00:00Z",
        },
    }

    page = render_submission_report(record)
    # Target the Total score field specifically: a plain substring check on
    # "0.0 / 100" would also match the legitimate "100.0 / 100" subtotal.
    check(
        "report does not show a bare 0.0 total",
        "<dt>Total score</dt><dd><strong>0.0 / 100</strong></dd>" not in page,
    )
    check(
        "report shows the total as pending",
        "<dt>Total score</dt><dd><strong>Pending judge</strong></dd>" in page,
    )
    check("report says the score is pending", "Pending judge" in page)
    check("report names the awaited dimensions", "d3_code_quality" in page)
    check("report shows the deterministic subtotal", "Deterministic subtotal" in page)


def test_dashboard_marks_pending_scores() -> None:
    records = [
        {
            "submission_id": "TEAM_001",
            "team_name": "Alpha",
            "artifact_type": "skill",
            "total": 0,
            "confidence": "medium",
            "state": "awaiting-judge",
            "human_review_required": False,
            "static_gate": {"passed": True},
            "scoring_status": {"pending_dimensions": ["d3_code_quality"], "final": False},
        }
    ]
    page = render_dashboard(records, generated_at="2026-09-19T00:00:00Z")
    check("dashboard marks the score as pending", '<span class="pending">pending</span>' in page)
    # The score cell specifically: a bare ">0</td>" also matches the Tokens
    # column, which is legitimately zero when no model was called.
    check(
        "dashboard does not show a bare zero in the score column",
        '<td class="num"><span class="pending">pending</span></td>' in page,
    )


def main() -> int:
    test_aggregation_median()
    test_aggregation_agreement()
    test_single_pass_cannot_be_high()
    test_confidence_rules()
    test_weight_loading()
    test_ranking_flags_top_slice_low_confidence()
    test_ranking_excludes_non_scored_submissions()
    test_egress_is_blocked()
    test_report_escapes_hostile_input()
    test_dashboard_renders()
    test_dashboard_links_to_each_report()
    test_report_filename_is_shared()
    test_generate_reports_writes_linked_pages()
    test_number_formatting_is_human_readable()
    test_dashboard_shows_formatted_cost()
    test_partial_total_excludes_pending_dimensions()
    test_pending_report_does_not_show_zero_total()
    test_dashboard_marks_pending_scores()

    print()
    if FAILURES:
        print(f"{len(FAILURES)} test(s) failed: {', '.join(FAILURES)}")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
