# .agents Directory

This directory follows the [.agents Protocol](https://dotagentsprotocol.com/) and is intended to be committed to this repository.

To use it as your global agents directory, link it to `~/.agents`:

```bash
ln -s "$PWD/.agents" "$HOME/.agents"
```

## Structure

- `agents.md`            # instructions (AGENTS.md compatible)
- `system-prompt.md`     # system prompt
- `mcp.json`             # MCP server configuration
- `models.json`          # model presets & provider keys
- `skills/`              # codified procedural knowledge
- `agents/`              # sub-agent profiles
- `tasks/`               # scheduled repeat tasks
- `memories/`            # persistent memory

## Usage

1. Add or edit content in this directory and commit to your repo.

2. Configure your AI tools to read from `~/.agents` (or link this directory to `~/.agents`).
