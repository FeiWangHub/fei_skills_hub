"""Deterministic dimension scoring for Code Cup evaluation.

This module implements the "deterministic-first" design stance: the dimensions
that can be judged from repository facts alone are scored here, with no LLM
involvement. Only genuinely qualitative dimensions are left to the judge.

Dimensions scored deterministically:

- D1 Security and compliance      — from the static gate findings
- D2 Standards and structure      — from artifact conformance markers
- D4 Documentation                — from documentation presence and depth
- D5 Testing and reliability      — from test presence and count

Dimensions left to the LLM judge:

- D3 Code and content quality     — requires judgement
- D6 Business value and impact    — requires judgement
- D7 Innovation and differentiation — requires judgement

Every deterministic score carries evidence, so the merged result satisfies the
same evidence contract the judge must meet.

This module performs no network calls and never executes submitted code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

BAND_WEAK = 1
BAND_ACCEPTABLE = 3
BAND_STRONG = 5

DETERMINISTIC_DIMENSIONS = (
    "d1_security_and_compliance",
    "d2_structure_and_conformance",
    "d4_documentation",
    "d5_testing_and_reliability",
)

JUDGE_ONLY_DIMENSIONS = (
    "d3_code_quality",
    "d6_business_value",
    "d7_innovation",
)

DOC_EXTENSIONS = {".md", ".rst", ".adoc", ".txt"}
SKIP_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".venv",
    "venv",
    "__pycache__",
    ".next",
    "target",
}

TEST_PATH_HINTS = (
    "test/",
    "tests/",
    "spec/",
    "__tests__/",
    "test_",
    "_test.",
    ".test.",
    ".spec.",
    "test.java",
    "tests.py",
    "conftest.py",
)

REQUIRED_FOR_ARTIFACT = {
    "skill": ("SKILL.md", "skill.md"),
    "copilot_agent": (".github/agents",),
    "opencode_agent": ("opencode.json", "opencode.jsonc", ".opencode"),
    "source_project": (),
}


@dataclass
class DimensionScore:
    band: int
    evidence: list[dict[str, str]] = field(default_factory=list)
    rationale: str = ""


@dataclass
class DeterministicResult:
    scores: dict[str, int] = field(default_factory=dict)
    evidence: list[dict[str, str]] = field(default_factory=list)
    rationales: dict[str, str] = field(default_factory=dict)
    judge_dimensions: tuple[str, ...] = JUDGE_ONLY_DIMENSIONS

    def as_dict(self) -> dict[str, object]:
        return {
            "scores": self.scores,
            "evidence": self.evidence,
            "rationales": self.rationales,
            "judge_dimensions": list(self.judge_dimensions),
        }


def _iter_files(root: Path):
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file():
            yield path


def _rel(root: Path, path: Path) -> str:
    return str(path.relative_to(root))


def _evidence(file_path: str, line_or_range: str, note: str) -> dict[str, str]:
    return {"file_path": file_path, "line_or_range": line_or_range, "note": note}


def score_security(findings: list[dict[str, object]]) -> DimensionScore:
    """D1: driven by the static gate. A hard failure is already fatal upstream."""
    hard_fail = [f for f in findings if f.get("severity") == "hard_fail"]
    review = [f for f in findings if f.get("severity") == "review"]

    if hard_fail:
        return DimensionScore(
            BAND_WEAK,
            [
                _evidence(
                    str(f.get("file_path", "")),
                    str(f.get("line", "")),
                    f"hard-fail finding: {f.get('category')}",
                )
                for f in hard_fail[:5]
            ],
            f"{len(hard_fail)} hard-fail finding(s) present",
        )

    if review:
        return DimensionScore(
            BAND_ACCEPTABLE,
            [
                _evidence(
                    str(f.get("file_path", "")),
                    str(f.get("line", "")),
                    f"flagged for review: {f.get('category')}",
                )
                for f in review[:5]
            ],
            f"{len(review)} review-level finding(s) present",
        )

    return DimensionScore(
        BAND_STRONG,
        [_evidence("(repository)", "-", "static gate passed with no findings")],
        "no security findings from the static gate",
    )


def score_structure(root: Path, artifact_type: str) -> DimensionScore:
    """D2: artifact conformance against the declared type."""
    required = REQUIRED_FOR_ARTIFACT.get(artifact_type, ())

    if not required:
        return DimensionScore(
            BAND_ACCEPTABLE,
            [_evidence("(repository)", "-", "source project: no fixed artifact shape required")],
            "source project has no mandated artifact structure",
        )

    present = [marker for marker in required if (root / marker).exists()]

    if present:
        return DimensionScore(
            BAND_STRONG,
            [_evidence(marker, "-", f"required {artifact_type} marker present") for marker in present],
            f"declared structure present for {artifact_type}",
        )

    return DimensionScore(
        BAND_WEAK,
        [_evidence("(repository)", "-", f"no {artifact_type} marker found")],
        f"declared artifact type {artifact_type} is not reflected in the repository",
    )


def score_documentation(root: Path) -> DimensionScore:
    """D4: documentation presence and depth."""
    docs = []
    for path in _iter_files(root):
        if path.suffix.lower() in DOC_EXTENSIONS:
            docs.append(path)

    if not docs:
        return DimensionScore(
            BAND_WEAK,
            [_evidence("(repository)", "-", "no documentation files found")],
            "no documentation of any kind",
        )

    readme = [p for p in docs if p.name.lower().startswith("readme")]
    total_bytes = sum(p.stat().st_size for p in docs if p.stat().st_size < 2_000_000)

    evidence = [
        _evidence(_rel(root, p), "-", "documentation file") for p in (readme or docs)[:5]
    ]

    if readme and total_bytes >= 2000:
        return DimensionScore(
            BAND_STRONG, evidence, f"README present with {len(docs)} doc file(s), {total_bytes} bytes"
        )

    if readme or total_bytes >= 500:
        return DimensionScore(
            BAND_ACCEPTABLE, evidence, f"{len(docs)} doc file(s), {total_bytes} bytes"
        )

    return DimensionScore(
        BAND_WEAK, evidence, f"minimal documentation: {len(docs)} file(s), {total_bytes} bytes"
    )


def score_testing(root: Path) -> DimensionScore:
    """D5: test presence and breadth."""
    test_files = []
    for path in _iter_files(root):
        rel = _rel(root, path).lower()
        if any(hint in rel for hint in TEST_PATH_HINTS):
            test_files.append(path)

    if not test_files:
        return DimensionScore(
            BAND_WEAK,
            [_evidence("(repository)", "-", "no test files detected")],
            "no tests detected",
        )

    evidence = [
        _evidence(_rel(root, p), "-", "test file") for p in test_files[:5]
    ]

    if len(test_files) >= 5:
        return DimensionScore(
            BAND_STRONG, evidence, f"{len(test_files)} test file(s) detected"
        )

    return DimensionScore(
        BAND_ACCEPTABLE, evidence, f"{len(test_files)} test file(s) detected"
    )


def score_deterministic(
    root: str | Path,
    artifact_type: str,
    findings: list[dict[str, object]],
) -> DeterministicResult:
    """Score every dimension that does not require judgement."""
    root_path = Path(root)
    if not root_path.exists():
        raise FileNotFoundError(f"Repository path not found: {root_path}")

    scorers = {
        "d1_security_and_compliance": lambda: score_security(findings),
        "d2_structure_and_conformance": lambda: score_structure(root_path, artifact_type),
        "d4_documentation": lambda: score_documentation(root_path),
        "d5_testing_and_reliability": lambda: score_testing(root_path),
    }

    result = DeterministicResult()

    for key, scorer in scorers.items():
        scored = scorer()
        result.scores[key] = scored.band
        result.rationales[key] = scored.rationale
        result.evidence.extend(scored.evidence)

    return result
