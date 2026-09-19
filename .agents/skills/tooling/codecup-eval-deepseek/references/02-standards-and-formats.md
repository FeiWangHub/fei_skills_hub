# 02 — Standards & Formats (the three schemas + normalization)

This file is the **single source of truth** for what a valid submission looks like. It is self-contained (no internet needed). Implement validators directly from it.

> **Key insight:** the three standards have **different frontmatter fields**. You cannot validate them with one schema. Normalize all three into the internal schema in §4, then score the normalized record.

---

## 1. Standard A — Agent Skill (Claude / Agent Skills spec)

**Location:** `<skill-name>/SKILL.md` (uppercase canonical; lowercase `skill.md` accepted as fallback).

**Allowed frontmatter keys (exactly six):** `name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility`. Any extra top-level key fails validation.

| Field | Required | Rules |
|---|---|---|
| `name` | **Yes** | 1–64 chars; `^[a-z0-9-]+$`; no leading/trailing hyphen; no `--`; **must equal the parent directory name** |
| `description` | **Yes** | 1–1024 chars; must state WHAT + WHEN; **no `<` or `>`** |
| `license` | No | SPDX id or pointer to bundled file |
| `compatibility` | No | 1–500 chars; runtime/environment prerequisites |
| `metadata` | No | map<string,string> |
| `allowed-tools` | No | experimental; space-separated tool patterns |

**Progressive disclosure (also a scoring input):**
- L1 = `name`+`description` (~100 tokens, always in context)
- L2 = `SKILL.md` body — keep **< 500 lines**
- L3 = `scripts/`, `references/`, `assets/` — loaded on demand; references should be **one level deep**; long reference files should carry a table of contents.

**Quality bar (from official skill-creator):** description is the primary trigger (make it "pushy"); write in imperative form; explain the *why* rather than heavy-handed ALL-CAPS MUSTs; extract repeated work into bundled scripts; principle of lack of surprise (no malicious content).

**Canonical template:**
```markdown
---
name: template-skill
description: Replace with what the skill does and when to use it.
---

# Insert instructions below
```

---

## 2. Standard B — GitHub Copilot custom agent

**Location:** `.github/agents/<name>.agent.md` (also `<name>.md`); user-level `~/.copilot/agents/`. The legacy `*.chatmode.md` format is **deprecated** — flag it.

**Frontmatter:**

| Field | Required | Notes |
|---|---|---|
| `description` | **Yes** | Used for auto-routing + UI |
| `name` | No | Defaults to filename |
| `target` | No | `vscode` \| `github-copilot` |
| `model` | No | string or string[] (fallback order) |
| `tools` | No | string[] or comma string; `[]` disables all |
| `agents` | No | allowed subagents (`*` or list); requires `agent` in tools |
| `handoffs` | No | suggestion buttons: label/agent/prompt/send/model |
| `mcp-servers` | No | agent-scoped MCP definitions |
| `argument-hint` | No | IDE input placeholder |
| `user-invocable` | No | default true |
| `disable-model-invocation` | No | default false |
| `metadata` | No | map<string,string> |

**Body:** the agent's system prompt; **max 30,000 characters**.

---

## 3. Standard C — OpenCode agent

**Location:** `.opencode/agent(s)/<name>.md` (project) or `~/.config/opencode/agent(s)/<name>.md` (global); OR `opencode.json` under an `"agent"` object. Filename becomes the invocation id (`@name`).

**Frontmatter:**

| Field | Required | Notes |
|---|---|---|
| `description` | Recommended | shown when selecting/routing |
| `mode` | No | `primary` \| `subagent` \| `all` (default `all`) |
| `model` | No | `provider/model` |
| `temperature` | No | 0.0–1.0 |
| `permission` | No | per-action `allow`\|`ask`\|`deny` or glob-map |
| `prompt` | Config-only | system instructions (in Markdown, the body) |
| `tools` | No | **legacy/deprecated** in favor of `permission` |

**Permission categories:** `read`, `edit`, `glob`, `grep`, `bash`, `task`, `skill`, `lsp`, `webfetch`, `websearch`, `external_directory`.

**Also relevant:** `AGENTS.md` at repo root — ambient workspace instructions (no required frontmatter). Useful as a "documentation completeness" input.

---

## 4. Normalized internal artifact schema (cross-tool)

Map every submission into this shape before scoring. This is what the rubric dimensions read.

```yaml
normalized_artifact:
  submission_id: string
  artifact_type: skill | copilot_agent | opencode_agent | source_project
  detected_standard: standard_a_claude_skill | standard_b_copilot_agent | standard_c_opencode | none
  files:
    entry_file: path            # SKILL.md | *.agent.md | *.md
    supporting: [paths]         # scripts/ references/ assets/
  identity:
    name: string | null
    name_valid: boolean         # kebab-case, <=64, matches dir (skills only)
    description: string | null
    description_len: integer
    description_valid: boolean
  prompt_body:
    present: boolean
    char_count: integer
    line_count: integer
  model: string | null
  tools_declared: [string]
  permissions: object | null    # opencode
  subagents: [string]
  portability: portable | platform_specific
  conformance:
    violations: [ {rule, severity: hard_fail|warn, detail, file_path, line} ]
```

### Field mapping cheat-sheet

| Normalized | Skill (A) | Copilot (B) | OpenCode (C) |
|---|---|---|---|
| identity.name | `name` | `name` (opt) | filename |
| identity.description | `description` | `description` | `description` |
| prompt_body | body | body (≤30k) | body / `prompt` |
| model | — | `model` | `model` |
| tools_declared | `allowed-tools` | `tools` | `tools` (legacy) / `permission` |
| subagents | — | `agents` | `permission.task` |
| permissions | — | — | `permission` |

### Universal minimum (applies to all three)
- A non-empty `description`.
- A non-empty instruction body defining role/behavior.
- No deprecated formats (`.chatmode.md`, OpenCode boolean `tools` map).

### Intranet / air-gap validation (flag, don't execute)
- Reject/flag tools or permissions enabling external networking (`webfetch`, `websearch`) unless whitelisted.
- Flag `edit`/`bash` permissions that are unrestricted (`allow` with no destructive-command guards).
