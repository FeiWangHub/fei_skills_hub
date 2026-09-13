# Standard C — OpenCode Agent / Skill / AGENTS.md Specification

**Sources**: [opencode.ai/docs](https://opencode.ai/docs), `sst/opencode` source (`packages/core/src/v1/config/agent.ts`, `packages/core/src/v1/config/permission.ts`, `packages/opencode/src/agent/agent.ts`, `packages/opencode/src/skill/index.ts`, `packages/opencode/src/session/instruction.ts`), and the cross-vendor `AGENTS.md` / `.agents` protocol ([dotagentsprotocol.com](https://dotagentsprotocol.com/)).

Use this document when scoring an **OpenCode Agent or OpenCode Skill submission** for schema conformance. OpenCode's `permission` model is particularly relevant to the **security dimension** — see §4.

---

## 1. OpenCode Agent Specification

### 1.1 File Locations
- Project agents: `.opencode/agent/*.md` or `.opencode/agents/*.md`
- Global agents: `~/.config/opencode/agent/*.md` or `~/.config/opencode/agents/*.md`
- Or defined inline in `opencode.json`/`opencode.jsonc` under the `"agent"` key
- Filename (minus `.md`) becomes the agent identifier

### 1.2 Frontmatter Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `description` | string | Recommended | When/why to invoke this agent (used for subagent routing) |
| `mode` | `"subagent"` \| `"primary"` \| `"all"` | Optional (default `"all"`) | `primary`=top-level interactive; `subagent`=dispatched via `@agent`/background task; `all`=both |
| `model` | string | Optional | `provider/model`, e.g. `anthropic/claude-3-7-sonnet` |
| `variant` | string | Optional | Reasoning variant (`high`, `medium`, `thinking`) |
| `temperature` | number | Optional | Sampling temperature |
| `top_p` | number | Optional | Nucleus sampling parameter |
| `steps` | positive int | Optional | Max agentic tool-call iterations before forced text response (replaces deprecated `maxSteps`) |
| `color` | string | Optional | Hex color or theme alias |
| `hidden` | boolean | Optional | Hide from `@` autocomplete (subagents only) |
| `disable` | boolean | Optional | Disable this agent |
| `permission` | object | Optional | Tool authorization ruleset — see §1.3 |
| `options` | object | Optional | Provider-specific params; unrecognized keys auto-collected here |
| `prompt` | string | Optional (JSON config only) | System prompt string or `{file:./prompts/x.txt}`; in Markdown files the body below frontmatter IS the prompt |
| `tools` | map (string→boolean) | *Deprecated* | Legacy; normalized to `permission` automatically |

### 1.3 Tool Permission Schema (`permission`)

Actions: `"allow" | "ask" | "deny"`.

Gated operations: `read`, `edit`, `glob`, `grep`, `list`, `bash`, `task` (subagent launching), `skill` (skill activation), `external_directory`, `todowrite`, `lsp`, `question`, `webfetch`, `websearch`, `doom_loop`.

Keys `read/edit/glob/grep/list/bash/task/external_directory/lsp/skill` accept either a single action string OR a pattern-map object, e.g.:

```yaml
permission:
  edit: deny
  bash:
    "*": deny
    "git diff*": allow
    "git log*": allow
  webfetch: deny
  websearch: deny
```

> **Security scoring relevance**: an OpenCode Agent submission that declares `bash: { "*": "allow" }` or `webfetch: allow`/`websearch: allow` without narrow scoping should be flagged in the security dimension — broad shell/network permission with no justification is a red flag in an air-gapped bank environment.

---

## 2. OpenCode Skill Specification

### 2.1 File Locations (discovery order)
1. `.opencode/skill/<name>/SKILL.md` or `.opencode/skills/<name>/SKILL.md` (project)
2. `~/.config/opencode/skills/<name>/SKILL.md` (global)
3. `.agents/skills/<name>/SKILL.md` / `~/.agents/skills/<name>/SKILL.md` (`.agents` protocol fallback)
4. `.claude/skills/<name>/SKILL.md` / `~/.claude/skills/<name>/SKILL.md` (Claude Code fallback)
5. Explicit `"skills": { "paths": [...], "urls": [...] }` in `opencode.json`

### 2.2 Frontmatter Fields

| Field | Type | Required | Validation |
|---|---|---|---|
| `name` | string | **Yes** | 1–64 chars, `^[a-z0-9]+(-[a-z0-9]+)*$`, must match directory name |
| `description` | string | **Yes** | 1–1024 chars, trigger-oriented |
| `license` | string | No | e.g. `MIT` |
| `compatibility` | string | No | Typically `opencode` |
| `metadata` | map(string→string) | No | Free-form |
| `opencode/autoinvoke` | boolean | No | `false` hides from auto-listing (manual invocation still works) |

### 2.3 Directory Structure

```text
.opencode/skills/<skill-name>/
├── SKILL.md
├── templates/
├── scripts/
├── references/
└── assets/
```

---

## 3. `AGENTS.md` / `.agents` Protocol Conventions

### 3.1 Resolution Precedence
1. Project root: `AGENTS.md` → fallback `CLAUDE.md` → legacy fallback `CONTEXT.md`
2. Global: `~/.config/opencode/AGENTS.md` → fallback `~/.claude/CLAUDE.md`
3. Explicit list in `opencode.json` → `"instructions": [...]` (files or URLs)

### 3.2 Monorepo Composition
Nearest-wins, additive layering: root `AGENTS.md` = global baseline; nested `services/x/AGENTS.md` = local overrides/additions, discovered as the agent traverses into that directory.

### 3.3 Expected Sections for a Well-Authored `AGENTS.md` (used for the docs-quality sub-score)
1. Project overview & architecture (non-obvious patterns, key entry points)
2. Build/test/validate commands (exact CLI invocations)
3. Coding standards & conventions
4. Security & data boundaries (air-gap rules, no-external-call policy, secret handling)
5. Progressive-disclosure pointers to deep-dive docs

---

## 4. Machine-Checkable Conformance Rules (Hard Gate)

1. **Agent**: file at `.opencode/agent(s)/*.md` or global equivalent; frontmatter parses as YAML; `mode` (if present) is one of `subagent|primary|all`; `model` (if present) matches `^[a-z0-9_.-]+/[a-z0-9_.:-]+$`; non-empty Markdown body below frontmatter.
2. **Agent security flag (not hard-fail, routed to security dimension)**: `permission.bash` resolves to blanket `allow` for `"*"`, OR `permission.webfetch`/`permission.websearch` is `allow` with no narrowing — flag as "broad permission grant, review required".
3. **Skill**: file at `.opencode/skill(s)/<name>/SKILL.md` (or `.agents/skills/<name>/SKILL.md`), directory name equals `name` field; `name` matches `^[a-z0-9]+(-[a-z0-9]+)*$`, ≤64 chars; `description` present, 1–1024 chars.
4. **AGENTS.md**: file exists; not empty; recommend (not require) presence of the 5 sections in §3.3 — scored under documentation dimension, not the hard gate.

## 5. Canonical Example (Illustrative Only)

```yaml
---
description: Static code security analyzer for vulnerability scanning and credential leak prevention
mode: subagent
model: anthropic/claude-3-7-sonnet
temperature: 0.1
steps: 15
color: error
permission:
  edit: deny
  bash:
    "*": deny
    "git diff*": allow
    "git log*": allow
  webfetch: deny
  websearch: deny
---
```

> Illustrative frontmatter only — not an executable script.
