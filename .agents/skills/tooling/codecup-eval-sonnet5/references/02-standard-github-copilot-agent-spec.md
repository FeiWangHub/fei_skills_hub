# Standard B — GitHub Copilot Agent & Customization Specification

**Sources**: GitHub official docs — [Custom agents configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration), [Customization cheat sheet](https://docs.github.com/en/copilot/reference/customization-cheat-sheet), [Adding repository custom instructions](https://docs.github.com/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot), [Customizing the Cloud Agent environment](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/customize-the-agent-environment), [Best practices for Copilot coding agent tasks](https://docs.github.com/copilot/how-tos/agents/copilot-coding-agent/best-practices-for-using-copilot-to-work-on-tasks).

Use this document when scoring a **GitHub Copilot Agent submission** for schema conformance.

---

## 1. File Locations & Naming Conventions

| Config Type | Path(s) | Naming Rule | Scope / Trigger |
|---|---|---|---|
| Custom Agent Profile | `.github/agents/<name>.md` or `.github/agents/<name>.agent.md`; org-level `/agents/<name>.md` in `.github`/`.github-private`; user-level `~/.copilot/agents/<name>.agent.md` | alphanumeric + `.` `-` `_` | Explicit selection (`/agent`) or auto-invoked by Copilot Cloud Agent |
| Repo-wide Custom Instructions | `.github/copilot-instructions.md` | exact filename | Auto-injected into every interaction in the repo |
| Path-Specific Instructions | `.github/instructions/**/*.instructions.md` | must end `.instructions.md` | Injected only when files matching `applyTo` glob are in scope |
| Agent/Standards Instructions | `AGENTS.md` (root or nested); also recognizes `CLAUDE.md`, `GEMINI.md` | exact filename | Auto-loaded by Copilot Coding Agent; nearest nested file wins |
| Prompt Files | `.github/prompts/*.prompt.md` | must end `.prompt.md` | Manual `/prompt-name` trigger in IDE chat |
| Agent Skills | `.github/skills/<name>/SKILL.md` (also recognizes `.agents/skills/...` and `.claude/skills/...`) | dir `<name>`, file `SKILL.md` | Auto-selected by Copilot when relevant |
| Cloud Agent Environment Setup | `.github/workflows/copilot-setup-steps.yml` | exact path, default branch | Actions workflow run before Cloud Agent starts |

---

## 2. Frontmatter Schema — Custom Agent Profile

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | No (defaults to filename) | Agent display name |
| `description` | string | **Yes** | Clear statement of capabilities/scope |
| `target` | string | No | `"vscode"` \| `"github-copilot"` (default: both) |
| `model` | string | No | Model identifier; inherits default if unset |
| `tools` | array or CSV string | No | Default `["*"]`. See tool alias table below |
| `disable-model-invocation` | boolean | No | Default `false`; replaces retired `infer` field |
| `user-invocable` | boolean | No | Default `true`; `false` = programmatic-only |
| `mcp-servers` | object | No | Cloud Agent MCP server configs (type, command, args, tools, env) |
| `metadata` | object | No | Free-form key-value metadata |

**Standard tool aliases**: `execute` (shell/Bash/PowerShell), `read` (file read), `edit` (write/edit/patch), `search` (grep/glob), `agent` (invoke subagents), `web` (web search/fetch), `todo` (task tracking), plus namespaced MCP tools `<mcp-server>/<tool-name>`.

**Body limit**: prompt body max ~30,000 characters.

---

## 3. Frontmatter Schema — Path-Specific Instructions

| Field | Type | Required | Notes |
|---|---|---|---|
| `applyTo` | string | **Yes** | Comma-separated glob patterns, e.g. `"**/*.{ts,tsx},src/controllers/**/*.js"` |
| `excludeAgent` | string | No | `"code-review"` \| `"cloud-agent"` |

---

## 4. Cloud Agent Setup Workflow Requirements

- File **must** live at `.github/workflows/copilot-setup-steps.yml` on the default branch.
- Job **must** be named exactly `copilot-setup-steps`.
- Should install dependencies deterministically (pinned versions, lockfiles) so the Cloud Agent environment is reproducible.

---

## 5. Official Best Practices (used for the "quality" sub-score, not just the gate)

1. **Three-tier instruction structure**: (a) high-level repo summary/architecture/runtime versions, (b) deterministic build/test/lint/validate command sequences, (c) project layout / where configs and test harnesses live.
2. **Deterministic, copy-pasteable commands** — not "run the tests" but the literal CLI invocation (`npm run test:unit`, `mvn test -Dtest=*UnitTest`).
3. **Scoping & modularity** — repo-wide file kept short (<2 pages); framework/directory-specific rules pushed into `.github/instructions/*.instructions.md` with `applyTo`; tool-restricted agents (e.g. read-only reviewer with `tools: ["read","search"]`) used where appropriate.
4. **Secrets handling** — always `${{ secrets.VAR_NAME }}` references, never hardcoded credentials in any instruction/config file.

---

## 6. Machine-Checkable Conformance Rules (Hard Gate)

1. If claiming to be a Custom Agent Profile: file exists under a recognized `.github/agents/` (or user/org equivalent) path; frontmatter parses as YAML; `description` present and non-empty.
2. If claiming repo-wide instructions: `.github/copilot-instructions.md` exists at repo root.
3. If claiming path-specific instructions: file ends in `.instructions.md`; `applyTo` field present and is a valid glob-pattern string.
4. If claiming a Cloud Agent setup workflow: file at `.github/workflows/copilot-setup-steps.yml`; job name literally `copilot-setup-steps`.
5. `tools`/`mcp-servers` fields, if present, must not grant unrestricted `["*"]` execute/write access without an explicit justification comment — flag (do not hard-fail) for security-dimension review.
6. No `${{ secrets.* }}` value is hardcoded as a literal string anywhere in the scanned files (this overlaps with `05-security-static-checklist.md`).

## 7. Canonical Example (Illustrative Only)

```yaml
---
name: security-auditor
description: Analyzes pull requests for auth issues
target: github-copilot
model: claude-3.7-sonnet
tools: ["read", "search", "github/*"]
disable-model-invocation: false
user-invocable: true
metadata:
  version: "1.0.0"
---
```

> Illustrative frontmatter only — not an executable script.
