# Fei Skills Hub

**A centralized, organized repository for AI agent skills designed for Fei engineers.**

---

## What is This?

This hub provides reusable, tested skills for AI coding assistants that enhance developer productivity across our teams. Instead of individuals creating their own workflows, we maintain a shared, curated collection that anyone can install and use.

### What Are Skills?

Skills are **multi-step workflows** with templates and helper scripts for complex development tasks (e.g., "Generate React components with tests", "Set up API contract testing", "Create deployment pipelines").

### Context

- **Internal use only**: This repository is for our engineers. All skills are designed with enterprise security and compliance requirements in mind, especially information security.
- **Intranet-friendly**: Skills do not depend on external services or require internet access beyond our internal network. They should work in restricted environments.
- **Tool-agnostic**: Skills are designed to work across multiple AI coding tools:
  - VS Code + GitHub Copilot Chat
  - IntelliJ IDEA + GitHub Copilot
  - Windsurf / Codeium / Cursor
  - Claude Code CLI
  - Gemini CLI
  - OpenCode
  - Any tool that supports `.prompt` or slash commands

### Supported Tools

| Tool | Prompt Location | Notes |
|------|----------------|-------|
| VS Code + Copilot | `prompts/` subdirectory of extensions directory | Works with `/` slash commands |
| IDEA + Copilot | Same as VS Code | JetBrains plugin respects workspace prompts |
| Claude Code | `~/.claude/` or workspace `.claude/` | Uses `.prompt` files |
| Gemini CLI | Workspace-local config | Similar slash command patterns |
| Windsurf / Cursor | IDE settings or workspace config | May require manual prompt import |

## Quick Start

### Installation

**Recommended: Clone + Run Install Script (One Command Per Platform)**

This handles all supported tools automatically via symlinks — no manual path guessing needed.

**macOS / Linux:**
```bash
git clone https://github.com/FeiWangHub/fei_skills_hub.git ~/fei-skills
cd ~/fei-skills
bash setup-for-agents.sh
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/FeiWangHub/fei_skills_hub.git $HOME\fei-skills
cd $HOME\fei-skills
.\setup-for-agents.ps1
```

The install script automatically creates symlinks to all detected AI coding tools on your machine. Restart your tool to see the skills.

#### Install Script Options

Both scripts support these flags:

| Flag | Description |
|------|-------------|
| `--dry-run` | Preview what would be created without making changes |
| `--force` | Overwrite existing symlinks/junctions |
| `--vscode` | Install only for VS Code + Copilot |
| `--claude` | Install only for Claude Code |
| `--cursor` | Install only for Cursor |
| `--windsurf` | Install only for Windsurf |
| `--intellij` | Install only for IntelliJ IDEA + Copilot |
| `--gemini` | Install only for Gemini CLI |
| `--opencode` | Install only for OpenCode |

**Examples:**
```bash
# Preview before installing
bash setup-for-agents.sh --dry-run

# Install only for Claude Code and VS Code
bash setup-for-agents.sh --claude --vscode

# Force reinstall (overwrite existing links)
bash setup-for-agents.sh --force

# Windows: Install only for IntelliJ
.\setup-for-agents.ps1 -IntelliJ
```

#### Alternative: Manual Clone to Specific Tool Paths

If you prefer manual installation, see [SETUP-GUIDE.md](./SETUP-GUIDE.md) for exact paths per tool.

#### Workspace-Level (Per Project)

Clone into your project's repo for project-specific skill usage:

```bash
cd your-project-repo/
git submodule add https://github.com/FeiWangHub/fei_skills_hub.git .github/skills/fei-skills
# OR without submodules:
git clone https://github.com/FeiWangHub/fei_skills_hub.git .github/skills/fei-skills
```

### Using a Skill

1. Open your AI coding assistant's chat
2. Type `/` to see available skills
3. Select a skill and follow the prompts

### Finding What You Need

- **Browse all skills**: See [SKILLS.md](./SKILLS.md) for a complete index
- **By domain**: Frontend, Backend, DevOps, Data, Platform, Security, AI/ML

## Repository Structure

```
fei-skills-repo/
├── .github/
│   └── skills/                 # Multi-step workflows
│       ├── frontend/
│       │   ├── react-component-gen/
│       │   │   ├── SKILL.md
│       │   │   ├── templates/
│       │   │   └── scripts/
│       │   └── ...
│       ├── backend/
│       ├── devops/
│       ├── data/
│       ├── platform/
│       ├── security/
│       └── ai/
├── .github/copilot-instructions.md   # Workspace configuration
├── SETUP-GUIDE.md              # Cross-tool installation guide
├── README.md                   # This file
├── CONTRIBUTING.md             # How to add new skills
├── SKILLS.md                   # Complete skills index
└── LICENSE
```

## Contributing

We welcome **new skills** from Fei engineers!

### Before You Create

Read [CONTRIBUTING.md](./CONTRIBUTING.md) to:
- Understand what makes a good skill
- Follow naming conventions and structure
- Write clear descriptions for discoverability
- Test locally before submitting
- Understand the review process

### Quick Example: Submitting a New Skill

1. Create folder: `.github/skills/backend/my-skill-name/`
2. Add `SKILL.md` with proper frontmatter
3. Add templates/ and scripts/ as needed
4. Test in VS Code
5. Open a PR with description

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed steps.

## FAQ

**Q: Which AI tool should I use?**  
A: We support them all. Pick the one you prefer — skills are designed to be tool-agnostic.

**Q: Can I use these outside of work?**  
A: These skills are designed for Fei work with enterprise security and compliance requirements. Personal use is fine if tools don't depend on internal systems or credentials.

**Q: Do skills work offline or on intranet?**  
A: Skills are designed to run in restricted environments. They don't call external URLs, download packages at runtime, or require internet access. Each skill documents its network requirements clearly.

**Q: How often are skills updated?**  
A: Skills are updated as needed. Check the repo for recent changes before using a skill in development. We recommend `git pull` periodically.

**Q: Can skills for different teams conflict?**  
A: Skills are organized by domain to avoid conflicts. If you find overlaps, open an Issue to discuss.

**Q: What if a skill stops working after a tool update?**  
A: Report the issue internally. Maintainers will investigate and patch as needed.

**Q: How do we handle security and compliance?**  
A: All skills pass through a security review before merging. Skills must not: send code or data to external endpoints, hardcode credentials, suggest insecure practices, or depend on unapproved external services.

## Security & Compliance

Skills targeting Fei environments must follow these rules:

1. **No external network calls**: Helper scripts should not curl/wget external APIs
2. **No credential storage**: Never include tokens, API keys, or certificates
3. **No external AI model calls**: Skills should not call other LLMs or AI APIs
4. **Composable and inspectable**: All templates and scripts must be human-readable
5. **Clear data boundaries**: Skills should document what data they read and write

## Support

- **Issues**: Report bugs, security concerns, or request new skills
- **Discussions**: Share feedback and ideas
- **Email**: [team contact, if applicable]

## Environment

- **IDEs**: VS Code, IntelliJ IDEA, Windsurf, Claude Code, Gemini CLI, OpenCode
- **AI Models**: Claude Haiku 4.5, Claude 3.5 Sonnet+, Gemini, and others (tested and supported)
- **Platforms**: macOS, Linux, Windows

## License

See the [MIT License](./LICENSE) file for details.

---

**Ready to use Copilot more effectively?** Head to [SKILLS.md](./SKILLS.md) to explore available skills, or [CONTRIBUTING.md](./CONTRIBUTING.md) to create your own!

**Last Updated**: April 2, 2026  
**Maintained by**: Fei Engineering Team
