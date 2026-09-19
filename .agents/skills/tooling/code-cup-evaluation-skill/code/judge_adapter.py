"""Constrained LLM judge adapter for Code Cup evaluation.

Responsibilities:
- build a judge prompt from an evidence bundle
- validate that the judge response is strict JSON
- enforce the evidence rule: a positive score requires evidence

The adapter performs NO network calls. The caller supplies a transport
function that must already be restricted to the internal allowlist.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

SCORE_KEYS = (
    "d1_security_and_compliance",
    "d2_structure_and_conformance",
    "d3_code_quality",
    "d4_documentation",
    "d5_testing_and_reliability",
    "d6_business_value",
    "d7_innovation",
)

ALLOWED_BANDS = {1, 3, 5}


@dataclass
class JudgeRequest:
    submission_id: str
    artifact_type: str
    repo_name: str
    commit_sha: str
    team_alias: str
    rubric_version: str
    prompt_version: str
    evidence_bundle: str


def load_prompt_template(path: str | Path) -> str:
    template_path = Path(path)
    if not template_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {template_path}")
    return template_path.read_text(encoding="utf-8")


def build_prompt(template: str, request: JudgeRequest) -> str:
    replacements = {
        "{{artifact_type}}": request.artifact_type,
        "{{repo_name}}": request.repo_name,
        "{{commit_sha}}": request.commit_sha,
        "{{team_alias}}": request.team_alias,
        "{{rubric_version}}": request.rubric_version,
        "{{prompt_version}}": request.prompt_version,
        "{{evidence_bundle}}": request.evidence_bundle,
    }

    prompt = template
    for key, value in replacements.items():
        prompt = prompt.replace(key, value)
    return prompt


class JudgeValidationError(ValueError):
    """Raised when the judge response violates the output contract."""


def parse_and_validate(response_text: str) -> dict[str, object]:
    """Parse judge output and enforce the contract.

    Rules enforced:
    - response must be a single JSON object
    - all score keys present
    - scores must be inside the anchored bands
    - any positive score must have evidence
    """
    text = (response_text or "").strip()

    if text.startswith("```"):
        raise JudgeValidationError("Response must not be wrapped in markdown fences")

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise JudgeValidationError(f"Response is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise JudgeValidationError("Response root must be a JSON object")

    scores = data.get("scores")
    if not isinstance(scores, dict):
        raise JudgeValidationError("Response is missing a 'scores' object")

    for key in SCORE_KEYS:
        if key not in scores:
            raise JudgeValidationError(f"Missing score key: {key}")
        value = scores[key]
        if not isinstance(value, int) or isinstance(value, bool):
            raise JudgeValidationError(f"Score {key} must be an integer")
        if value not in ALLOWED_BANDS and value != 0:
            raise JudgeValidationError(
                f"Score {key}={value} is outside the anchored bands {sorted(ALLOWED_BANDS)}"
            )

    evidence = data.get("evidence")
    if not isinstance(evidence, list):
        raise JudgeValidationError("Response is missing an 'evidence' array")

    positive_without_evidence = [
        key for key in SCORE_KEYS if scores.get(key, 0) > 0 and not evidence
    ]
    if positive_without_evidence:
        raise JudgeValidationError(
            "Positive scores require at least one evidence item: "
            + ", ".join(positive_without_evidence)
        )

    confidence = data.get("confidence")
    if confidence not in {"high", "medium", "low"}:
        raise JudgeValidationError("confidence must be one of high|medium|low")

    return data


def run_judge(
    request: JudgeRequest,
    template_path: str | Path,
    transport: Callable[[str], str],
    max_attempts: int = 3,
) -> dict[str, object]:
    """Run the judge with limited retries on contract violations.

    `transport` must be an internal-only, allowlist-enforced callable.
    """
    template = load_prompt_template(template_path)
    prompt = build_prompt(template, request)

    last_error: Exception | None = None
    for _ in range(max_attempts):
        raw = transport(prompt)
        try:
            return parse_and_validate(raw)
        except JudgeValidationError as exc:
            last_error = exc

    raise JudgeValidationError(
        f"Judge failed to produce a compliant response after {max_attempts} attempts: {last_error}"
    )
