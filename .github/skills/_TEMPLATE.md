---
name: Example Skill Template
description: "Use when: you want to understand the structure of a skill. This is a template showing required and optional sections."
---

# Example Skill: [Your Skill Name]

**Domain**: [backend/frontend/devops/data/platform/security/ai]  
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

Found a bug or want to improve this skill? See [../CONTRIBUTING.md](../../CONTRIBUTING.md).

---

**Tip**: This is a template. Replace all bracketed sections with your actual content.
