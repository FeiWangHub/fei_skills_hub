# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- feat: add OpenCode GitHub Actions workflows
- feat: add 8 skills from ~/.agents/skills with categorized structure
- feat: add initialization scripts for ~/.agents directory structure and update setup scripts for agent home integration
- feat: add java-springboot best practices skill
- feat: sync local remotion-best-practices rules and update SKILL.md
- feat: add security reviewer and frontend design skills

### Fixed

- fix: add use_github_token and git author config for changelog workflow
- fix: switch model to opencode/minimax-m2.5-free
- fix: remove external google fonts import in remotion assets to comply with internal security policy

### Changed

- AI: install opencode agent
- refactor: streamline repository structure and documentation for enterprise compliance
- chore: add .gitattributes for consistent line endings

### Documentation

- docs: embed full install scripts in README appendix
- docs: add install scripts to README, fix license placeholder

## [Unreleased] (initial content)

### Added

- Initial repository structure
- Cross-tool install scripts (`setup-for-agents.sh` / `setup-for-agents.ps1`)
  - Supports: VS Code, Claude Code, Cursor, Windsurf, IntelliJ IDEA, Gemini CLI, OpenCode
  - Flags: `--dry-run`, `--force`, per-tool selection
- Skill template at `.github/skills/_TEMPLATE.md`
- Contributing guide (CONTRIBUTING.md)
- Setup guide (SETUP-GUIDE.md)
- Skills index (SKILLS.md)
- Copilot workspace configuration (`.github/copilot-instructions.md`)