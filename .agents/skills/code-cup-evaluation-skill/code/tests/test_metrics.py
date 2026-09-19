"""Tests for timing and token accounting.

Run with:
    PYTHONPATH=. python3 tests/test_metrics.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from judge_transport import default_usage_parser  # noqa: E402
from metrics import (  # noqa: E402
    SOURCE_ESTIMATED,
    SOURCE_MEASURED,
    SOURCE_NONE,
    RunMetrics,
    TokenUsage,
    summarize,
    timed_stage,
)

FAILURES: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"PASS  {label}")
    else:
        print(f"FAIL  {label} {detail}")
        FAILURES.append(label)


def test_timed_stage_measures_elapsed() -> None:
    metrics = RunMetrics()
    with timed_stage(metrics, "slow"):
        time.sleep(0.05)

    check("stage was recorded", len(metrics.stages) == 1)
    elapsed = metrics.stages[0].elapsed_ms
    check("elapsed is at least the sleep", elapsed >= 50.0, str(elapsed))
    check("elapsed is plausible", elapsed < 1000.0, str(elapsed))
    check("stage name is kept", metrics.stages[0].name == "slow")


def test_unavailable_usage_is_not_zero_measured() -> None:
    usage = TokenUsage.unavailable()
    check("unavailable total is 0", usage.total_tokens == 0)
    check(
        "unavailable is labelled none, not measured",
        usage.source == SOURCE_NONE,
        usage.source,
    )


def test_estimated_usage_is_labelled() -> None:
    usage = TokenUsage.estimated_from_text("x" * 400)
    check("estimate scales with length", usage.total_tokens == 100, str(usage.total_tokens))
    check(
        "estimate is labelled estimated",
        usage.source == SOURCE_ESTIMATED,
        usage.source,
    )
    check("estimate makes no model calls", usage.calls == 0)


def test_provider_usage_is_measured() -> None:
    usage = TokenUsage.from_provider_usage(
        {"prompt_tokens": 1200, "completion_tokens": 300, "total_tokens": 1500},
        model="internal-judge-v1",
    )
    check("prompt tokens captured", usage.prompt_tokens == 1200)
    check("completion tokens captured", usage.completion_tokens == 300)
    check("total captured", usage.total_tokens == 1500)
    check("source is measured", usage.source == SOURCE_MEASURED, usage.source)
    check("model is recorded", usage.model == "internal-judge-v1")
    check("call count is one", usage.calls == 1)


def test_provider_usage_derives_total_when_absent() -> None:
    usage = TokenUsage.from_provider_usage(
        {"prompt_tokens": "10", "completion_tokens": "5"}, model="m"
    )
    check("total is derived from parts", usage.total_tokens == 15, str(usage.total_tokens))

    empty = TokenUsage.from_provider_usage({}, model="m")
    check("empty usage yields zero", empty.total_tokens == 0)


def test_merge_keeps_weakest_source() -> None:
    measured = TokenUsage.from_provider_usage(
        {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}, model="m"
    )
    estimated = TokenUsage.estimated_from_text("y" * 400)

    both = measured.merge(measured)
    check("measured + measured stays measured", both.source == SOURCE_MEASURED, both.source)
    check("totals add up", both.total_tokens == 300, str(both.total_tokens))
    check("call counts add up", both.calls == 2, str(both.calls))

    mixed = measured.merge(estimated)
    check(
        "measured + estimated degrades to estimated",
        mixed.source == SOURCE_ESTIMATED,
        mixed.source,
    )


def test_run_metrics_totals() -> None:
    metrics = RunMetrics()
    with timed_stage(metrics, "a"):
        time.sleep(0.01)
    with timed_stage(metrics, "b"):
        time.sleep(0.01)

    total = metrics.total_elapsed_ms
    check("two stages recorded", len(metrics.stages) == 2)
    check("total is the sum of stages", abs(total - sum(s.elapsed_ms for s in metrics.stages)) < 1e-6)
    check("total is at least 20ms", total >= 20.0, str(total))

    payload = metrics.as_dict()
    check("serialised payload has stages", len(payload["stages"]) == 2)
    check("serialised payload has total seconds", "total_elapsed_s" in payload)


def test_summarize_separates_measured_and_estimated() -> None:
    metrics_a = {
        "total_elapsed_ms": 100.0,
        "total_tokens": {
            "total_tokens": 1500,
            "source": SOURCE_MEASURED,
        },
    }
    metrics_b = {
        "total_elapsed_ms": 200.0,
        "total_tokens": {
            "total_tokens": 400,
            "source": SOURCE_ESTIMATED,
        },
    }

    summary = summarize([metrics_a, metrics_b])
    check("submission count", summary["submissions"] == 2)
    check("elapsed totals", summary["total_elapsed_ms"] == 300.0, str(summary["total_elapsed_ms"]))
    check("mean elapsed", summary["mean_elapsed_ms"] == 150.0, str(summary["mean_elapsed_ms"]))
    check("total tokens", summary["total_tokens"] == 1900, str(summary["total_tokens"]))
    check(
        "measured tokens reported separately",
        summary["measured_tokens"] == 1500,
        str(summary["measured_tokens"]),
    )
    check(
        "estimated tokens reported separately",
        summary["estimated_tokens"] == 400,
        str(summary["estimated_tokens"]),
    )
    check("summarize handles an empty batch", summarize([])["submissions"] == 0)


def test_usage_parser_distinguishes_absent_from_zero() -> None:
    reported = default_usage_parser(
        {"usage": {"prompt_tokens": 5, "completion_tokens": 1, "total_tokens": 6}}
    )
    check("reported usage is returned", reported.get("total_tokens") == 6)

    absent = default_usage_parser({"choices": []})
    check("absent usage yields an empty mapping", absent == {}, str(absent))


def test_no_model_call_means_no_measured_tokens() -> None:
    """The pipeline's current deterministic stages must never claim LLM usage."""
    metrics = RunMetrics()
    with timed_stage(metrics, "static_scan"):
        time.sleep(0.01)

    payload = metrics.as_dict()
    tokens = payload["total_tokens"]
    check(
        "a run with no judge call reports source none",
        tokens["source"] == SOURCE_NONE,
        str(tokens),
    )
    check("and zero tokens", tokens["total_tokens"] == 0, str(tokens))
    check("and zero calls", tokens["calls"] == 0, str(tokens))


def main() -> int:
    test_timed_stage_measures_elapsed()
    test_unavailable_usage_is_not_zero_measured()
    test_estimated_usage_is_labelled()
    test_provider_usage_is_measured()
    test_provider_usage_derives_total_when_absent()
    test_merge_keeps_weakest_source()
    test_run_metrics_totals()
    test_summarize_separates_measured_and_estimated()
    test_usage_parser_distinguishes_absent_from_zero()
    test_no_model_call_means_no_measured_tokens()

    print()
    if FAILURES:
        print(f"{len(FAILURES)} test(s) failed: {', '.join(FAILURES)}")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
