#!/usr/bin/env bash
# Fei Skills Hub — Initialize ~/.agents directory structure
#
# This script creates the directory structure for ~/.agents,
# following the .agents Protocol (https://dotagentsprotocol.com/).
#
# Usage:  bash init-agents-home.sh                  # interactive mode
#         bash init-agents-home.sh --auto           # auto-create all
#         bash init-agents-home.sh --dry-run        # preview only

set -euo pipefail

# ── Colors ──────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}[info]${NC} $*"; }
ok()    { echo -e "${GREEN}[ok]${NC}   $*"; }
warn()  { echo -e "${YELLOW}[warn]${NC}  $*"; }
fail()  { echo -e "${RED}[fail]${NC}  $*"; }

# ── Paths ───────────────────────────────────────────────────────────
AGENTS_HOME="${HOME}/.agents"
SKILLS_DIR="${AGENTS_HOME}/skills"
AGENTS_DIR="${AGENTS_HOME}/agents"
TASKS_DIR="${AGENTS_HOME}/tasks"
MEMORIES_DIR="${AGENTS_HOME}/memories"

# ── Options ─────────────────────────────────────────────────────────
DRY_RUN=false
AUTO_CREATE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)  DRY_RUN=true; shift ;;
        --auto)     AUTO_CREATE=true; shift ;;
        *)          shift ;;
    esac
done

# ── Utility Functions ───────────────────────────────────────────────
create_dir() {
    local dir="$1" desc="$2"
    
    if $DRY_RUN; then
        info "[DRY RUN] mkdir: $dir"
        return
    fi

    if [ -d "$dir" ]; then
        warn "Directory already exists: $dir"
        return
    fi

    mkdir -p "$dir"
    ok "Created: $dir ($desc)"
}

create_file() {
    local file="$1" content="$2" desc="$3"
    
    if $DRY_RUN; then
        info "[DRY RUN] create: $file"
        return
    fi

    if [ -f "$file" ]; then
        warn "File already exists: $file"
        return
    fi

    mkdir -p "$(dirname "$file")"
    echo "$content" > "$file"
    ok "Created: $file ($desc)"
}

# ── Directory Structure ─────────────────────────────────────────────
create_structure() {
    echo ""
    echo "Creating ~/.agents directory structure (.agents Protocol)..."
    echo ""

    # Main directories
    create_dir "$AGENTS_HOME" "Agents home directory"
    create_dir "$SKILLS_DIR" "Skills directory"
    create_dir "$AGENTS_DIR" "Sub-agents directory"
    create_dir "$TASKS_DIR" "Tasks directory"
    create_dir "$MEMORIES_DIR" "Memories directory"

    # Skills subdirectories (organized by domain - optional but useful)
    create_dir "$SKILLS_DIR/frontend" "Frontend skills"
    create_dir "$SKILLS_DIR/backend" "Backend skills"
    create_dir "$SKILLS_DIR/devops" "DevOps skills"
    create_dir "$SKILLS_DIR/data" "Data skills"
    create_dir "$SKILLS_DIR/platform" "Platform skills"
    create_dir "$SKILLS_DIR/security" "Security skills"
    create_dir "$SKILLS_DIR/ai" "AI skills"
    create_dir "$SKILLS_DIR/mobile" "Mobile skills"
    create_dir "$SKILLS_DIR/infrastructure" "Infrastructure skills"
}

# ── Protocol Files ──────────────────────────────────────────────────
create_protocol_files() {
    echo ""
    echo "Creating .agents Protocol files..."
    echo ""

    # agents.md
    create_file "$AGENTS_HOME/agents.md" \
'# Agent Instructions

This file contains global instructions and conventions for your AI agents.
It is compatible with the AGENTS.md standard.

## Conventions
- Write clean, self-documenting code.
- Think step-by-step before making changes.
' "agents.md"

    # system-prompt.md
    create_file "$AGENTS_HOME/system-prompt.md" \
'You are an expert AI assistant.
Follow the instructions in agents.md and utilize available tools in mcp.json.
Use the skills provided in the skills/ directory to accomplish tasks efficiently.
' "system-prompt.md"

    # mcp.json
    create_file "$AGENTS_HOME/mcp.json" \
'{
  "mcpServers": {}
}' "mcp.json"

    # models.json
    create_file "$AGENTS_HOME/models.json" \
'{
  "models": []
}' "models.json"

    # Root README
    create_file "$AGENTS_HOME/README.md" \
'# ~/.agents Directory

This directory serves as your local hub for AI agent configuration, following the [.agents Protocol](https://dotagentsprotocol.com/).

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

1. Link skills from Fei Skills Hub:
   ```bash
   bash setup-for-agents.sh --agents-home
   ```

2. Configure your AI tools (Claude Code, Cursor, Windsurf, etc.) to use these skills and settings.
' "Main README"
}

# ── .gitignore ─────────────────────────────────────────────────────
create_gitignore() {
    echo ""
    echo "Creating .gitignore..."
    echo ""

    create_file "$AGENTS_HOME/.gitignore" \
'# OS-specific
.DS_Store
Thumbs.db

# IDE-specific
.vscode/
.idea/

# Temporary files
*.tmp
*.swp
*~
' "Gitignore file"
}

# ── Summary ─────────────────────────────────────────────────────────
show_summary() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║         ~/.agents Directory Initialized                 ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    echo "Location: ${AGENTS_HOME}"
    echo ""
    echo "Created following the .agents Protocol standards:"
    echo "  - mcp.json & models.json"
    echo "  - agents.md & system-prompt.md"
    echo "  - skills/, agents/, tasks/, memories/ directories"
    echo ""
    echo "Next steps:"
    echo "  1. Link skills: bash setup-for-agents.sh --agents-home"
    echo "  2. Update your MCP servers in ${AGENTS_HOME}/mcp.json"
    echo "  3. Add persistent context in ${AGENTS_HOME}/memories/"
    echo ""
    echo "Documentation: ${AGENTS_HOME}/README.md"
    echo ""
}

# ── Main ────────────────────────────────────────────────────────────
main() {
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║    Fei Skills Hub — Initialize ~/.agents                ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""

    if $DRY_RUN; then
        echo "*** DRY RUN MODE — no changes will be made ***"
        echo ""
    fi

    # Confirm before proceeding (unless --auto)
    if [ ! "$AUTO_CREATE" = true ] && [ ! "$DRY_RUN" = true ]; then
        echo "This will create the directory structure at: $AGENTS_HOME"
        echo ""
        read -p "Continue? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            info "Cancelled."
            exit 0
        fi
    fi

    # Create everything
    create_structure
    create_protocol_files
    create_gitignore

    if $DRY_RUN; then
        info "Dry run complete. Run without --dry-run to actually initialize."
    else
        show_summary
    fi
}

main
