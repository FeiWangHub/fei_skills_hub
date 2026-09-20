# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Initial repository structure
- .agents initializer scripts (`init-dot-agents.sh` / `init-dot-agents.ps1`)
  - Creates or updates `./.agents` following https://dotagentsprotocol.com/
  - Flags: `--dry-run`, `--auto`
- Skill template at `.agents/skills/_TEMPLATE.md`
- Contributing guide (CONTRIBUTING.md)
- Setup guide (SETUP-GUIDE.md)
- Skills index (SKILLS.md)
- Copilot workspace configuration (`.github/copilot-instructions.md`)

## [0.1.0] - 2026-05-11

### Added

- Add OpenCode GitHub Actions workflows
- Install opencode agent
- Add 8 skills from ~/.agents/skills with categorized structure
- Add initialization scripts for ~/.agents directory structure and update setup scripts for agent home integration
- Add java-springboot best practices skill
- Sync local remotion-best-practices rules and update SKILL.md
- Add security reviewer and frontend design skills
- Initial commit of fei-skill-hub
- Embed full install scripts in README appendix
- Add install scripts to README, fix license placeholder

### Fixed

- Add use_github_token and git author config for changelog workflow
- Switch model to opencode/minimax-m2.5-free
- Remove external google fonts import in remotion assets to comply with internal security policy

### Improved

- Streamline repository structure and documentation for enterprise compliance
- Add .gitattributes for consistent line endings
