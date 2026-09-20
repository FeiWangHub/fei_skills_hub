"""Tests for the efficiency telemetry module.

Run with:
    PYTHONPATH=. python3 tests/test_efficiency.py

Standard library only, matching the rest of the suite.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from efficiency import collect, compare_runs, render_markdown  # noqa: E402

PASSED = 0
FAILED = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"PASS  {label}")
    else:
        FAILED += 1
        print(f"FAIL  {label}  {detail}")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _stage(name, elapsed_s, tokens, source):
    return {
        "name": name,
        "elapsed_ms": elapsed_s * 1000,
        "elapsed_s": elapsed_s,
        "tokens": {
            "prompt_tokens": tokens,
            "completion_tokens": 0,
            "total_tokens": tokens,
            "source": source,
            "model": "",
            "calls": 0,
        },
    }


def _bundle(records, cost=None, generated_at="2026-01-01T00:00:00+00:00"):
    return {
        "state": {"generated_at": generated_at, "total": len(records)},
        "cost": cost or {},
        "results": records,
    }


def _record(sid, *, state="done", agent_span=100.0, program_s=0.01,
            agent_tokens=1000, program_tokens=2000, total=70.0,
            confidence="high", rank=1, evidence=2, review=False,
            provenance=None, bytes_read=10000, source="estimated",
            agent_source="estimated"):
    return {
        "submission_id": sid,
        "state": state,
        "confidence": confidence,
        "rank": rank,
        "human_review_required": review,
        "evidence": [{"file_path": "a", "line_or_range": "1", "note": "n"}] * evidence,
        "scores": {"total": total},
        "static_gate": {"passed": True, "bytes_read": bytes_read, "findings": []},
        "provenance": provenance or {
            "rubric_version": "1", "prompt_version": "1",
            "model_version": "m", "scanned_at": "t",
        },
        "metrics": {
            "total_elapsed_s": program_s,
            "agent_wall_clock_s": agent_span,
            "stages": [
                _stage("classify", 0.0, 0, "none"),
                _stage("static_scan", program_s / 2, program_tokens, source),
                _stage("judge_wall_clock", agent_span, agent_tokens, agent_source),
            ],
        },
    }


def test_missing_run_raises() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        try:
            collect(tmp)
            check("missing run raises FileNotFoundError", False)
        except FileNotFoundError:
            check("missing run raises FileNotFoundError", True)


def test_totals_split_program_and_agent() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        _write(out / "execution-state.json", json.dumps(_bundle([_record("T1")])))
        report = collect(out)

        check("program tokens counted", report["tokens"]["program"] == 2000, str(report["tokens"]))
        check("agent tokens counted", report["tokens"]["agent"] == 1000)
        check("total tokens summed", report["tokens"]["total"] == 3000)
        check("program time recorded", report["wall_clock"]["program_s"] == 0.01)
        check("agent span recorded", report["wall_clock"]["agent_s"] == 100.0)
        check("end to end summed", report["wall_clock"]["end_to_end_s"] == 100.01)


def test_agent_span_is_not_multiplied_by_cohort() -> None:
    """merge stamps one prepare->merge span on every record.

    Summing it per record would report 3x the real elapsed time. The report
    must take the maximum instead, and must flag the condition.
    """
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        records = [_record(f"T{i}", agent_span=161.377) for i in range(3)]
        _write(out / "execution-state.json", json.dumps(_bundle(records)))
        report = collect(out)

        check(
            "agent span is not tripled",
            report["wall_clock"]["agent_s"] == 161.377,
            str(report["wall_clock"]["agent_s"]),
        )
        check(
            "shared span is flagged in data_quality",
            any("shared span" in f or "prepare->merge span" in f for f in report["data_quality"]),
            str(report["data_quality"]),
        )
        check(
            "shared span is flagged in the report body",
            report["wall_clock"]["agent_span_is_shared"] is True,
        )


def test_measured_is_never_conflated_with_estimated() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        _write(out / "execution-state.json", json.dumps(_bundle([_record("T1")])))
        report = collect(out)

        check("no measured tokens", report["tokens"]["measured"] == 0)
        check("all estimated", report["tokens"]["estimated"] == 3000)
        check(
            "unmeasured usage raises a flag",
            any("no measured token usage" in f for f in report["data_quality"]),
            str(report["data_quality"]),
        )


def test_measured_usage_clears_the_flag() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        record = _record("T1", agent_source="measured", agent_tokens=5000)
        _write(out / "execution-state.json", json.dumps(_bundle([record])))
        report = collect(out)

        check("measured tokens reported", report["tokens"]["measured"] == 5000)
        check(
            "no unmeasured flag when usage was reported",
            not any("no measured token usage" in f for f in report["data_quality"]),
            str(report["data_quality"]),
        )


def test_unversioned_provenance_is_flagged() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        record = _record("T1", provenance={
            "rubric_version": "unversioned", "prompt_version": "unversioned",
            "model_version": "not-run", "scanned_at": "t",
        })
        _write(out / "execution-state.json", json.dumps(_bundle([record])))
        report = collect(out)

        check(
            "unversioned provenance raises a flag",
            any("unversioned" in f for f in report["data_quality"]),
            str(report["data_quality"]),
        )


def test_dispatch_shape_from_run_meta() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        _write(out / "execution-state.json", json.dumps(_bundle([_record("T1")])))
        _write(out / "run-meta.json", json.dumps({
            "mode": "agent", "scorers": 3, "batches": 3, "re_dispatches": 1,
        }))
        report = collect(out)

        check("mode read from run-meta", report["run"]["mode"] == "agent")
        check("scorer count read", report["dispatch"]["scorers"] == 3)
        check("re-dispatches read", report["dispatch"]["re_dispatches"] == 1)
        check(
            "no dispatch flag when recorded",
            not any("dispatch shape not recorded" in f for f in report["data_quality"]),
            str(report["data_quality"]),
        )


def test_missing_run_meta_is_flagged() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        _write(out / "execution-state.json", json.dumps(_bundle([_record("T1")])))
        report = collect(out)

        check("scorers unrecorded", report["dispatch"]["scorers"] == "not recorded")
        check(
            "missing dispatch shape raises a flag",
            any("dispatch shape not recorded" in f for f in report["data_quality"]),
            str(report["data_quality"]),
        )


def test_cohort_counts() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        records = [
            _record("T1"),
            _record("T2", state="hard-failed", rank=None, total=0.0),
            _record("T3", state="awaiting-judge", rank=None, total=0.0),
        ]
        _write(out / "execution-state.json", json.dumps(_bundle(records)))
        report = collect(out)

        check("submission count", report["cohort"]["submissions"] == 3)
        check("done count", report["cohort"]["done"] == 1)
        check("hard-failed count", report["cohort"]["hard_failed"] == 1)
        check("awaiting-judge count", report["cohort"]["awaiting_judge"] == 1)
        check("ranked count", report["cohort"]["scored"] == 1)
        check(
            "awaiting judge raises a flag",
            any("awaiting the judge" in f for f in report["data_quality"]),
            str(report["data_quality"]),
        )


def test_quality_metrics() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        records = [_record("T1", total=80.0), _record("T2", total=60.0)]
        _write(out / "execution-state.json", json.dumps(_bundle(records)))
        report = collect(out)

        check("mean total", report["quality"]["mean_total"] == 70.0)
        check("min total", report["quality"]["min_total"] == 60.0)
        check("max total", report["quality"]["max_total"] == 80.0)
        check("evidence summed", report["quality"]["evidence_items_total"] == 4)


def test_render_markdown_has_the_headline_blocks() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        _write(out / "execution-state.json", json.dumps(_bundle([_record("T1")])))
        text = render_markdown(collect(out, mode="skill", label="demo"))

        for heading in ("## Time", "## Tokens", "## Deterministic share",
                        "## Dispatch", "## Cohort and quality"):
            check(f"markdown has {heading}", heading in text)
        check("label appears", "demo" in text)
        check("mode appears", "skill" in text)
        check("flags section rendered", "## Data quality flags" in text)


def test_compare_warns_on_different_cohort_sizes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        a, b = Path(tmp) / "a", Path(tmp) / "b"
        _write(a / "execution-state.json", json.dumps(_bundle([_record("T1")])))
        _write(b / "execution-state.json",
               json.dumps(_bundle([_record("T1"), _record("T2"), _record("T3")])))

        text = compare_runs(collect(a), collect(b))
        check("cohort mismatch warned", "Not comparable" in text)


def test_compare_warns_when_nothing_was_measured() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        a, b = Path(tmp) / "a", Path(tmp) / "b"
        _write(a / "execution-state.json", json.dumps(_bundle([_record("T1")])))
        _write(b / "execution-state.json", json.dumps(_bundle([_record("T1")])))

        text = compare_runs(collect(a), collect(b))
        check("unmeasured comparison warned", "Neither run captured measured" in text)
        check("delta table present", "| Metric | Baseline | Variant | Change |" in text)


def test_compare_does_not_print_a_winner() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        a, b = Path(tmp) / "a", Path(tmp) / "b"
        _write(a / "execution-state.json", json.dumps(_bundle([_record("T1")])))
        _write(b / "execution-state.json", json.dumps(_bundle([_record("T1")])))

        text = compare_runs(collect(a), collect(b)).lower()
        check("no winner verdict", "winner" not in text or "not an efficiency" in text)


def test_other_stage_elapsed_is_summed() -> None:
    """Non-agent stages are real per-submission compute and must be summed."""
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        records = [_record(f"T{i}", program_s=0.01) for i in range(3)]
        _write(out / "execution-state.json", json.dumps(_bundle(records)))
        report = collect(out)

        check(
            "program time is summed across submissions",
            report["wall_clock"]["program_s"] == 0.03,
            str(report["wall_clock"]["program_s"]),
        )
        check(
            "static_scan stage is not flagged as a span",
            report["tokens"]["by_stage"]["static_scan"]["elapsed_s"] == 0.015,
            str(report["tokens"]["by_stage"]["static_scan"]),
        )


def main() -> None:
    tests = [
        test_missing_run_raises,
        test_totals_split_program_and_agent,
        test_agent_span_is_not_multiplied_by_cohort,
        test_measured_is_never_conflated_with_estimated,
        test_measured_usage_clears_the_flag,
        test_unversioned_provenance_is_flagged,
        test_dispatch_shape_from_run_meta,
        test_missing_run_meta_is_flagged,
        test_cohort_counts,
        test_quality_metrics,
        test_render_markdown_has_the_headline_blocks,
        test_compare_warns_on_different_cohort_sizes,
        test_compare_warns_when_nothing_was_measured,
        test_compare_does_not_print_a_winner,
        test_other_stage_elapsed_is_summed,
    ]
    for test in tests:
        test()

    print()
    if FAILED:
        print(f"{FAILED} check(s) failed, {PASSED} passed.")
        raise SystemExit(1)
    print("All checks passed.")


if __name__ == "__main__":
    main()
