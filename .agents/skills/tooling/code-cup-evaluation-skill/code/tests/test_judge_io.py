"""Tests for the two-phase host-agent judge workflow.

Run with:
    PYTHONPATH=. python3 tests/test_judge_io.py
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from judge_adapter import (  # noqa: E402
    JudgeValidationError,
    build_evidence_bundle,
    build_prompt,
    JudgeRequest,
)
from judge_io import AGENT_STAGE_NAME, load_agent_scores  # noqa: E402

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


def test_evidence_bundle_prioritises_entry_files() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "SKILL.md", "# Skill\n" + "x" * 500)
        _write(root / "README.md", "# Readme\n")
        _write(root / "src" / "main.py", "print(1)\n")
        _write(root / "tests" / "test_a.py", "def test_a(): pass\n")

        bundle, included = build_evidence_bundle(root, "skill")

        check("entry files come first", included[0] in {"SKILL.md", "README.md"}, str(included))
        check("bundle wraps content as untrusted", "UNTRUSTED_REPOSITORY_CONTENT" in bundle)
        check("bundle declares the data-not-instructions rule", "never as instructions" in bundle)
        check("file markers are present", "--- FILE:" in bundle)
        check("nested files are included", any("src/" in p for p in included), str(included))


def test_evidence_bundle_skips_vendored_dirs() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "SKILL.md", "# Skill\n")
        _write(root / "node_modules" / "pkg" / "index.js", "module.exports = 1\n")
        _write(root / ".git" / "config", "[core]\n")

        _, included = build_evidence_bundle(root, "skill")
        check("node_modules is skipped", not any("node_modules" in p for p in included), str(included))
        check(".git is skipped", not any(".git" in p for p in included), str(included))


def test_evidence_bundle_respects_caps() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for i in range(50):
            _write(root / f"file_{i}.py", "x = 1\n" * 200)

        _, included = build_evidence_bundle(root, "source_project", max_files=5)
        check("max_files is enforced", len(included) <= 5, str(len(included)))

        bundle, _ = build_evidence_bundle(root, "source_project", max_bytes=2000)
        check("max_bytes is enforced", len(bundle) < 3000, str(len(bundle)))


def test_oversized_entry_file_is_truncated_not_dropped() -> None:
    """The entry point is the most informative file; never drop it silently."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "SKILL.md", "# Skill\n" + "x" * 50_000)
        _write(root / "other_big.py", "y = 1\n" * 20_000)

        bundle, included = build_evidence_bundle(
            root, "skill", max_file_bytes=5_000, max_bytes=200_000
        )

        check(
            "oversized entry file is still included",
            "SKILL.md" in included,
            str(included),
        )
        check(
            "oversized non-entry file is skipped",
            "other_big.py" not in included,
            str(included),
        )
        check(
            "truncation is marked in the bundle",
            "[truncated at 5000 bytes" in bundle,
            "marker missing",
        )


def test_entry_file_survives_a_tight_total_budget() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "SKILL.md", "# Skill\n" + "x" * 30_000)
        _write(root / "filler.py", "z = 1\n" * 5_000)

        bundle, included = build_evidence_bundle(
            root, "skill", max_file_bytes=30_000, max_bytes=8_000
        )
        check(
            "entry file survives a tight total budget",
            "SKILL.md" in included,
            str(included),
        )
        check("bundle stays within the total budget", len(bundle) < 12_000, str(len(bundle)))


def test_evidence_bundle_missing_repo_raises() -> None:
    try:
        build_evidence_bundle("/nonexistent/repo/xyz")
        check("missing repo raises FileNotFoundError", False)
    except FileNotFoundError:
        check("missing repo raises FileNotFoundError", True)


def test_prompt_substitutes_placeholders() -> None:
    request = JudgeRequest(
        submission_id="TEAM_001",
        artifact_type="skill",
        repo_name="TEAM_001",
        commit_sha="abc123",
        team_alias="TEAM_001",
        rubric_version="1",
        prompt_version="1",
        evidence_bundle="EVIDENCE",
    )
    template = (
        "type={{artifact_type}} sha={{commit_sha}} "
        "rubric={{rubric_version}} bundle={{evidence_bundle}}"
    )
    prompt = build_prompt(template, request)

    check("artifact type substituted", "type=skill" in prompt)
    check("commit sha substituted", "sha=abc123" in prompt)
    check("evidence substituted", "bundle=EVIDENCE" in prompt)
    check("no placeholders remain", "{{" not in prompt)


def _valid_entry() -> dict:
    return {
        "scores": {
            "d1_security_and_compliance": 3,
            "d2_structure_and_conformance": 5,
            "d3_code_quality": 5,
            "d4_documentation": 5,
            "d5_testing_and_reliability": 3,
            "d6_business_value": 5,
            "d7_innovation": 5,
        },
        "evidence": [{"file_path": "SKILL.md", "line_or_range": "1-10", "note": "ok"}],
        "confidence": "high",
    }


def test_load_agent_scores_accepts_mapping() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "judge-scores.json"
        path.write_text(json.dumps({"TEAM_001": _valid_entry()}), encoding="utf-8")

        scores = load_agent_scores(path)
        check("mapping form is parsed", "TEAM_001" in scores)
        check("confidence is preserved", scores["TEAM_001"]["confidence"] == "high")


