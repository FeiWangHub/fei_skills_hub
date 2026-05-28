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

## The `.agents` Protocol Environment

This project fully embraces the open [.agents Protocol](https://dotagentsprotocol.com/), serving as a centralized, tool-agnostic configuration hub for all your AI agents.

By using our initialization scripts (`init-dot-agents.sh` or `init-dot-agents.ps1`), you can scaffold a standard `.agents` directory structure in your repo (and optionally link it to `~/.agents`):

```text
.agents/
├── agents.md            # global agent instructions
├── system-prompt.md     # system prompt template
├── speakmcp-settings.json # general settings
├── mcp.json             # MCP server configuration
├── models.json          # model presets & provider keys
├── layouts/             # UI/layout preferences
├── skills/              # codified procedural knowledge
├── agents/              # sub-agent profiles
├── tasks/               # scheduled repeat tasks
├── memories/            # persistent memory
├── knowledge/           # optional free-form notes
└── .backups/            # optional local backups
```

This layout ensures your skills, sub-agents, tasks, and memories are portable and instantly available to any compatible AI IDE or CLI (like Claude Code, Cursor, OpenCode, etc.).

## Quick Start

### 1. Create or Update `./.agents` (Recommended)

This repo includes a `.agents` directory. Run the initializer to update it (or fill in missing pieces):

**macOS / Linux:**
```bash
git clone https://github.com/FeiWangHub/fei_skills_hub.git ~/fei-skills
cd ~/fei-skills
bash init-dot-agents.sh
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/FeiWangHub/fei_skills_hub.git $HOME\fei-skills
cd $HOME\fei-skills
.\init-dot-agents.ps1
```

### 2. Use as Your Global `~/.agents` (Optional)

**macOS / Linux:**
```bash
ln -s "$PWD/.agents" "$HOME/.agents"
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Junction -Path "$HOME\.agents" -Target "$PWD\.agents"
```

### Using a Skill

1. Open your AI coding assistant's chat
2. Type `/` to see available skills
3. Select a skill and follow the prompts

### Finding What You Need

- **Browse all skills**: See the **Available Skills** section below for a complete index
- **By domain**: Frontend, Backend, DevOps, Data, Platform, Security, AI/ML

## Available Skills

| Name | Description | Location |
|------|-------------|----------|
| api-design-principles | Master REST and GraphQL API design principles to build intuitive, scalable, and maintainable APIs that delight developers. Use when designing new APIs, reviewing API specifications, or establishing API design standards. | `.agents/skills/tooling/api-design-principles` |
| nodejs-backend-patterns | Build production-ready Node.js backend services with Express/Fastify, implementing middleware patterns, error handling, authentication, database integration, and API design best practices. Use when creating Node.js servers, REST APIs, GraphQL backends, or microservices architectures. | `.agents/skills/backend/nodejs-backend-patterns` |
| openapi-spec-generation | Generate and maintain OpenAPI 3.1 specifications from code, design-first specs, and validation patterns. Use when creating API documentation, generating SDKs, or ensuring API contract compliance. | `.agents/skills/documentation/openapi-spec-generation` |
| browser-use | Automates browser interactions for web testing, form filling, screenshots, and data extraction. Use when the user needs to navigate websites, interact with web pages, fill forms, take screenshots, or extract information from web pages. | `.agents/skills/automation/browser-use` |
| cost-optimization | Optimize cloud costs across AWS, Azure, GCP, and OCI through resource rightsizing, tagging strategies, reserved instances, and spending analysis. Use when reducing cloud expenses, analyzing infrastructure costs, or implementing cost governance policies. | `.agents/skills/cloud/cost-optimization` |
| dependency-upgrade | Manage major dependency version upgrades with compatibility analysis, staged rollout, and comprehensive testing. Use when upgrading framework versions, updating major dependencies, or managing breaking changes in libraries. | `.agents/skills/tooling/dependency-upgrade` |
| docx | Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files). Triggers include: any mention of 'Word doc', 'word document', '.docx', or requests to produce professional documents with formatting like tables of contents, headings, page numbers, or letterheads. Also use when extracting or reorganizing content from .docx files, inserting or replacing images in documents, performing find-and-replace in Word files, working with tracked changes or comments, or converting content into a polished Word document. If the user asks for a 'report', 'memo', 'letter', 'template', or similar deliverable as a Word or .docx file, use this skill. Do NOT use for PDFs, spreadsheets, Google Docs, or general coding tasks unrelated to document generation. | `.agents/skills/documents/docx` |
| fastapi-templates | Create production-ready FastAPI projects with async patterns, dependency injection, and comprehensive error handling. Use when building new FastAPI applications or setting up backend API projects. | `.agents/skills/backend/fastapi-templates` |
| find-skills | Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill. | `.agents/skills/tooling/find-skills` |
| frontend-design | Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, artifacts, posters, or applications (examples include websites, landing pages, dashboards, React components, HTML/CSS layouts, or when styling/beautifying any web UI). Generates creative, polished code and UI design that avoids generic AI aesthetics. | `.agents/skills/frontend/frontend-design` |
| github-copilot-starter | 'Set up complete GitHub Copilot configuration for a new project based on technology stack' | `.agents/skills/tooling/github-copilot-starter` |
| java-springboot | Guidelines and best practices for writing high-quality Spring Boot applications. Covers project structure, dependency injection, configuration, security, and testing. | `.agents/skills/backend/java-springboot` |
| pdf | Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables from PDFs, combining or merging multiple PDFs into one, splitting PDFs apart, rotating pages, adding watermarks, creating new PDFs, filling PDF forms, encrypting/decrypting PDFs, extracting images, and OCR on scanned PDFs to make them searchable. If the user mentions a .pdf file or asks to produce one, use this skill. | `.agents/skills/documents/pdf` |
| pptx | Use this skill any time a .pptx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; working with templates, layouts, speaker notes, or comments. Trigger whenever the user mentions "deck," "slides," "presentation," or references a .pptx filename, regardless of what they plan to do with the content afterward. If a .pptx file needs to be opened, created, or touched, use this skill. | `.agents/skills/documents/pptx` |
| python-performance-optimization | Profile and optimize Python code using cProfile, memory profilers, and performance best practices. Use when debugging slow Python code, optimizing bottlenecks, or improving application performance. | `.agents/skills/languages/python-performance-optimization` |
| remotion-best-practices | Best practices for Remotion - Video creation in React | `.agents/skills/frontend/remotion-best-practices` |
| skill-creator | Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy. | `.agents/skills/tooling/skill-creator` |
| supabase-postgres-best-practices | Postgres performance optimization and best practices from Supabase. Use this skill when writing, reviewing, or optimizing Postgres queries, schema designs, or database configurations. | `.agents/skills/backend/supabase-postgres-best-practices` |
| tailwind-design-system | Build scalable design systems with Tailwind CSS v4, design tokens, component libraries, and responsive patterns. Use when creating component libraries, implementing design systems, or standardizing UI patterns. | `.agents/skills/frontend/tailwind-design-system` |
| ui-ux-pro-max | Comprehensive design guide for web and mobile applications | `.agents/skills/frontend/ui-ux-pro-max` |

