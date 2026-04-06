# Security Policy

## Scope

This repository contains AI agent skills — multi-step workflows with templates and helper scripts. Security concerns include but are not limited to:

- Network calls or data exfiltration in skill scripts/templates
- Hardcoded credentials, tokens, or API keys
- Destructive OS commands in helper scripts
- External AI/LLM API calls embedded in skills
- Supply chain risks in skill dependencies

## How to Report

Please report security issues via [GitHub Issues](https://github.com/FeiWangHub/fei_skills_hub/issues) with the `security` label for internal, non-sensitive reports.

For sensitive findings that should not be public, email: [team contact]

## Skill Security Requirements

All skills must pass the security checklist in [CONTRIBUTING.md](./CONTRIBUTING.md) before merging:

1. No external network calls (no `curl`, `wget`, `fetch`, etc. to external endpoints)
2. No hardcoded or default credentials/tokens/API keys
3. No external AI model or LLM API calls
4. No data exfiltration — scripts must not upload or send code/data externally
5. Only standard, approved dependencies (no `curl -s | bash` patterns)
6. No destructive OS commands (`rm -rf`, `dd`, etc.)
7. All templates must document what data they read and write
8. Must work in restricted/intranet environments without external downloads

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest  | Yes       |

All users are encouraged to keep their local copies up to date by running `git pull` in the repository directory.