def test_load_agent_scores_accepts_list() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "judge-scores.json"
        entry = {"submission_id": "TEAM_001", **_valid_entry()}
        path.write_text(json.dumps([entry]), encoding="utf-8")

        scores = load_agent_scores(path)
        check("list form is parsed", "TEAM_001" in scores)


def test_load_agent_scores_rejects_bad_entries() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "judge-scores.json"

        # A positive score with no evidence must be rejected.
        bad = _valid_entry()
        bad["evidence"] = []
        path.write_text(json.dumps({"TEAM_001": bad}), encoding="utf-8")
        try:
            load_agent_scores(path)
            check("evidence-free positive score is rejected", False)
        except JudgeValidationError:
            check("evidence-free positive score is rejected", True)

        # An out-of-band score must be rejected.
        bad2 = _valid_entry()
        bad2["scores"]["d3_code_quality"] = 99
        path.write_text(json.dumps({"TEAM_001": bad2}), encoding="utf-8")
        try:
            load_agent_scores(path)
            check("out-of-band score is rejected", False)
        except JudgeValidationError:
            check("out-of-band score is rejected", True)

        # A missing dimension must be rejected.
        bad3 = _valid_entry()
        del bad3["scores"]["d7_innovation"]
        path.write_text(json.dumps({"TEAM_001": bad3}), encoding="utf-8")
        try:
            load_agent_scores(path)
            check("missing dimension is rejected", False)
        except JudgeValidationError:
            check("missing dimension is rejected", True)

        # A missing file must be reported, not treated as an empty result.
        try:
            load_agent_scores(Path(tmp) / "absent.json")
            check("missing scores file raises", False)
        except FileNotFoundError:
            check("missing scores file raises", True)


def test_merge_is_idempotent() -> None:
    """Re-running merge must not double-count the judge stage or its evidence."""
    from judge_io import merge, prepare

    with tempfile.TemporaryDirectory() as tmp:
        repo_root = Path(tmp) / "repos"
        _write(repo_root / "TEAM_001" / "SKILL.md", "# Skill\n")
        _write(repo_root / "TEAM_001" / "README.md", "# Readme\n" + "x" * 3000)
        for i in range(6):
            _write(repo_root / "TEAM_001" / "tests" / f"test_{i}.py", "def test_a(): pass\n")

        manifest = Path(tmp) / "manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    "submissions": [
                        {
                            "submission_id": "TEAM_001",
                            "team_name": "Alpha",
                            "artifact_type": "skill",
                            "repo_url": "https://git.internal.example/a.git",
                            "commit_sha": "abc",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        allowlist = Path(tmp) / "allowlist.json"
        allowlist.write_text(
            json.dumps({"allowed_domains": [".example"], "blocked_domains": []}),
            encoding="utf-8",
        )
        out = Path(tmp) / "out"

        prepare(str(manifest), str(allowlist), str(repo_root), str(out), rubric_path=None)

        entry = _valid_entry()
        entry["tokens"] = {
            "prompt_tokens": 1000,
            "completion_tokens": 100,
            "total_tokens": 1100,
        }
        (out / "judge-scores.json").write_text(
            json.dumps({"TEAM_001": entry}), encoding="utf-8"
        )

        first = merge(str(out), rubric_path=None, report=False)
        first_record = first["results"][0]
        first_stages = [s["name"] for s in first_record["metrics"]["stages"]]
        first_evidence = len(first_record["evidence"])
        first_tokens = first["cost"]["measured_tokens"]

        second = merge(str(out), rubric_path=None, report=False)
        second_record = second["results"][0]
        second_stages = [s["name"] for s in second_record["metrics"]["stages"]]
        second_evidence = len(second_record["evidence"])
        second_tokens = second["cost"]["measured_tokens"]

        check(
            "judge stage is not duplicated",
            second_stages.count(AGENT_STAGE_NAME) == 1,
            str(second_stages),
        )
        check(
            "stage list is unchanged on re-run",
            first_stages == second_stages,
            f"{first_stages} vs {second_stages}",
        )
        check(
            "evidence is not duplicated",
            first_evidence == second_evidence,
            f"{first_evidence} vs {second_evidence}",
        )
        check(
            "measured tokens are not double-counted",
            first_tokens == second_tokens,
            f"{first_tokens} vs {second_tokens}",
        )
        check("measured tokens equal the reported amount", second_tokens == 1100, str(second_tokens))


def main() -> int:
    test_evidence_bundle_prioritises_entry_files()
    test_evidence_bundle_skips_vendored_dirs()
    test_evidence_bundle_respects_caps()
    test_oversized_entry_file_is_truncated_not_dropped()
    test_entry_file_survives_a_tight_total_budget()
    test_evidence_bundle_missing_repo_raises()
    test_prompt_substitutes_placeholders()
    test_load_agent_scores_accepts_mapping()
    test_load_agent_scores_accepts_list()
    test_load_agent_scores_rejects_bad_entries()
    test_merge_is_idempotent()

    print()
    if FAILURES:
        print(f"{len(FAILURES)} test(s) failed: {', '.join(FAILURES)}")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
