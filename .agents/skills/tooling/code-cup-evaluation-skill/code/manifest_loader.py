"""Load a frozen submission manifest for Code Cup evaluation.

This loader is intentionally offline-only. It parses YAML from a local file
and returns normalized submission records. It never fetches remote content.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - guidance for restricted environments
    yaml = None


@dataclass
class Submission:
    submission_id: str
    team_name: str
    artifact_type: str
    repo_url: str
    commit_sha: str
    track: str = ""
    contact_email: str = ""
    country: str = ""
    region: str = ""
    classification_confidence: str = "unknown"
    notes: str = ""
    state: str = "pending"
    extra: dict[str, Any] = field(default_factory=dict)


def _require_yaml():
    if yaml is None:
        raise RuntimeError(
            "PyYAML is required to read YAML manifests. "
            "Install it inside the internal environment or convert the manifest to JSON."
        )


def load_manifest(path: str | Path) -> dict[str, Any]:
    """Load a manifest file from a local path only.

    Supports YAML (preferred) and JSON (as a dependency-free fallback).
    """
    manifest_path = Path(path)
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    raw = manifest_path.read_text(encoding="utf-8")

    if manifest_path.suffix.lower() in {".json"}:
        data = json.loads(raw)
    else:
        _require_yaml()
        data = yaml.safe_load(raw)

    if not isinstance(data, dict):
        raise ValueError("Manifest root must be a mapping/object")

    return data


def normalize_submissions(manifest: dict[str, Any]) -> list[Submission]:
    submissions: list[Submission] = []
    for entry in manifest.get("submissions", []):
        submissions.append(
            Submission(
                submission_id=str(entry.get("submission_id", "")),
                team_name=str(entry.get("team_name", "")),
                artifact_type=str(entry.get("artifact_type", "source_project")),
                repo_url=str(entry.get("repo_url", "")),
                commit_sha=str(entry.get("commit_sha", "")),
                track=str(entry.get("track", "")),
                contact_email=str(entry.get("contact_email", "")),
                country=str(entry.get("country", "")),
                region=str(entry.get("region", "")),
                classification_confidence=str(
                    entry.get("classification_confidence", "unknown")
                ),
                notes=str(entry.get("notes", "")),
                state=str(entry.get("state", "pending")),
                extra={
                    k: v
                    for k, v in entry.items()
                    if k
                    not in {
                        "submission_id",
                        "team_name",
                        "artifact_type",
                        "repo_url",
                        "commit_sha",
                        "track",
                        "contact_email",
                        "country",
                        "region",
                        "classification_confidence",
                        "notes",
                        "state",
                    }
                },
            )
        )
    return submissions


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    """Return a list of validation problems. Empty list means valid."""
    problems: list[str] = []

    if "submissions" not in manifest:
        problems.append("Manifest is missing the 'submissions' key")
        return problems

    seen_ids: set[str] = set()
    for index, entry in enumerate(manifest["submissions"]):
        label = f"submissions[{index}]"
        submission_id = entry.get("submission_id")
        if not submission_id:
            problems.append(f"{label} is missing submission_id")
        elif submission_id in seen_ids:
            problems.append(f"{label} duplicates submission_id {submission_id}")
        else:
            seen_ids.add(submission_id)

        if not entry.get("repo_url"):
            problems.append(f"{label} is missing repo_url")

        if not entry.get("commit_sha"):
            problems.append(f"{label} is missing a frozen commit_sha")

    return problems
