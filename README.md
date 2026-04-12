# Fei Skills Hub

**A centralized, organized repository for AI agent skills designed exclusively for the IT Department of a Top 5 Global Multinational Bank.**

As a globally systemically important bank (G-SIB), strict adherence to security, data privacy, and regulatory compliance is paramount. Every skill in this repository is designed to operate securely within our air-gapped/restricted intranet environment and strictly prohibits external data exfiltration or unauthorized LLM API calls.

---

## What is This?

This hub provides reusable, tested skills for AI coding assistants that enhance developer productivity across our internal engineering teams. Instead of individuals creating their own workflows, we maintain a shared, curated, and security-approved collection that anyone in the bank can install and use.

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
git submodule add https://github.com/FeiWangHub/fei_skills_hub.git skills/fei-skills
# OR without submodules:
git clone https://github.com/FeiWangHub/fei_skills_hub.git skills/fei-skills
```

### Using a Skill

1. Open your AI coding assistant's chat
2. Type `/` to see available skills
3. Select a skill and follow the prompts

### Finding What You Need

- **Browse all skills**: See the **Available Skills** section below for a complete index
- **By domain**: Frontend, Backend, DevOps, Data, Platform, Security, AI/ML

## Available Skills

### Frontend
| Name | Description | Location |
|------|-------------|----------|
| ui-ux-pro-max | Comprehensive design guide for web and mobile applications | `skills/frontend/ui-ux-pro-max` |
| frontend-design | Anthropic's guide to creating distinctive, production-grade interfaces | `skills/frontend/frontend-design` |
| remotion-best-practices | Best practices for building programmatic videos using Remotion | `skills/frontend/remotion-best-practices` |

## Repository Structure

```text
fei-skills-repo/
├── skills/                     # Multi-step skills (Centralized for easy management)
│   ├── frontend/
│   │   └── ui-ux-pro-max/      # Comprehensive UI/UX design skill
│   │       ├── data/           # Local CSV database for design rules
│   │       ├── scripts/        # Python retrieval scripts
│   │       └── PROMPT.md       # Main skill definition prompt
│   └── _TEMPLATE.md            # Template for creating new skills
├── .github/
│   └── copilot-instructions.md # Workspace configuration
├── README.md                   # This file (Includes Installation and Skills index)
├── CONTRIBUTING.md             # How to add new skills
├── setup-for-agents.sh         # Installer for macOS / Linux
├── setup-for-agents.ps1        # Installer for Windows
└── LICENSE                     # License information
```

## Contributing

We welcome new skills from Fei engineers! Ensure your contributions meet our security standards:
- **No external network calls or AI APIs** in scripts/templates.
- **No credential storage** or hardcoded tokens.
- **Clear data boundaries** and offline intranet compatibility.

To add a new skill:
1. Use `skills/_TEMPLATE.md` to create your `SKILL.md` in the appropriate domain folder (e.g., `skills/backend/my-skill/`).
2. Add necessary `templates/` and `scripts/`.
3. Test locally in your AI tool.
4. Submit a PR for security review.

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

---

## Appendix: Install Script Source Code

The installation scripts `setup-for-agents.sh` and `setup-for-agents.ps1` are located in the root of this repository. They handle automatic symlinking/junction creation across macOS, Linux, and Windows for all supported tools. Feel free to inspect them directly if you wish to see how the paths are resolved.

