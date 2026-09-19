"""Allowlist-enforced judge transport.

This is the ONLY module in the pipeline permitted to open a network connection.
It refuses to send a request unless the destination host passes the allowlist
check, so a misconfigured endpoint fails closed instead of leaking submission
content to an unapproved destination.

The transport is deliberately generic: point it at any internal chat-completions
compatible endpoint by supplying a small `build_request` function. Nothing here
knows about a specific vendor.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable

from allowlist import NetworkAllowlist


class EgressBlockedError(RuntimeError):
    """Raised when a destination is outside the approved internal boundary."""


@dataclass
class TransportConfig:
    endpoint_url: str
    model: str
    temperature: float = 0.0
    timeout_seconds: int = 60
    max_retries: int = 3
    backoff_seconds: float = 1.0
    extra_headers: dict[str, str] = field(default_factory=dict)


def default_request_builder(prompt: str, config: TransportConfig) -> dict[str, Any]:
    """Build an OpenAI-compatible chat request body.

    Override this if the internal endpoint uses a different schema.
    """
    return {
        "model": config.model,
        "temperature": config.temperature,
        "messages": [
            {"role": "system", "content": "You are a constrained evaluation judge. Return only JSON."},
            {"role": "user", "content": prompt},
        ],
    }


def default_response_parser(payload: dict[str, Any]) -> str:
    """Extract the assistant text from an OpenAI-compatible response body."""
    choices = payload.get("choices") or []
    if not choices:
        raise ValueError("Response contained no choices")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if not isinstance(content, str):
        raise ValueError("Response message did not contain text content")
    return content


class JudgeTransport:
    """Allowlist-enforced HTTP transport for judge calls."""

    def __init__(
        self,
        config: TransportConfig,
        allowlist: NetworkAllowlist,
        api_key: str | None = None,
        request_builder: Callable[[str, TransportConfig], dict[str, Any]] | None = None,
        response_parser: Callable[[dict[str, Any]], str] | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.config = config
        self.allowlist = allowlist
        self.api_key = api_key
        self.build_request = request_builder or default_request_builder
        self.parse_response = response_parser or default_response_parser
        self._sleep = sleep

    def assert_allowed(self) -> None:
        decision = self.allowlist.check_url(self.config.endpoint_url)
        if not decision.allowed:
            raise EgressBlockedError(
                f"Judge endpoint blocked by allowlist: {self.config.endpoint_url} "
                f"({decision.reason})"
            )

    def __call__(self, prompt: str) -> str:
        """Send a single judge prompt, returning raw response text."""
        self.assert_allowed()

        body = json.dumps(self.build_request(prompt, self.config)).encode("utf-8")

        headers = {"Content-Type": "application/json", **self.config.extra_headers}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        last_error: Exception | None = None
        for attempt in range(self.config.max_retries):
            request = urllib.request.Request(
                self.config.endpoint_url,
                data=body,
                headers=headers,
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                return self.parse_response(payload)
            except urllib.error.HTTPError as exc:
                last_error = exc
                # Retry only on rate limiting and transient server errors.
                if exc.code not in {429, 500, 502, 503, 504}:
                    raise
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc

            if attempt < self.config.max_retries - 1:
                # Exponential backoff with jitter to avoid synchronised retries.
                delay = self.config.backoff_seconds * (2**attempt)
                self._sleep(delay)

        raise RuntimeError(f"Judge transport failed after {self.config.max_retries} attempts: {last_error}")
