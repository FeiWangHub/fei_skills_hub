# Zero-Execution Security & Compliance Static Checklist

This checklist defines what the **deterministic static scanner** (Layer 0 gate + Dimension 3 evidence feed) must detect **without running any submitted code**. It is organized as pattern *categories* (for a future implementer to turn into regex/AST-grep/semgrep rules) — this document itself contains no scanning code.

Aligned to CWE identifiers and OWASP Top 10 for LLM Applications where applicable.

---

## Severity Tiers

| Tier | Meaning | Effect |
|---|---|---|
| **Auto-Fail** | Confirmed real secret/credential or confirmed exfiltration-capable call to an unapproved external endpoint | Layer 0 gate FAILS → submission routed to remediation queue, Dimension 3 locked to 0, no Tier 1 score issued until fixed |
| **Warn** | Pattern that *could* be risky but requires context (e.g., generic `eval()` usage, broad tool permission grant) | Does not fail the gate; injected as a fact into the Dimension 3 LLM reasoning, capped contribution |
| **Info** | Stylistic/best-practice deviation (e.g., missing `--help` on a script) | Feeds Dimension 4/5 only |

---

## Category 1 — Hardcoded Secrets & Sensitive Data (CWE-798, CWE-312)

**Auto-Fail signatures**:
- API key / bearer token patterns: `Bearer [A-Za-z0-9_\-\.]{20,}`, well-known provider key prefixes (e.g. `sk-`, `AKIA`, `ghp_`, `xox[baprs]-`)
- Private key headers: `-----BEGIN (RSA|EC|OPENSSH|PGP) PRIVATE KEY-----`
- Database connection strings with embedded credentials: `postgres://user:pass@`, `mongodb(+srv)?://user:pass@`
- Unmasked real-looking PII: Luhn-valid credit card numbers, SSN/Tax-ID-shaped strings **not** annotated as mock data

**Warn signatures**:
- Internal hostnames/domains (`*.internal.bank.corp`, `*.corp.local`)
- Internal IP ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`) hardcoded in config
- Generic `password =`, `secret =`, `token =` string literal assignments (even if value looks like a placeholder — flag for human glance)

## Category 2 — Air-Gap & Exfiltration Violations (CWE-200, OWASP LLM06)

**Auto-Fail signatures**:
- Outbound HTTP calls (`requests.`, `axios.`, `fetch(`, `httpx.`, `urllib.request.`) targeting a **hardcoded public-internet hostname** that is not on an approved allow-list (approved list = organizer-maintained, see `11-...md`)
- Remote-fetch-and-execute patterns: `curl ... | sh`, `curl ... | bash`, `iex (New-Object Net.WebClient).DownloadString(...)`
- Package installs from unpinned/arbitrary remote sources: `pip install --extra-index-url <external>`, `npm install <git-url>` pointing outside the org's registry

**Warn signatures**:
- Any outbound network call where the destination is a **variable/config value** rather than hardcoded (can't statically confirm target — needs human/dynamic check)
- Analytics/telemetry SDK imports (posthog, segment, sentry, mixpanel, etc.) without an explicit opt-out/disable flag visible in config

## Category 3 — Agent/Tool Execution Risk (CWE-78, CWE-94, CWE-22, CWE-89)

**Warn signatures** (rarely auto-fail from static text alone, since context matters):
- `eval(`, `exec(`, `compile(`, `os.system(`, `subprocess.Popen(..., shell=True)` where an argument is traceable to unsanitized external/tool input
- Node `child_process.exec(`, `vm.runInContext(`
- File-path construction via string concatenation feeding into file-read/write APIs without a visible containment check (e.g., no `commonpath`/`resolve`-and-compare against a base directory)
- SQL/NoSQL query strings built via f-string/`+` concatenation instead of parameterized queries/prepared statements

## Category 4 — Prompt Injection & Excessive Agency (OWASP LLM01, LLM06)

**Warn signatures** (Agent/Skill submissions only):
- No visible delimiter/tagging convention (e.g. `<untrusted_context>`) when the agent's instructions describe ingesting external documents, emails, web pages, or arbitrary repo content into the model context
- Declared tool permissions that are maximally broad with no scoping:
  - OpenCode: `permission.bash` = blanket `"*": allow`; `permission.webfetch`/`permission.websearch` = `allow` with no narrowing
  - GitHub Copilot: `tools: ["*"]` on an agent whose stated purpose doesn't need write/execute access
  - Claude Skill: `allowed-tools` granting `Bash(*)` unscoped

## Category 5 — Repo Hygiene Signals (feeds Dimension 4, not security gate)

- `.env` files committed with non-empty values (vs. `.env.example` with placeholders — that's fine)
- `node_modules/`, `venv/`, build artifacts, or `.pyc`/`.class` binaries committed (signal of low engineering hygiene)
- No `.gitignore` present at all

---

## How This Feeds the Pipeline

1. Scanner runs Categories 1-3 as **Auto-Fail vs Warn vs clean**, producing a `security_scan_result` fact object (see `08-json-output-schema.md`).
2. If any Auto-Fail hit → Layer 0 gate FAILS immediately, remediation ticket generated with file:line references, no LLM call made for this submission's Tier 1 score.
3. If only Warn/Info hits → these are **injected as pre-computed facts** into the Dimension 3 Judge prompt (see `templates/judge-prompt-*.md`) so the LLM reasons over confirmed findings rather than re-discovering them (cheaper, more reliable, avoids the LLM missing something the deterministic scanner already caught).
4. The LLM Judge is explicitly instructed: **do not perform your own security scanning from scratch** — only interpret/contextualize the findings already provided, and you may note additional *candidate* concerns as "observations" (not scored) for human follow-up.
