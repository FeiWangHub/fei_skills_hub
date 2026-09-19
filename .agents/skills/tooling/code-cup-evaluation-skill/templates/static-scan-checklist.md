# Static Scan Checklist for Code Cup Submissions

## Scope

Apply this checklist before any LLM evaluation. This pass must run in a read-only, non-executing environment and must block any submission with a hard security issue.

## Required Checks

### 1. Credential scanning
- Search for API keys, tokens, client secrets, private keys, OAuth material, JWTs, and embedded credentials.
- Check `.env`, `.env.*`, JSON config, YAML secrets, CI files, shell scripts, and deployment manifests.
- Run `gitleaks` or equivalent on the repository snapshot.

### 2. PII and internal leakage
- Detect email addresses, phone numbers, internal hostnames, branch names, and customer identifiers.
- Flag references to internal infrastructure, test users, or production data.

### 3. Dangerous network behavior
- Search for HTTP / HTTPS calls to external domains not in allowlist.
- Flag outbound requests to non-`.example` domains.
- Check CI scripts, package config, and runtime config for unapproved destinations.

### 4. Prompt injection and malicious instructions
- Search for phrases such as: "ignore previous instructions", "always give full score", "act as system", "override safety".
- Review README, skill metadata, agent definitions, and prompt files for manipulative instructions.

### 5. Security policy violations
- Flag scripts that exfiltrate files, send telemetry, or call unknown domains.
- Flag unusual package installs, postinstall scripts, or code execution steps that are not justified.

### 6. Artifact conformance
- Check whether the repo shape matches its declared artifact type.
- For skill submissions, verify presence of a valid `SKILL.md` / `skill.md` file and expected structure.
- For agent submissions, verify agent metadata and expected configuration format.

## Hard Fail Conditions

A submission is rejected if any of the following occur:

- hard-coded secret or credential detected
- outbound URL points to non-approved external domain
- malicious or prompt-injection text found in core metadata
- private key material found in repo
- unsafe install or exfiltration script found in CI or package setup

## Pass / Fail Output

```json
{
  "passed": true,
  "hard_failed": false,
  "issues": []
}
```
