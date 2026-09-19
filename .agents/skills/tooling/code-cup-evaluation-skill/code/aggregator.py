"""Deterministic score aggregation for Code Cup evaluation.

Design stance:
- the orchestrator owns all arithmetic; the judge never computes a total
- weights live in config, not in the model
- two judge passes are reconciled by median, and disagreement lowers confidence

This module performs no network calls and never executes submitted code.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

SCORE_KEYS = (
    "d1_security_and_compliance",
    "d2_structure_and_conformance",
    "d3_code_quality",
    "d4_documentation",
    "d5_testing_and_reliability",
    "d6_business_value",
    "d7_innovation",
)

CONFIDENCE_HIGH = "high"
CONFIDENCE_MEDIUM = "medium"
CONFIDENCE_LOW = "low"

DEFAULT_WEIGHTS: dict[str, float] = {
    "d1_security_and_compliance": 1 / 7,
    "d2_structure_and_conformance": 1 / 7,
    "d3_code_quality": 1 / 7,
    "d4_documentation": 1 / 7,
    "d5_testing_and_reliability": 1 / 7,
    "d6_business_value": 1 / 7,
    "d7_innovation": 1 / 7,
}


@dataclass
class AggregatedScore:
    scores: dict[str, float]
    total: float
    confidence: str
    spread: int
    human_review_required: bool
    evidence: list[dict[str, str]]

    def as_dict(self) -> dict[str, object]:
        return {
            "scores": self.scores,
            "total": self.total,
            "confidence": self.confidence,
            "spread": self.spread,
            "human_review_required": self.human_review_required,
            "evidence": self.evidence,
        }


def load_weights(path: str | Path, artifact_type: str) -> dict[str, float]:
    """Load per-artifact weights from a local rubric file.

    Falls back to an equal weighting if the rubric or artifact entry is absent,
    so a missing config degrades predictably rather than crashing a batch run.
    """
    rubric_path = Path(path)
    if not rubric_path.exists():
        return dict(DEFAULT_WEIGHTS)

    try:
        import yaml  # type: ignore

        data = yaml.safe_load(rubric_path.read_text(encoding="utf-8")) or {}
    except ImportError:
        try:
            data = json.loads(rubric_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return dict(DEFAULT_WEIGHTS)
    except Exception:
        return dict(DEFAULT_WEIGHTS)

    entry = (data.get("artifact_types") or {}).get(artifact_type) or {}
    weights = entry.get("weights") or {}

    resolved = {key: float(weights.get(key, DEFAULT_WEIGHTS[key])) for key in SCORE_KEYS}

    total = sum(resolved.values())
    if total <= 0:
        return dict(DEFAULT_WEIGHTS)

    return {key: value / total for key, value in resolved.items()}


def _median(values: list[int]) -> float:
    ordered = sorted(values)
    count = len(ordered)
    if count == 0:
        return 0.0
    middle = count // 2
    if count % 2 == 1:
        return float(ordered[middle])
    return (ordered[middle - 1] + ordered[middle]) / 2


def reconcile_passes(passes: list[dict[str, object]]) -> tuple[dict[str, float], int, list[dict[str, str]]]:
    """Combine one or more judge passes by per-dimension median.

    Returns the reconciled per-dimension scores, the maximum per-dimension
    spread across passes, and the union of cited evidence.
    """
    if not passes:
        raise ValueError("reconcile_passes requires at least one judge pass")

    reconciled: dict[str, float] = {}
    max_spread = 0

    for key in SCORE_KEYS:
        values = [int(p["scores"][key]) for p in passes]  # type: ignore[index]
        reconciled[key] = _median(values)
        max_spread = max(max_spread, max(values) - min(values))

    evidence: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in passes:
        for entry in item.get("evidence", []) or []:  # type: ignore[union-attr]
            marker = (str(entry.get("file_path", "")), str(entry.get("line_or_range", "")))
            if marker in seen:
                continue
            seen.add(marker)
            evidence.append(
                {
                    "file_path": str(entry.get("file_path", "")),
                    "line_or_range": str(entry.get("line_or_range", "")),
                    "note": str(entry.get("note", "")),
                }
            )

    return reconciled, max_spread, evidence


def derive_confidence(spread: int, pass_count: int, review_findings: int) -> str:
    """Map judge disagreement and static findings onto a confidence label.

    A single pass cannot demonstrate agreement, so it can never be `high`.
    """
    if spread > 1:
        return CONFIDENCE_LOW
    if spread == 1:
        return CONFIDENCE_MEDIUM
    if pass_count < 2:
        return CONFIDENCE_MEDIUM
    if review_findings > 2:
        return CONFIDENCE_MEDIUM
    return CONFIDENCE_HIGH


def aggregate(
    passes: list[dict[str, object]],
    weights: dict[str, float],
    review_findings: int = 0,
) -> AggregatedScore:
    """Aggregate judge passes into a final anchored score.

    Judge bands are 1/3/5. The weighted mean is projected onto a 0-100 scale
    so the leaderboard stays readable while the underlying scale stays anchored.
    """
    reconciled, spread, evidence = reconcile_passes(passes)
    confidence = derive_confidence(spread, len(passes), review_findings)

    weighted = sum(reconciled[key] * weights.get(key, 0.0) for key in SCORE_KEYS)
    total = round((weighted / 5.0) * 100, 2)

    return AggregatedScore(
        scores={key: reconciled[key] for key in SCORE_KEYS},
        total=total,
        confidence=confidence,
        spread=spread,
        human_review_required=confidence == CONFIDENCE_LOW,
        evidence=evidence,
    )


NON_SCORED_STATES = {"hard-failed", "failed"}


def _is_scored(record: dict[str, object]) -> bool:
    """A record only counts as scored once the judge has produced a total.

    Hard-failed and failed submissions are excluded from ranking and from the
    top-slice review rule, so a blocked submission can never be presented as a
    high-ranking entry awaiting manual review.
    """
    if str(record.get("state", "")) in NON_SCORED_STATES:
        return False
    return float(record.get("total", 0) or 0) > 0


def rank_results(results: list[dict[str, object]]) -> list[dict[str, object]]:
    """Sort results by total descending, then by submission_id for stability.

    Scored submissions are ranked first. Low-confidence scored results that land
    in the top slice are flagged for review, so an uncertain score can never
    silently decide a prize. Non-scored submissions are ordered last and are
    never assigned a rank.
    """
    scored = [r for r in results if _is_scored(r)]
    unscored = [r for r in results if not _is_scored(r)]

    scored.sort(key=lambda r: (-float(r.get("total", 0) or 0), str(r.get("submission_id", ""))))
    unscored.sort(key=lambda r: str(r.get("submission_id", "")))

    ranked = scored + unscored

    top_slice = max(1, int(len(scored) * 0.1)) if scored else 0
    for index, record in enumerate(ranked):
        if index < len(scored):
            record["rank"] = index + 1
            if index < top_slice and record.get("confidence") == CONFIDENCE_LOW:
                record["human_review_required"] = True
                record["review_reason"] = "low confidence within the top-ranked slice"
        else:
            record.pop("rank", None)

    return ranked
