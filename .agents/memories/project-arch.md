---
id: project-arch
title: Project Architecture
content: High-level architecture notes for this repository
importance: medium
tags: architecture, repository, agents
---

## Purpose

This repository is a version-controlled personal `.agents` notebook. The `./.agents` directory is the source of truth for skills, sub-agents, tasks, and memories.

## Layout

- `./.agents/skills/` stores reusable skills.
- `./.agents/agents/` stores sub-agent profiles.
- `./.agents/tasks/` stores scheduled task definitions.
- `./.agents/memories/` stores persistent notes that should be reused across sessions.
