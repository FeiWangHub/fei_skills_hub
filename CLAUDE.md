# Fei Skills Hub — CLAUDE.md

> **Note:** This file provides context for Claude Code (and other AI agents) working in this repository. For human-readable project docs, see [`README.md`](./README.md).

## What Is This Repository

**Fei Skills Hub** is a curated, tool-agnostic collection of AI agent skills for developer productivity. It follows the [`.agents` Protocol](https://dotagentsprotocol.com/), providing a portable `.agents/` directory that can be linked to `~/.agents` for system-wide agent use.

### Key Facts

- **Purpose:** Centralized, skills library for AI coding assistants
- **Audience:** IT engineers at a top-5 global multinational bank (G-SIB)
- **Security-first:** All skills must be air-gapped/intranet-compatible; no external data exfiltration, no hardcoded credentials
- **Tool-agnostic:** Works with Claude Code, GitHub Copilot (VS Code / IntelliJ), Gemini CLI, Cursor, Windsurf, OpenCode
- **License:** MIT

## Directory Structure

```
fei_skills_hub/
├── .agents/                    # The .agents Protocol notebook (source of truth)
│   ├── agents.md               # Global agent instructions (AGENTS.md-compatible)
│   ├── system-prompt.md        # System prompt template
│   ├── mcp.json                # MCP server configuration (currently empty)
│   ├── models.json             # Model presets & provider keys (currently empty)
│   ├── skills/                 # All skills live here, organized by domain
│   │   ├── _TEMPLATE.md        # Template for creating new skills
│   │   ├── frontend/           # 4 skills (frontend-design, remotion-best-practices, tailwind-design-system, ui-ux-pro-max)
│   │   ├── backend/            # 4 skills (fastapi-templates, java-springboot, nodejs-backend-patterns, supabase-postgres)
│   │   ├── tooling/            # 5 skills (api-design-principles, dependency-upgrade, find-skills, github-copilot-starter, skill-creator)
│   │   ├── documents/          # 3 skills (docx, pdf, pptx)
│   │   ├── security/           # 1 skill (skill-security-reviewer)
│   │   ├── cloud/              # 1 skill (cost-optimization)
│   │   ├── automation/         # 1 skill (browser-use)
│   │   ├── documentation/      # 1 skill (openapi-spec-generation)
│   │   ├── languages/          # 1 skill (python-performance-optimization)
│   │   ├── ai/                 # (empty, reserved)
│   │   ├── data/               # (empty, reserved)
│   │   ├── devops/             # (empty, reserved)
│   │   ├── infrastructure/     # (empty, reserved)
│   │   ├── mobile/             # (empty, reserved)
│   │   └── platform/           # (empty, reserved)
│   ├── agents/                 # Sub-agent profiles (currently empty)
│   ├── tasks/                  # Scheduled repeat tasks (currently empty)
│   └── memories/               # Persistent memory (currently empty)
├── .claude/                    # Claude Code local config
│   └── settings.local.json     # Claude-specific permissions
├── .github/
│   ├── copilot-instructions.md # GitHub Copilot workspace config
│   └── workflows/              # CI/CD workflows
├── artifacts/                  # Presentation and build artifacts
├── docs/                       # Extra documentation (top-100 skills list)
├── init-dot-agents.sh          # macOS/Linux initializer script
├── init-dot-agents.ps1         # Windows initializer script
├── CHANGELOG.md                # Project changelog (Keep a Changelog format)
├── README.md                   # Full project documentation
└── LICENSE                     // MIT License
```

## Skill Anatomy

Each skill is a directory containing at minimum a `SKILL.md` file:

```
.agents/skills/<domain>/<skill-name>/
├── SKILL.md          # Required — frontmatter (name, description) + instructions
├── templates/        # Optional — file templates used by the skill
├── scripts/          # Optional — helper scripts (Python, Bash, etc.)
├── agents/           # Optional — sub-agent definitions
├── references/       # Optional — reference docs
└── assets/           # Optional — static assets
```

The `SKILL.md` frontmatter **must** include `name` and `description` fields. The description drives skill triggering — it should clearly state when the skill should be used. See `.agents/skills/_TEMPLATE.md` for the full template.

## Common Tasks

### Adding a New Skill

1. Create a new directory under `.agents/skills/<domain>/`
2. Use `.agents/skills/_TEMPLATE.md` as your starting point
3. Write the `SKILL.md` with clear frontmatter (`name`, `description`)
4. Add any `templates/`, `scripts/`, or other supporting files
5. Update the skills table in `README.md`
6. No external network calls, credential storage, or hardcoded tokens are permitted

### Installing Skills Locally

**macOS / Linux:**
```bash
git clone https://github.com/FeiWangHub/fei_skills_hub.git ~/fei-skills
cd ~/fei-skills
bash init-dot-agents.sh

# Optional: link to ~/.agents for global use
ln -s "$PWD/.agents" "$HOME/.agents"
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/FeiWangHub/fei_skills_hub.git $HOME\fei-skills
cd $HOME\fei-skills
.\init-dot-agents.ps1

# Optional: junction to ~/.agents
New-Item -ItemType Junction -Path "$HOME\.agents" -Target "$PWD\.agents"
```

### Running the Initializer

The init scripts support three modes:
- **Interactive** (default): prompts for each action
- **`--auto`**: creates/updates everything without prompting
- **`--dry-run`**: previews actions without making changes

## Architecture & Conventions

### Design Principles

- **Tool-agnostic:** Skills use Markdown-based `SKILL.md` files, not tool-specific formats. They should work across Claude Code, Copilot, Gemini CLI, etc.
- **Security-first:** All skills are designed for restricted intranet environments. No external API calls, no runtime package downloads, no credential storage.
- **Self-contained:** Each skill carries its own templates, scripts, and references.

### Naming Conventions

- Skill directories: lowercase with hyphens (e.g., `frontend-design`, `api-design-principles`)
- Domain folders: singular nouns (e.g., `backend/`, `frontend/`, `cloud/`)
- `SKILL.md` is always uppercase

### Branch / Commit Conventions

- Use descriptive commit messages following conventional patterns
- Security review is required before merging new skills

## Security Requirements (Critical)

All skills and contributions **must** comply with:

1. **No external network calls** or AI API invocations in scripts/templates
2. **No credential storage** — no hardcoded tokens, API keys, or passwords
3. **No data exfiltration** — code and data must never be sent to external endpoints
4. **Clear data boundaries** — each skill documents its network requirements
5. **Offline/intranet compatibility** — skills must function without internet access

Violations should be reported immediately and block any PR from merging.

## Claude Code Configuration

The `.claude/settings.local.json` file contains Claude-specific permissions (currently allows `WebSearch`, `git add`, `gh api`, and `git commit` commands). This file is gitignored and should not be committed.

## Useful References

- [`.agents` Protocol Specification](https://dotagentsprotocol.com/)
- [Skill Template](.agents/skills/_TEMPLATE.md)
- [README.md](README.md) — full documentation, skills index, FAQ
- [CHANGELOG.md](CHANGELOG.md) — recent changes
