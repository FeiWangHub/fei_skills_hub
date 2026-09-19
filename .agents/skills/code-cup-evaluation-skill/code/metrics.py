"""Timing and token accounting for the Code Cup evaluation pipeline.

Purpose: make each scoring run measurable so variants can be compared.

Two kinds of number are recorded, and they are never conflated:

- **Measured** — wall-clock elapsed time, and token counts reported by the
  inference endpoint in its `usage` field. These are facts.
- **Estimated** — token counts for stages that never call a model (the static
  scanner, the deterministic scorer). A character-based heuristic is used, and
  every estimate is tagged `estimated` so it can never be mistaken for provider
  usage.

An LLM token count of `0` with `source: "measured"` is a real zero: the stage
ran and made no model call. Anything else is labelled.

This module performs no network calls.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterator

SOURCE_MEASURED = "measured"
SOURCE_ESTIMATED = "estimated"
SOURCE_NONE = "none"

# Rough characters-per-token ratio for English prose plus code. Only ever used
# for stages that make no model call, and always flagged as an estimate.
CHARS_PER_TOKEN = 4.0


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    source: str = SOURCE_NONE
    model: str = ""
    calls: int = 0

    def as_dict(self) -> dict[str, object]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "source": self.source,
            "model": self.model,
            "calls": self.calls,
        }

    @classmethod
    def unavailable(cls) -> "TokenUsage":
        """No model call was made, so no token figure exists."""
        return cls(0, 0, 0, SOURCE_NONE, "", 0)

    @classmethod
    def estimated_from_text(cls, text: str) -> "TokenUsage":
        """Heuristic token count for a stage that did not call a model."""
        char_count = len(text or "")
        tokens = int(char_count / CHARS_PER_TOKEN)
        return cls(tokens, 0, tokens, SOURCE_ESTIMATED, "", 0)

    @classmethod
    def from_provider_usage(cls, usage: dict[str, object], model: str) -> "TokenUsage":
        """Build usage from an endpoint's reported `usage` object."""
        def _int(key: str) -> int:
            value = usage.get(key, 0)
            try:
                return int(value)  # type: ignore[arg-type]
            except (TypeError, ValueError):
                return 0

        prompt = _int("prompt_tokens")
        completion = _int("completion_tokens")
        total = _int("total_tokens") or (prompt + completion)

        return cls(prompt, completion, total, SOURCE_MEASURED, model, 1)

    def merge(self, other: "TokenUsage") -> "TokenUsage":
        """Combine two usage records, keeping the weaker evidence source."""
        # If either is measured the total is partly measured; report `measured`
        # only when both sides are, so the label always reflects the weakest link.
        if self.source == SOURCE_MEASURED and other.source == SOURCE_MEASURED:
            source = SOURCE_MEASURED
        elif SOURCE_ESTIMATED in (self.source, other.source):
            source = SOURCE_ESTIMATED
        elif SOURCE_NONE in (self.source, other.source):
            source = SOURCE_ESTIMATED if (self.total_tokens or other.total_tokens) else SOURCE_NONE
        else:
            source = other.source

        return TokenUsage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
            source=source,
            model=self.model or other.model,
            calls=self.calls + other.calls,
        )


@dataclass
class StageMetric:
    name: str
    elapsed_ms: float
    tokens: TokenUsage = field(default_factory=TokenUsage.unavailable)

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "elapsed_ms": round(self.elapsed_ms, 2),
            "elapsed_s": round(self.elapsed_ms / 1000.0, 3),
            "tokens": self.tokens.as_dict(),
        }


@dataclass
class RunMetrics:
    stages: list[StageMetric] = field(default_factory=list)

    def add(self, metric: StageMetric) -> None:
        self.stages.append(metric)

    @property
    def total_elapsed_ms(self) -> float:
        return sum(stage.elapsed_ms for stage in self.stages)

    def total_tokens(self) -> TokenUsage:
        totals = TokenUsage.unavailable()
        for stage in self.stages:
            totals = totals.merge(stage.tokens)
        return totals

    def as_dict(self) -> dict[str, object]:
        return {
            "total_elapsed_ms": round(self.total_elapsed_ms, 2),
            "total_elapsed_s": round(self.total_elapsed_ms / 1000.0, 3),
            "total_tokens": self.total_tokens().as_dict(),
            "stages": [stage.as_dict() for stage in self.stages],
        }


@contextmanager
def timed_stage(
    metrics: RunMetrics,
    name: str,
    tokens: TokenUsage | None = None,
) -> Iterator[None]:
    """Record the elapsed time of a pipeline stage.

    `tokens` is captured before the block runs; pass a mutable holder if the
    value is only known afterwards.
    """
    started = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        metrics.add(StageMetric(name, elapsed_ms, tokens or TokenUsage.unavailable()))


def summarize(metrics_list: list[dict[str, object]]) -> dict[str, object]:
    """Aggregate per-submission metrics for a batch comparison.

    Measured and estimated token amounts are summed by *stage*, not by the
    submission's merged label. A submission whose total is labelled
    `estimated` because one stage was heuristic may still contain genuinely
    measured tokens from another stage; bucketing the whole total by the
    weakest label would hide them.
    """
    total_ms = 0.0
    total_tokens = 0
    measured_tokens = 0
    estimated_tokens = 0

    for metrics in metrics_list:
        total_ms += float(metrics.get("total_elapsed_ms", 0) or 0)

        stages = metrics.get("stages")
        if isinstance(stages, list) and stages:
            for stage in stages:
                if not isinstance(stage, dict):
                    continue
                tokens = stage.get("tokens") or {}
                amount = int(tokens.get("total_tokens", 0) or 0)
                total_tokens += amount
                if tokens.get("source") == SOURCE_MEASURED:
                    measured_tokens += amount
                elif tokens.get("source") == SOURCE_ESTIMATED:
                    estimated_tokens += amount
        else:
            # No stage detail: fall back to the merged total.
            tokens = metrics.get("total_tokens") or {}
            amount = int(tokens.get("total_tokens", 0) or 0)
            total_tokens += amount
            if tokens.get("source") == SOURCE_MEASURED:
                measured_tokens += amount
            elif tokens.get("source") == SOURCE_ESTIMATED:
                estimated_tokens += amount

    count = len(metrics_list)
    return {
        "submissions": count,
        "total_elapsed_ms": round(total_ms, 2),
        "total_elapsed_s": round(total_ms / 1000.0, 3),
        "mean_elapsed_ms": round(total_ms / count, 2) if count else 0.0,
        "total_tokens": total_tokens,
        "measured_tokens": measured_tokens,
        "estimated_tokens": estimated_tokens,
        "note": (
            "measured_tokens were reported by the model/endpoint; "
            "estimated_tokens are a character heuristic for stages that call no model"
        ),
    }
