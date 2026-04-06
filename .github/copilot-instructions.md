---
name: Fei Copilot Skills Hub
description: Central repository for AI agent skills used across Fei organization. Use when working on Fei engineering tasks or extending agent capabilities.
---

# Fei Copilot Skills Hub

This repository is the centralized hub for GitHub Copilot agent skills used across the Fei organization. It provides safe, tested, and reusable skills that enhance developer productivity.

## Overview

The hub focuses on **Skills** - multi-step workflows with bundled templates and scripts for complex development tasks.

Skills are organized by domain: frontend, backend, devops, data, platform, security, ai.

## Installation

Clone this repository into your VS Code user prompts folder to install all skills:

```bash
git clone https://github.com/FeiWangHub/fei_skills_hub.git \
  ~/Library/Application\ Support/Code/User/prompts/fei-skills
```

After cloning, reload VS Code or run **Copilot: Reload Extensions** to activate.

### Alternative: Workspace-Level Installation

To use only within a specific workspace:

```bash
# In your workspace root
mkdir -p .github/skills

# Copy desired skills from this hub into .github/skills/
```

## Quick Start

### Using a Skill

Type `/` in Copilot Chat to see available skills. Select one and provide any required inputs.

### Environment

All skills are designed for **VS Code + GitHub Copilot Chat** and tested with Claude Haiku and Claude 3.5 Sonnet models.

## Structure

```
.github/
└── skills/
    ├── frontend/
    │   ├── react-component-gen/
    │   │   ├── SKILL.md
    │   │   ├── templates/
    │   │   └── scripts/
    │   └── ...
    ├── backend/
    ├── devops/
    ├── data/
    ├── platform/
    ├── security/
    └── ai/
```

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on:
- Creating new skills
- Testing and validation
- Submission and review process
- Naming conventions and best practices

## Skill Index

For a complete index of all available skills, see [SKILLS.md](./SKILLS.md).

## Support

- **Issues**: Report bugs or request new skills via GitHub Issues
- **Discussions**: Share feedback and ideas in Discussions
- **Contributing**: Submit improvements via pull requests

---

**Last updated**: April 2, 2026  
**Maintained by**: Fei Engineering Team
