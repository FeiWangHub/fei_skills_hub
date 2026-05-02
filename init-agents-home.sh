#!/usr/bin/env bash
# Fei Skills Hub — Initialize ~/.agents directory structure
#
# This script creates the directory structure for ~/.agents,
# which is used as a local hub for agent skills and configurations.
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
CONFIG_DIR="${AGENTS_HOME}/config"
CACHE_DIR="${AGENTS_HOME}/cache"
DATA_DIR="${AGENTS_HOME}/data"

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
    echo "Creating ~/.agents directory structure..."
    echo ""

    # Main directories
    create_dir "$AGENTS_HOME" "Agents home directory"
    create_dir "$SKILLS_DIR" "Skills directory"
    create_dir "$CONFIG_DIR" "Configuration directory"
    create_dir "$CACHE_DIR" "Cache directory"
    create_dir "$DATA_DIR" "Data directory"

    # Skills subdirectories (organized by domain)
    create_dir "$SKILLS_DIR/frontend" "Frontend skills"
    create_dir "$SKILLS_DIR/backend" "Backend skills"
    create_dir "$SKILLS_DIR/devops" "DevOps skills"
    create_dir "$SKILLS_DIR/data" "Data skills"
    create_dir "$SKILLS_DIR/platform" "Platform skills"
    create_dir "$SKILLS_DIR/security" "Security skills"
    create_dir "$SKILLS_DIR/ai" "AI skills"
    create_dir "$SKILLS_DIR/mobile" "Mobile skills"
    create_dir "$SKILLS_DIR/infrastructure" "Infrastructure skills"

    # Config subdirectories
    create_dir "$CONFIG_DIR/agents" "Agent configurations"
    create_dir "$CONFIG_DIR/tools" "Tool configurations"

    # Cache subdirectories
    create_dir "$CACHE_DIR/search" "Search cache"
    create_dir "$CACHE_DIR/analysis" "Analysis cache"

    # Data subdirectories
    create_dir "$DATA_DIR/logs" "Log files"
    create_dir "$DATA_DIR/projects" "Project metadata"
}

# ── README Files ────────────────────────────────────────────────────
create_readme_files() {
    echo ""
    echo "Creating README files..."
    echo ""

    # Root README
    create_file "$AGENTS_HOME/README.md" \
'# ~/.agents Directory

This directory serves as your local hub for AI agent skills, configurations, and data.

## Structure

- **skills/** - Agent skills organized by domain
  - frontend/ - Frontend development skills
  - backend/ - Backend development skills
  - devops/ - DevOps and infrastructure skills
  - data/ - Data science and analytics skills
  - platform/ - Platform and architecture skills
  - security/ - Security and compliance skills
  - ai/ - AI/ML specific skills
  - mobile/ - Mobile development skills
  - infrastructure/ - Infrastructure skills

- **config/** - Configuration files for agents and tools
  - agents/ - Agent-specific configurations
  - tools/ - Tool-specific configurations

- **cache/** - Temporary cache data (can be safely deleted)
  - search/ - Search operation cache
  - analysis/ - Analysis operation cache

- **data/** - Persistent data and metadata
  - logs/ - Operation logs
  - projects/ - Project-specific metadata

## Usage

1. Link skills from Fei Skills Hub:
   ```bash
   bash setup-for-agents.sh --agents-home
   ```

2. Install skills into specific domains:
   ```bash
   # Frontend skills will appear in ./skills/frontend/
   # Backend skills will appear in ./skills/backend/
   # etc.
   ```

3. Configure tools to use ~/.agents as their skill root

## Tips

- Keep config files as YAML or JSON for easy parsing
- Log important operations in data/logs/
- Clear cache/ periodically to save disk space
- Version control: Consider committing config/ but not cache/

---

Created by: Fei Skills Hub Initializer
' "Main README"

    # Skills README
    create_file "$SKILLS_DIR/README.md" \
'# Skills Directory

This directory contains agent skills organized by domain.

## Domains

- **frontend/** - React, Vue, Svelte, UI/UX design patterns
- **backend/** - Java, Python, Node.js, architecture patterns
- **devops/** - Docker, Kubernetes, CI/CD, IaC
- **data/** - Data processing, analytics, ML models
- **platform/** - System design, scalability, performance
- **security/** - Security best practices, compliance
- **ai/** - LLM patterns, prompt engineering, agents
- **mobile/** - iOS, Android, React Native, Flutter
- **infrastructure/** - Cloud platforms, networking

## Adding Skills

1. Create a subdirectory for your skill: `mkdir -p frontend/my-skill`
2. Add a SKILL.md or README.md with documentation
3. Include templates and scripts as needed

---

Skills are typically symlinked or copied from Fei Skills Hub.
' "Skills README"

    # Config README
    create_file "$CONFIG_DIR/README.md" \
'# Configuration Directory

Store agent and tool configurations here.

## agents/

Tool-specific agent configurations:
- copilot.yaml - GitHub Copilot settings
- claude.yaml - Claude configuration
- cursor.yaml - Cursor AI settings

## tools/

Configurations for various tools:
- vs-code.json - VS Code preferences
- extensions.json - VS Code extensions list

---

Configuration files are typically in YAML or JSON format.
' "Config README"
}

# ── .gitignore ─────────────────────────────────────────────────────
create_gitignore() {
    echo ""
    echo "Creating .gitignore..."
    echo ""

    create_file "$AGENTS_HOME/.gitignore" \
'# Cache (regenerated)
cache/
*.cache

# Logs (sensitive information)
data/logs/

# IDE-specific
.DS_Store
.vscode/
.idea/

# Temporary files
*.tmp
*.swp
*.swo
*~

# OS-specific
Thumbs.db
' "Gitignore file"
}

# ── Environment Config ──────────────────────────────────────────────
create_env_config() {
    echo ""
    echo "Creating environment configuration..."
    echo ""

    create_file "$CONFIG_DIR/.env.example" \
'# Fei Skills Hub — Local Agent Configuration

# Set to true to enable debug logging
DEBUG=false

# Skills root directory
SKILLS_ROOT=${HOME}/.agents/skills

# Log level (debug, info, warn, error)
LOG_LEVEL=info

# Cache settings
CACHE_ENABLED=true
CACHE_TTL=3600

# Add custom paths as needed
CUSTOM_SKILLS_PATH=

' "Environment example"
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
    echo "Next steps:"
    echo "  1. Link skills: bash setup-for-agents.sh --agents-home"
    echo "  2. Configure tools to use: ${AGENTS_HOME}/skills"
    echo "  3. Add custom configurations in: ${CONFIG_DIR}/"
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
    create_readme_files
    create_gitignore
    create_env_config

    if $DRY_RUN; then
        info "Dry run complete. Run without --dry-run to actually initialize."
    else
        show_summary
    fi
}

main
