# Standard A — Claude / Anthropic Agent Skill Specification

**Sources**: Agent Skills Open Standard ([agentskills.io/specification](https://agentskills.io/specification)), Anthropic Claude Code Skills docs ([docs.anthropic.com/en/docs/claude-code/skills](https://docs.anthropic.com/en/docs/claude-code/skills)), official `anthropics/skills` GitHub repository, `agentskills.io/skill-creation/*` best-practice guides.

This is the reference document the Judge Agent must be given when scoring an **Agent Skill submission** (schema-conformance dimension). It is also the basis for the deterministic hard-gate validator (see `04-scoring-rubric.md` and `05-security-static-checklist.md`).

---

## 1. Directory & File Structure

Every skill is a directory containing, at minimum, a root `SKILL.md` file:

```text
<skill-name>/
├── SKILL.md              # REQUIRED — YAML frontmatter + Markdown instructions
├── scripts/               # OPTIONAL — executable helper code
├── references/            # OPTIONAL — on-demand reference docs, loaded conditionally
├── assets/                 # OPTIONAL — static assets (templates, schemas, icons)
└── evals/                  # OPTIONAL — evals.json test cases
```

**Naming rules**:
- Entry-point filename MUST be `SKILL.md` (uppercase).
- The containing directory name MUST match the `name` frontmatter field verbatim.
- Internal references (e.g. `references/REFERENCE.md`) must use relative paths, kept to 1 level of nesting where possible.

---

## 2. YAML Frontmatter Fields

### 2.1 Core Open-Spec Fields (portable across Claude Code, Claude.ai uploads, Anthropic Skills API)

Any frontmatter key **outside this list** fails standard packaging validation ("Unexpected key(s) in SKILL.md frontmatter").

| Field | Type | Required | Constraints |
|---|---|---|---|
| `name` | string | **Yes** | 1–64 chars. Lowercase alphanumeric + single hyphens only (`^[a-z0-9]+(-[a-z0-9]+)*$`). No leading/trailing/consecutive hyphens. Must equal parent directory name. |
| `description` | string | **Yes** | 1–1024 chars. Must state *what* the skill does and *when* to trigger it. |
| `license` | string | No | e.g. `MIT`, `Apache-2.0`, or "Proprietary — see LICENSE.txt". |
| `compatibility` | string | No | 1–500 chars. Environment/runtime requirements. |
| `metadata` | map (string→string) | No | Free-form key-value pairs (author, version, etc.). |
| `allowed-tools` | string or list | No | Space-separated or YAML list of pre-approved tools, e.g. `Bash(git:*) Read Grep`. |

### 2.2 Claude Code Extended Fields (client-specific, still valid in the open spec's `metadata`/extension slots)

| Field | Type | Default | Description |
|---|---|---|---|
| `when_to_use` | string | none | Appended to `description` for indexing; combined cap 1,536 chars. |
| `disable-model-invocation` | boolean | `false` | If `true`, only explicit user invocation triggers the skill (no autonomous triggering). |
| `user-invocable` | boolean | `true` | If `false`, hidden from `/` autocomplete; agent-only background knowledge. |
| `disallowed-tools` | string/list | none | Tools removed from the pool while this skill is active. |
| `argument-hint` | string | none | Autocomplete placeholder text. |
| `arguments` | string/list | none | Named positional args mapped to `$1`, `$2`, `$varname`. |
| `context` | string | none | `context: fork` spawns an isolated subagent to run the skill. |
| `hooks` | object | none | Lifecycle hooks (`PreToolUse`, `PostToolUse`). |

---

## 3. Progressive Disclosure Architecture (Size Budget)

```
Tier 1 — Metadata     (always loaded, ~100 tokens)   → name + description only
Tier 2 — Instructions (loaded on activation, <5,000 tokens) → full SKILL.md body, <500 lines
Tier 3 — Resources    (loaded on demand, unlimited)  → scripts/, references/, assets/
```

- `description`: hard cap **1,024 chars** (spec) / **1,536 chars** combined with `when_to_use` (Claude Code).
- `SKILL.md` body: **under 500 lines**, **under ~5,000 tokens**.
- Any reference file over 300 lines needs its own table of contents and must be pulled out of the main body.

---

## 4. Description-Writing / Trigger-Engineering Rules

1. **Imperative, action-first phrasing** — "Use this skill when the user asks to..." not "Helps with...".
2. **Cover both formal and casual phrasing** of the same intent (file extensions, synonyms, colloquial task names).
3. **Calibrate slightly "pushy"** — LLMs under-trigger skills that look solvable with plain tools; explicitly enumerate trigger scenarios.
4. **Negative boundary precision** — explicitly distinguish this skill's domain from adjacent skills to avoid false-triggering.

---

## 5. Script & Tool Execution Standards (for skills that bundle `scripts/`)

- Scripts must be **fully non-interactive** — no stdin prompts; all inputs via flags/env vars/config.
- Scripts must self-document via `--help`.
- Machine-parseable output (JSON/CSV) on stdout; diagnostics/progress on stderr.
- Self-contained dependency declaration (e.g. Python PEP 723 inline metadata, or lockfiles committed alongside).

*(This section is evaluated on submissions but is not itself something CodeCup Eval implements as code — see the parent SKILL.md's "no code" constraint.)*

---

## 6. Official Skill Quality & Best-Practice Checklist

| Category | Pass Signal | Fail / Anti-Pattern |
|---|---|---|
| Scope & Focus | Single coherent purpose | Kitchen-sink skill spanning unrelated domains |
| Token Economy | Teaches what the model *lacks* (project-specific APIs, gotchas) | Restates baseline knowledge everyone already has |
| Prescriptiveness | Balances flexible reasoning with strict steps only where fragility demands it | Wall of `ALWAYS`/`NEVER` rules with no rationale |
| Gotchas Section | Explicit environment quirks, non-obvious failure modes | Generic "handle errors appropriately" |
| Output Templates | Concrete markdown/JSON output templates provided | Abstract prose with no structural example |
| Self-Validation | Built-in verify-before-done step | Blind execution, no sanity check |
| Security & Safety | "Principle of Lack of Surprise" — zero hidden exfiltration, transparent tool use | Obfuscated commands, hidden network calls, hardcoded secrets |

---

## 7. Machine-Checkable Conformance Rules (Hard Gate)

These rules are deterministic and should run **before** any LLM judging call:

1. `SKILL.md` file exists at the submission's skill root.
2. Frontmatter parses as valid YAML and is a flat map (not nested lists at top level).
3. Frontmatter contains **only** keys from: `name, description, license, allowed-tools, metadata, compatibility` (plus recognized Claude Code extension keys listed in §2.2, if the submission explicitly targets Claude Code).
4. `name` is present, matches `^[a-z0-9]+(-[a-z0-9]+)*$`, ≤ 64 chars, equals the parent directory name.
5. `description` is present, non-empty, ≤ 1,024 chars, contains no raw `<`/`>` angle-bracket HTML.
6. If `compatibility` present: ≤ 500 chars.
7. `SKILL.md` body line count < 500 (warn, not hard-fail, if between 500–700; hard-fail above 700).

## 8. Canonical Example (Illustrative Only)

```markdown
---
name: data-exporter
description: Extracts transaction records, scrubs PII, and generates audit reports. Use whenever the user requests ledger exports, data extracts, or transaction compliance audits.
license: Proprietary
compatibility: Requires Python 3.11+ and uv
allowed-tools: Bash(uv run ${CLAUDE_SKILL_DIR}/scripts/*) Read
metadata:
  author: enterprise-data-team
  version: "1.2.0"
---

# Data Exporter

## Workflow Checklist
- [ ] Step 1: Pre-flight check
- [ ] Step 2: Extract dataset to staging
- [ ] Step 3: Verify zero PII leakage

## Gotchas
- Ledger timestamps are UTC epoch milliseconds — always normalize to ISO-8601 in exports.
- Transaction amounts are stored as integer cents, not floating-point dollars.
```

> This example is a **data/format illustration**, not an executable script, and is safe to include in this requirements pack.
