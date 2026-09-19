"""Static security scanner for Code Cup submissions.

Behaviour:
- reads local files only
- never executes submitted code
- never opens a network connection
- fails closed on credentials and unapproved destinations

The scanner is intentionally dependency-free so it can run in a restricted,
air-gapped environment. Optional external tools (gitleaks, semgrep) may be
invoked by the orchestrator as an additional layer, but this module must
remain self-contained.

Context-aware severity
----------------------
The same string is a genuine risk in executable code but routine elsewhere.
A test fixture is *expected* to contain fake credentials; a security document
*describes* the patterns it detects; a JSON Schema `$schema` value is an
identifier, not an egress attempt. Treating all of these as hard failures
produces false positives that make the gate unusable.

Severity is therefore decided by file context:

| Context | Secrets | Unapproved URLs | Dangerous scripts |
|---|---|---|---|
| code / config | hard fail | hard fail | hard fail |
| test fixture | review | review | review |
| documentation | review | review | review |

Declaration identifiers (`$schema`, `$id`, `$ref`, `xmlns`) and comment lines
are never treated as egress. Placeholder-looking credentials are downgraded to
review. Nothing is silently dropped: a downgraded finding still reaches the
human review queue.
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

CONTEXT_CODE = "code"
CONTEXT_CONFIG = "config"
CONTEXT_TEST = "test"
CONTEXT_DOC = "doc"
CONTEXT_TEMPLATE = "template"

# Contexts where a match represents executable risk.
EXECUTABLE_CONTEXTS = {CONTEXT_CODE, CONTEXT_CONFIG}

DOC_EXTENSIONS = {".md", ".rst", ".adoc", ".txt"}
CONFIG_EXTENSIONS = {".json", ".jsonc", ".yaml", ".yml", ".toml", ".ini", ".cfg"}
TEST_PATH_HINTS = (
    "tests/",
    "test/",
    "spec/",
    "__tests__/",
    "test_",
    "_test.",
    ".test.",
    ".spec.",
)
DOC_DIR_HINTS = ("docs/", "references/", "documentation/")
# Templates exist to hold placeholder values, so a URL or credential-shaped
# string inside one is an example rather than a live configuration.
TEMPLATE_PATH_HINTS = (
    "templates/",
    "template",
    ".example",
    ".sample",
    ".tmpl",
    "fixtures/",
)

# Spec identifiers are declarations, not egress attempts.
DECLARATION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r'["\']?\$(schema|id|ref)["\']?\s*:', re.IGNORECASE),
    re.compile(r"\bxmlns\b", re.IGNORECASE),
]

# Lines that are comments, so a URL on them is a reference rather than a call.
COMMENT_LINE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^\s*#"),
    re.compile(r"^\s*//"),
    re.compile(r"^\s*\*"),
    re.compile(r"^\s*<!--"),
    re.compile(r"^\s*;"),
]

# Words that mark a credential-shaped string as an obvious placeholder.
PLACEHOLDER_MARKERS = (
    "example",
    "your_",
    "your-",
    "yourkey",
    "changeme",
    "placeholder",
    "dummy",
    "redacted",
    "xxxx",
    "todo",
)

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
    files_scanned: int = 0
    bytes_read: int = 0

    def as_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "hard_failed": self.hard_failed,
            "issues": self.issues,
            "findings": self.findings,
            "files_scanned": self.files_scanned,
            "bytes_read": self.bytes_read,
        }


def _read_text(path: Path) -> str | None:
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return None
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def classify_context(rel_path: str) -> str:
    """Decide how much weight a match in this file deserves.

    Documentation and test fixtures legitimately contain credential-shaped
    strings, pattern descriptions, and reference URLs. Treating those as hard
    failures makes the gate unusable on any repository that documents security.
    """
    lowered = rel_path.lower().replace("\\", "/")
    name = lowered.rsplit("/", 1)[-1]

    if any(hint in lowered for hint in TEST_PATH_HINTS):
        return CONTEXT_TEST

    if any(hint in lowered for hint in TEMPLATE_PATH_HINTS):
        return CONTEXT_TEMPLATE

    suffix = ""
    if "." in name:
        suffix = "." + name.rsplit(".", 1)[-1]

    if suffix in DOC_EXTENSIONS or any(hint in lowered for hint in DOC_DIR_HINTS):
        return CONTEXT_DOC

    if suffix in CONFIG_EXTENSIONS:
        return CONTEXT_CONFIG

    return CONTEXT_CODE


def _is_declaration(line_text: str) -> bool:
    """True for spec identifiers such as `$schema` or `xmlns`."""
    return any(pattern.search(line_text) for pattern in DECLARATION_PATTERNS)


def _is_comment_line(line_text: str) -> bool:
    return any(pattern.search(line_text) for pattern in COMMENT_LINE_PATTERNS)


def _looks_like_placeholder(line_text: str) -> bool:
    lowered = line_text.lower()
    return any(marker in lowered for marker in PLACEHOLDER_MARKERS)


def _severity_for(context: str, kind: str, line_text: str) -> str:
    """Resolve the effective severity for a match.

    `kind` is one of `secret`, `network`, or `script`.
    """
    if context not in EXECUTABLE_CONTEXTS:
        # Test fixtures and documentation are expected to contain examples.
        return SEVERITY_REVIEW

    if kind == "secret" and _looks_like_placeholder(line_text):
        return SEVERITY_REVIEW

    if kind == "network" and (_is_declaration(line_text) or _is_comment_line(line_text)):
        return SEVERITY_REVIEW

    return SEVERITY_HARD_FAIL


def _line_bounds(text: str, start: int, end: int) -> tuple[int, int, int]:
    line_no = text.count("\n", 0, start) + 1
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    if line_end == -1:
        line_end = len(text)
    return line_no, line_start, line_end


def _scan_patterns(
    text: str,
    rel_path: str,
    context: str,
    patterns: list[tuple[str, re.Pattern[str]]],
    category_prefix: str,
    kind: str,
) -> list[Finding]:
    findings: list[Finding] = []
    for label, pattern in patterns:
        for match in pattern.finditer(text):
            line_no, line_start, line_end = _line_bounds(text, match.start(), match.end())
            line_text = text[line_start:line_end]
            findings.append(
                Finding(
                    severity=_severity_for(context, kind, line_text),
                    category=f"{category_prefix}:{label}",
                    file_path=rel_path,
                    line=line_no,
                    line_text=line_text,
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
    files_scanned = 0
    bytes_read = 0

    for file_path in iter_scannable_files(root_path):
        text = _read_text(file_path)
        if text is None:
            continue

        files_scanned += 1
        bytes_read += len(text.encode("utf-8", errors="ignore"))

        rel_path = str(file_path.relative_to(root_path))
        context = classify_context(rel_path)

        findings.extend(
            _scan_patterns(text, rel_path, context, SECRET_PATTERNS, "secret", "secret")
        )
        findings.extend(
            _scan_patterns(text, rel_path, context, INJECTION_PATTERNS, "injection", "injection")
        )
        findings.extend(
            _scan_patterns(
                text, rel_path, context, DANGEROUS_SCRIPT_PATTERNS, "script", "script"
            )
        )

        for match in URL_PATTERN.finditer(text):
            host = match.group(1).lower()
            if allowlist.check_host(host).allowed:
                continue

            line_no, line_start, line_end = _line_bounds(text, match.start(), match.end())
            line_text = text[line_start:line_end]
            severity = _severity_for(context, "network", line_text)

            # Only a genuine, executable egress attempt counts as an external
            # host of concern; a documented reference URL does not.
            if severity == SEVERITY_HARD_FAIL:
                external_hosts.add(host)

            findings.append(
                Finding(
                    severity=severity,
                    category=f"network:external_host:{host}",
                    file_path=rel_path,
                    line=line_no,
                    line_text=line_text,
                )
            )

        for match in EMAIL_PATTERN.finditer(text):
            domain = match.group(1).lower()
            if allowlist.check_host(domain).allowed:
                continue

            line_no, line_start, line_end = _line_bounds(text, match.start(), match.end())
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
        files_scanned=files_scanned,
        bytes_read=bytes_read,
    )
