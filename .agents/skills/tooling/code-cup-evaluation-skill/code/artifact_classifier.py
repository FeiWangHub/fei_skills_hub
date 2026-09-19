"""Deterministic artifact-type classification for Code Cup submissions.

Classification is file-shape based only. No network access, no code execution.
"""

from __future__ import annotations

from pathlib import Path

ARTIFACT_SKILL = "skill"
ARTIFACT_COPILOT_AGENT = "copilot_agent"
ARTIFACT_OPENCODE_AGENT = "opencode_agent"
ARTIFACT_SOURCE_PROJECT = "source_project"

SKILL_MARKERS = ("SKILL.md", "skill.md")
COPILOT_AGENT_GLOBS = (".github/agents/*.agent.md",)
OPENCODE_MARKERS = ("opencode.json", "opencode.jsonc", ".opencode/agent", ".opencode/agents")

TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".json",
    ".jsonc",
    ".yaml",
    ".yml",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".go",
    ".rb",
    ".sh",
    ".ps1",
}


def _has_skill_marker(root: Path) -> bool:
    return any((root / marker).is_file() for marker in SKILL_MARKERS)


def _has_copilot_agent(root: Path) -> bool:
    agents_dir = root / ".github" / "agents"
    if not agents_dir.is_dir():
        return False
    return any(agents_dir.glob("*.agent.md"))


def _has_opencode_agent(root: Path) -> bool:
    if (root / "opencode.json").is_file() or (root / "opencode.jsonc").is_file():
        return True
    for candidate in (".opencode/agent", ".opencode/agents"):
        if (root / candidate).exists():
            return True
    return False


def classify(root: str | Path) -> tuple[str, str]:
    """Return (artifact_type, rationale)."""
    root_path = Path(root)

    if _has_skill_marker(root_path):
        return ARTIFACT_SKILL, "found SKILL.md / skill.md marker"

    if _has_copilot_agent(root_path):
        return ARTIFACT_COPILOT_AGENT, "found .github/agents/*.agent.md"

    if _has_opencode_agent(root_path):
        return ARTIFACT_OPENCODE_AGENT, "found opencode agent configuration"

    return ARTIFACT_SOURCE_PROJECT, "no skill or agent markers detected"


def iter_scannable_files(root: str | Path):
    """Yield scannable text files, skipping VCS and dependency directories."""
    root_path = Path(root)
    skip_dirs = {".git", "node_modules", "dist", "build", ".venv", "venv", "__pycache__"}

    for path in root_path.rglob("*"):
        if any(part in skip_dirs for part in path.parts):
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS and path.name not in SKILL_MARKERS:
            continue
        yield path
