# Contributing to Fei Copilot Skills Hub

Thank you for contributing to the Fei Copilot Skills Hub! This guide explains how to create, test, and submit new skills.

## Before You Start

Familiarize yourself with what skills are:

- **Skill**: Multi-step workflow with bundled assets (templates, scripts, docs)
- Skills are for complex development tasks that benefit from reusable templates and scripts

## Creating a New Skill

### Step 1: Choose the Domain

Skills are organized by domain:

- `frontend`: React, Vue, Angular, UI components, styling
- `backend`: APIs, databases, server-side logic, microservices
- `devops`: CI/CD, infrastructure, deployment, monitoring
- `data`: Data processing, analytics, ML pipelines
- `platform`: Core platform services, authentication, messaging
- `security`: Security scanning, compliance, vulnerability management
- `ai`: AI/ML model development, training pipelines

### Step 2: Create the Skill Structure

Create a folder structure like this:

```
.github/skills/<domain>/<skill-name>/
├── SKILL.md          # Main skill definition
├── templates/        # Code/config templates
│   ├── example.ts
│   └── config.yml
├── scripts/          # Helper scripts
│   └── validate.sh
└── docs/             # Supporting docs
    └── README.md
```

### Step 3: Write the SKILL.md File

Use this frontmatter structure:

```markdown
---
name: Short name
description: "Use when: <trigger phrases>. This skill helps teams <value>."
---

# Skill Name

**Domain**: [domain]
**Tool Compatibility**: VS Code, IDEA, Claude Code (list all that work)
**Status**: Draft | Beta | Stable
**Last Updated**: April 2, 2026

## What It Does

One-paragraph description of the skill's purpose and primary use case.

### Use Cases

- When you need to [specific task]
- When building [specific type of component/system]
- When you want to [specific outcome]

## Input Parameters

List parameters that Copilot should ask for:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `projectType` | string | Yes | Type of project (e.g., react, nextjs, ....) |
| `includeTests` | boolean | No | Whether to generate test files (default: true) |

## What You'll Get

Description of outputs: files generated, templates applied, or recommendations provided.

## Example

```
Input: projectType=React, includeTests=true
Output: Generated component with PropTypes, unit tests, and Storybook story
```

## How It Works

Brief explanation of the workflow steps. Example:

1. Analyzes your `package.json` or codebase structure
2. Validates project type and dependencies
3. Generates component template from templates/ folder
4. Applies formatting with prettier
5. Outputs ready-to-use files

## Prerequisites

- Node.js 16+
- [Optional dependency]

## Templates

Files in the `templates/` folder are:

- `component.tsx`: Basic functional component structure
- `component.test.tsx`: Jest test template
- `component.stories.tsx`: Storybook story template

## Troubleshooting

**Issue**: Template doesn't match my project structure  
**Solution**: [explanation]

**Issue**: [Another common issue]  
**Solution**: [explanation]

## Contributing

Found a bug or want to improve this skill? See [CONTRIBUTING.md](../../CONTRIBUTING.md).
```

### Step 4: Add Templates and Scripts

- **templates/**: Reusable code/config templates that the skill uses
- **scripts/**: Helper scripts for validation, setup, or post-processing
- **docs/**: Additional documentation beyond the SKILL.md

### Step 5: Test Locally

1. **For user-level testing**: Copy your skill to `~/Library/Application\ Support/Code/User/prompts/<domain>/<skill-name>/`
2. **For workspace testing**: Copy to `.github/skills/<domain>/<skill-name>/` and reload VS Code
3. Run through the workflow and verify outputs

**Checklist:**
- [ ] Frontmatter is valid YAML (no unescaped colons, proper spacing)
- [ ] `description` contains discovery keywords starting with "Use when:"
- [ ] All file paths and links are relative and correct
- [ ] Templates render correctly
- [ ] Instructions are clear for non-expert users

### Security Checklist

Every skill must pass this review before merging:

- [ ] No external network calls, API calls, or internet requests in scripts or templates
- [ ] No hardcoded or default credentials, tokens, API keys, or certificates
- [ ] No references to external LLMs or AI APIs (skills don't call other models)
- [ ] No data exfiltration — scripts don't upload or send code contents to external endpoints
- [ ] All scripts use only standard, approved dependencies (no `curl -s | bash` patterns)
- [ ] No OS commands that could be destructive or unexpected (`rm -rf`, `dd`, `curl | sh`, etc.)
- [ ] Templates document what data they read and what they write
- [ ] Works in restricted / intranet environments without external package downloads at runtime

## Submission Process

1. **Create a branch**: `git checkout -b skills/<domain>/<name>`
2. **Commit Changes**: `git commit -m "Add skill: <domain>/<name>"`
3. **Push & Open PR**: Include:
   - Title: `Add skill: <domain>/<name>`
   - Description: What it does, use cases, testing notes
4. **Address Feedback**: Maintainers will review for:
   - Correctness and usefulness
   - Alignment with Fei practices
   - Quality of documentation
   - YAML/Markdown syntax

## Naming Conventions

- **Domains**: `frontend`, `backend`, `devops`, `data`, `platform`, `security`, `ai` (lowercase, no underscores)
- **Skill names**: `kebab-case` (e.g., `react-component-gen`, `api-contract-testing`)
- **File names**: Match domain/skill name structure exactly
- **Descriptions**: Start with "Use when: " to aid discovery

## Examples

### Example: React Component Generator

**Location**: `.github/skills/frontend/react-component-gen/SKILL.md`

```markdown
---
name: React Component Generator
description: "Use when: creating new React components, scaffolding UI elements, or generating component boilerplate. Use this skill to generate complete React components with TypeScript, tests, and documentation."
---

# React Component Generator

**Domain**: frontend  
**Status**: Stable  
**Last Updated**: April 2, 2026

## What It Does

Generates complete React components with TypeScript, unit tests, and Storybook stories based on your specifications.

### Use Cases

- When creating new UI components for a React application
- When you need consistent component structure across your team
- When scaffolding components with tests and documentation

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `componentName` | string | Yes | Name of the component (PascalCase) |
| `componentType` | string | No | Type: functional, class, hook (default: functional) |
| `includeTests` | boolean | No | Generate Jest tests (default: true) |
| `includeStories` | boolean | No | Generate Storybook stories (default: true) |

## What You'll Get

- Component file with TypeScript interfaces
- Unit tests with Jest and React Testing Library
- Storybook stories for component documentation
- Proper file structure and naming conventions

## How It Works

1. Validates component name and project structure
2. Generates component template from templates/ folder
3. Creates test file with common test patterns
4. Generates Storybook story for documentation
5. Applies project-specific formatting

## Prerequisites

- React 16.8+
- TypeScript configured
- Jest and React Testing Library (optional for tests)
- Storybook (optional for stories)
```

## Updating Existing Skills

When updating a skill, increment the version in frontmatter (if included), update the last-modified date, and document changes in a CHANGELOG section.

## Questions?

- Check [.github/copilot-instructions.md](./.github/copilot-instructions.md) for overview
- See [SKILLS.md](./SKILLS.md) for indexed examples
- Open a Discussion for guidance before creating

---

**Thank you for helping make Fei Copilot skills more valuable!**