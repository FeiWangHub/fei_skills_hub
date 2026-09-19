"""Tests for the deterministic dimension scorer.

Run with:
    PYTHONPATH=. python3 tests/test_deterministic_scorer.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from deterministic_scorer import (  # noqa: E402
    BAND_ACCEPTABLE,
    BAND_STRONG,
    BAND_WEAK,
    DETERMINISTIC_DIMENSIONS,
    JUDGE_ONLY_DIMENSIONS,
    score_deterministic,
    score_documentation,
    score_security,
    score_structure,
    score_testing,
)

FAILURES: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"PASS  {label}")
    else:
        print(f"FAIL  {label} {detail}")
        FAILURES.append(label)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_security_dimension() -> None:
    clean = score_security([])
    check("clean gate scores strong on D1", clean.band == BAND_STRONG, str(clean.band))
    check("clean D1 still cites evidence", len(clean.evidence) > 0)

    review = score_security(
        [{"severity": "review", "category": "injection:x", "file_path": "a.md", "line": 3}]
    )
    check("review finding caps D1 at acceptable", review.band == BAND_ACCEPTABLE, str(review.band))

    hard = score_security(
        [{"severity": "hard_fail", "category": "secret:aws", "file_path": "c.py", "line": 1}]
    )
    check("hard fail forces D1 to weak", hard.band == BAND_WEAK, str(hard.band))


def test_structure_dimension() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "SKILL.md", "# skill\n")
        scored = score_structure(root, "skill")
        check("skill with SKILL.md scores strong on D2", scored.band == BAND_STRONG, str(scored.band))

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "main.py", "print(1)\n")
        scored = score_structure(root, "skill")
        check("skill without marker scores weak on D2", scored.band == BAND_WEAK, str(scored.band))

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "main.py", "print(1)\n")
        scored = score_structure(root, "source_project")
        check(
            "source project is not penalised for missing markers",
            scored.band == BAND_ACCEPTABLE,
            str(scored.band),
        )


def test_documentation_dimension() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "main.py", "print(1)\n")
        scored = score_documentation(root)
        check("no docs scores weak on D4", scored.band == BAND_WEAK, str(scored.band))

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "README.md", "x" * 3000)
        scored = score_documentation(root)
        check("substantial README scores strong on D4", scored.band == BAND_STRONG, str(scored.band))

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "README.md", "# hi\n")
        scored = score_documentation(root)
        check("thin README scores acceptable on D4", scored.band == BAND_ACCEPTABLE, str(scored.band))


def test_testing_dimension() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "main.py", "print(1)\n")
        scored = score_testing(root)
        check("no tests scores weak on D5", scored.band == BAND_WEAK, str(scored.band))

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "tests" / "test_one.py", "def test_a(): pass\n")
        scored = score_testing(root)
        check("one test file scores acceptable on D5", scored.band == BAND_ACCEPTABLE, str(scored.band))

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for i in range(6):
            _write(root / "tests" / f"test_{i}.py", "def test_a(): pass\n")
        scored = score_testing(root)
        check("many test files score strong on D5", scored.band == BAND_STRONG, str(scored.band))


def test_skip_dirs_are_ignored() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "node_modules" / "tests" / "test_x.py", "pass\n")
        _write(root / "main.py", "print(1)\n")
        scored = score_testing(root)
        check(
            "tests inside node_modules are ignored",
            scored.band == BAND_WEAK,
            str(scored.band),
        )

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / ".git" / "README.md", "x" * 5000)
        scored = score_documentation(root)
        check("docs inside .git are ignored", scored.band == BAND_WEAK, str(scored.band))


def test_combined_scoring() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "SKILL.md", "# skill\n")
        _write(root / "README.md", "x" * 3000)
        for i in range(6):
            _write(root / "tests" / f"test_{i}.py", "def test_a(): pass\n")

        result = score_deterministic(root, "skill", [])

        check(
            "all deterministic dimensions are scored",
            set(result.scores) == set(DETERMINISTIC_DIMENSIONS),
            str(sorted(result.scores)),
        )
        check(
            "a clean complete repo scores strong on every deterministic dimension",
            all(band == BAND_STRONG for band in result.scores.values()),
            str(result.scores),
        )
        check("evidence is collected", len(result.evidence) > 0)
        check(
            "judge-only dimensions are declared",
            set(result.judge_dimensions) == set(JUDGE_ONLY_DIMENSIONS),
        )
        check(
            "no deterministic dimension overlaps a judge dimension",
            not (set(DETERMINISTIC_DIMENSIONS) & set(JUDGE_ONLY_DIMENSIONS)),
        )


def test_weak_repo_scores_low() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "main.py", "print(1)\n")

        result = score_deterministic(
            root,
            "skill",
            [{"severity": "hard_fail", "category": "secret:aws", "file_path": "main.py", "line": 1}],
        )

        check("weak repo scores weak on D1", result.scores["d1_security_and_compliance"] == BAND_WEAK)
        check("weak repo scores weak on D2", result.scores["d2_structure_and_conformance"] == BAND_WEAK)
        check("weak repo scores weak on D4", result.scores["d4_documentation"] == BAND_WEAK)
        check("weak repo scores weak on D5", result.scores["d5_testing_and_reliability"] == BAND_WEAK)


def test_missing_repo_raises() -> None:
    try:
        score_deterministic("/nonexistent/path/xyz", "skill", [])
        check("missing repo raises FileNotFoundError", False)
    except FileNotFoundError:
        check("missing repo raises FileNotFoundError", True)


def main() -> int:
    test_security_dimension()
    test_structure_dimension()
    test_documentation_dimension()
    test_testing_dimension()
    test_skip_dirs_are_ignored()
    test_combined_scoring()
    test_weak_repo_scores_low()
    test_missing_repo_raises()

    print()
    if FAILURES:
        print(f"{len(FAILURES)} test(s) failed: {', '.join(FAILURES)}")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
