"""Static security scanner for Code Cup submissions.

Behaviour:
- reads local files only
- never executes submitted code
- never opens a network connection
- fails closed on credentials, non-approved destinations, or injection text

The scanner is intentionally dependency-free so it can run in a restricted,
air-gapped environment. Optional external tools (gitleaks, semgrep) may be
invoked by the orchestrator as an additional layer, but this module must
remain self-contained.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from allowlist import NetworkAllowlist
from artifact_classifier import iter_scannable_files

SEVERITY_HARD_FAIL = "hard_fail"
SEVERITY_REVIEW = "review"

MAX_FILE_BYTES = 1_000_000

SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("aws_secret_key", re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*['\"][A-Za-z0-9/+=]{40}['\"]")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b")),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("anthropic_key", re.compile(r"\bsk-ant-[A-Za-z0-9\-_]{20,}\b")),
    ("private_key_block", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b")),
    ("generic_password", re.compile(r"(?i)\b(password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{8,}['\"]")),
    ("generic_secret", re.compile(r"(?i)\b(api_?key|client_?secret|access_?token)\s*[:=]\s*['\"][^'\"]{12,}['\"]")),
]

INJECTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("ignore_instructions", re.compile(r"(?i)ignore\s+(all\s+)?(previous|prior|above)\s+instructions")),
    ("force_full_score", re.compile(r"(?i)(give|assign|award)\s+(me\s+)?(a\s+)?(full|maximum|100)\s*(score|points|marks)")),
    ("system_override", re.compile(r"(?i)you\s+are\s+now\s+(the\s+)?(system|administrator|root)")),
    ("rubric_override", re.compile(r"(?i)(disregard|override)\s+(the\s+)?(rubric|scoring|rules)")),
    ("instruction_marker", re.compile(r"(?i)<\s*/?\s*(system|instruction|prompt)\s*>")),
]

DANGEROUS_SCRIPT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("curl_pipe_shell", re.compile(r"curl\s+[^\n|]*\|\s*(ba)?sh")),
    ("wget_pipe_shell", re.compile(r"wget\s+[^\n|]*\|\s*(ba)?sh")),
    ("postinstall_remote", re.compile(r"(?i)\"postinstall\"\s*:\s*\"[^\"]*(curl|wget|node\s+-e)")),
    ("base64_exec", re.compile(r"(?i)base64\s+(-d|--decode)\s*\|\s*(ba)?sh")),
    ("env_exfil", re.compile(r"(?i)(env|printenv)\s*\|\s*(curl|nc|wget)")),
]

URL_PATTERN = re.compile(r"https?://([A-Za-z0-9._\-]+)")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+\-]+@([A-Za-z0-9.\-]+\.[A-Za-z]{2,})\b")
INTERNAL_HOST_PATTERN = re.compile(r"(?i)\b[a-z0-9.\-]+\.(example|internal|corp|intra)\b")


@dataclass
class Finding:
    severity: str
    category: str
    file_path: str
    line: int
    line_text: str

    def as_dict(self) -> dict[str, object]:
        return {
            "severity": self.severity,
            "category": self.category,
            "file_path": self.file_path,
            "line": self.line,
            "line_text": self.line_text.strip()[:200],
        }


@dataclass
class ScanResult:
    passed: bool
    hard_failed: bool
    issues: list[str] = field(default_factory=list)
    findings: list[dict[str, object]] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "hard_failed": self.hard_failed,
            "issues": self.issues,
            "findings": self.findings,
        }


def _read_text(path: Path) -> str | None:
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return None
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def _scan_patterns(
    text: str,
    rel_path: str,
    patterns: list[tuple[str, re.Pattern[str]]],
    severity: str,
    category_prefix: str,
) -> list[Finding]:
    findings: list[Finding] = []
    for label, pattern in patterns:
        for match in pattern.finditer(text):
            line_no = text.count("\n", 0, match.start()) + 1
            line_start = text.rfind("\n", 0, match.start()) + 1
            line_end = text.find("\n", match.end())
            if line_end == -1:
                line_end = len(text)
            findings.append(
                Finding(
                    severity=severity,
                    category=f"{category_prefix}:{label}",
                    file_path=rel_path,
                    line=line_no,
                    line_text=text[line_start:line_end],
                )
            )
    return findings


def scan_repository(root: str | Path, allowlist: NetworkAllowlist) -> ScanResult:
    """Run the full static gate against a local repository snapshot."""
    root_path = Path(root)
    if not root_path.exists():
        raise FileNotFoundError(f"Repository path not found: {root_path}")

    findings: list[Finding] = []
    external_hosts: set[str] = set()

    for file_path in iter_scannable_files(root_path):
        text = _read_text(file_path)
        if text is None:
            continue

        rel_path = str(file_path.relative_to(root_path))

        findings.extend(
            _scan_patterns(text, rel_path, SECRET_PATTERNS, SEVERITY_HARD_FAIL, "secret")
        )
        findings.extend(
            _scan_patterns(text, rel_path, INJECTION_PATTERNS, SEVERITY_REVIEW, "injection")
        )
        findings.extend(
            _scan_patterns(
                text, rel_path, DANGEROUS_SCRIPT_PATTERNS, SEVERITY_HARD_FAIL, "script"
            )
        )

        for match in URL_PATTERN.finditer(text):
            host = match.group(1).lower()
            if not allowlist.check_host(host).allowed:
                external_hosts.add(host)
                line_no = text.count("\n", 0, match.start()) + 1
                line_start = text.rfind("\n", 0, match.start()) + 1
                line_end = text.find("\n", match.end())
                if line_end == -1:
                    line_end = len(text)
                findings.append(
                    Finding(
                        severity=SEVERITY_HARD_FAIL,
                        category=f"network:external_host:{host}",
                        file_path=rel_path,
                        line=line_no,
                        line_text=text[line_start:line_end],
                    )
                )

        for match in EMAIL_PATTERN.finditer(text):
            domain = match.group(1).lower()
            if not allowlist.check_host(domain).allowed:
                line_no = text.count("\n", 0, match.start()) + 1
                line_start = text.rfind("\n", 0, match.start()) + 1
                line_end = text.find("\n", match.end())
                if line_end == -1:
                    line_end = len(text)
                findings.append(
                    Finding(
                        severity=SEVERITY_REVIEW,
                        category="pii:external_email",
                        file_path=rel_path,
                        line=line_no,
                        line_text=text[line_start:line_end],
                    )
                )

    hard_fail_findings = [f for f in findings if f.severity == SEVERITY_HARD_FAIL]

    issues: list[str] = []
    if hard_fail_findings:
        issues.append(f"{len(hard_fail_findings)} hard-fail finding(s) detected")
    if external_hosts:
        issues.append(
            "non-approved external host(s): " + ", ".join(sorted(external_hosts))
        )
    review_count = len([f for f in findings if f.severity == SEVERITY_REVIEW])
    if review_count:
        issues.append(f"{review_count} finding(s) routed to human review")

    return ScanResult(
        passed=not hard_fail_findings,
        hard_failed=bool(hard_fail_findings),
        issues=issues,
        findings=[f.as_dict() for f in findings],
    )
