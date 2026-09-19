"""Network allowlist enforcement for the Code Cup evaluation pipeline.

Default posture: deny everything that is not an approved internal host.
This module contains no network calls itself; it only decides whether a
destination would be permitted. Enforcement happens in the orchestrator.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

APPROVED_SUFFIXES = (".example",)


@dataclass
class AllowlistDecision:
    allowed: bool
    host: str
    reason: str


class NetworkAllowlist:
    def __init__(
        self,
        allowed_domains: list[str] | None = None,
        blocked_domains: list[str] | None = None,
    ) -> None:
        self.allowed_domains = {
            d.strip().lower() for d in (allowed_domains or []) if d and d.strip()
        }
        self.blocked_domains = {
            d.strip().lower() for d in (blocked_domains or []) if d and d.strip()
        }

    @classmethod
    def from_file(cls, path: str | Path) -> "NetworkAllowlist":
        """Load an allowlist from a local JSON file only."""
        config_path = Path(path)
        if not config_path.exists():
            raise FileNotFoundError(f"Allowlist not found: {config_path}")

        data = json.loads(config_path.read_text(encoding="utf-8"))
        return cls(
            allowed_domains=data.get("allowed_domains", []),
            blocked_domains=data.get("blocked_domains", []),
        )

    def check_host(self, host: str) -> AllowlistDecision:
        normalized = (host or "").strip().lower()

        if not normalized:
            return AllowlistDecision(False, normalized, "empty host is not permitted")

        if self._matches(normalized, self.blocked_domains):
            return AllowlistDecision(
                False, normalized, "host is explicitly blocklisted"
            )

        if self._matches(normalized, self.allowed_domains):
            return AllowlistDecision(True, normalized, "host is on the allowlist")

        if normalized.endswith(APPROVED_SUFFIXES):
            return AllowlistDecision(
                True, normalized, "host is inside the approved internal estate"
            )

        return AllowlistDecision(
            False, normalized, "host is outside the approved internal boundary"
        )

    def check_url(self, url: str) -> AllowlistDecision:
        parsed = urlparse(url)
        return self.check_host(parsed.hostname or "")

    @staticmethod
    def _matches(host: str, patterns: set[str]) -> bool:
        for pattern in patterns:
            if pattern.startswith("."):
                if host == pattern[1:] or host.endswith(pattern):
                    return True
            elif host == pattern or host.endswith(f".{pattern}"):
                return True
        return False