## Repository Structure

```text
fei-skills-repo/
├── .agents/                    # Your personal agent notebook (source of truth)
│   ├── agents.md
│   ├── system-prompt.md
│   ├── speakmcp-settings.json
│   ├── mcp.json
│   ├── models.json
│   ├── layouts/
│   ├── skills/                 # Skills live here
│   │   ├── frontend/
│   │   │   └── ui-ux-pro-max/
│   │   └── _TEMPLATE.md
│   ├── agents/
│   ├── tasks/
│   ├── memories/
│   ├── knowledge/
│   └── .backups/
├── .github/
│   └── copilot-instructions.md # Workspace configuration
├── README.md                   # This file (Includes Installation and Skills index)
├── CONTRIBUTING.md             # How to add new skills
├── init-dot-agents.sh          # Initialize ./\.agents on macOS / Linux
├── init-dot-agents.ps1         # Initialize ./\.agents on Windows
└── LICENSE                     # License information
```

## Contributing

We welcome new skills from Fei engineers! Ensure your contributions meet our security standards:
- **No external network calls or AI APIs** in scripts/templates.
- **No credential storage** or hardcoded tokens.
- **Clear data boundaries** and offline intranet compatibility.

To add a new skill:
1. Use `.agents/skills/_TEMPLATE.md` to create your `skill.md` in the appropriate domain folder (e.g., `.agents/skills/backend/my-skill/`).
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

## Appendix: Script Source Code

The initialization scripts (`init-dot-agents.sh` and `init-dot-agents.ps1`) are located in the root of this repository. They handle creating (or filling in missing pieces of) the `.agents Protocol` directory structure under `./.agents`. Feel free to inspect them directly if you wish to see how the structure is resolved.
