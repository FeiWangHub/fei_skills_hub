#!/usr/bin/env bash
# Fei Skills Hub — Initialize the .agents Protocol
#
# This script links this repository's .agents directory to ~/.agents,
# following the .agents Protocol (https://dotagentsprotocol.com/).
#
# Usage:  bash init-dot-agents.sh                  # interactive mode
#         bash init-dot-agents.sh --auto           # auto-confirm all prompts
#         bash init-dot-agents.sh --dry-run        # preview only

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
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENTS_HOME="${SCRIPT_DIR}/.agents"

# ── Options ─────────────────────────────────────────────────────────
DRY_RUN=false
AUTO_YES=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)  DRY_RUN=true; shift ;;
        --auto)     AUTO_YES=true; shift ;;
        *)          shift ;;
    esac
done

# ── Validate repo .agents directory ─────────────────────────────────
validate_agents() {
    if [ ! -d "$AGENTS_HOME" ]; then
        fail "Cannot find .agents directory at: ${AGENTS_HOME}"
        fail "Make sure you are running this script from the repository root."
        exit 1
    fi

    local missing=()
    for item in skills agents.md system-prompt.md mcp.json models.json; do
        if [ ! -e "$AGENTS_HOME/$item" ]; then
            missing+=("$item")
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        fail "The .agents directory is missing required items:"
        for m in "${missing[@]}"; do
            fail "  - $m"
        done
        fail "Please update your repository and try again."
        exit 1
    fi
}

# ── Handle existing ~/.agents ───────────────────────────────────────
handle_existing() {
    # Check if it's already a symlink pointing to our repo (idempotent)
    if [ -L "$HOME/.agents" ]; then
        local current_target
        current_target=$(readlink "$HOME/.agents")
        if [ "$current_target" = "$AGENTS_HOME" ]; then
            ok "~/.agents is already linked to this repository."
            return 1  # signal: already linked, nothing to do
        fi
    fi

    warn "~/.agents already exists."
    echo ""
    echo "  (b) Back up the existing directory (rename with timestamp)"
    echo "  (q) Quit — do nothing"
    echo ""

    if $AUTO_YES; then
        REPLY="b"
    else
        read -p "Choose an option (b/q) " -n 1 -r
        echo
    fi

    case "$REPLY" in
        [Bb])
            local bkp="$HOME/.agents.bak.$(date '+%Y%m%d-%H%M%S')"
            if $DRY_RUN; then
                info "[DRY RUN] mv ~/.agents ${bkp}"
            else
                mv "$HOME/.agents" "$bkp"
                ok "Backed up existing ~/.agents to ${bkp}"
            fi
            ;;
        [Qq])
            info "Cancelled. No changes made."
            exit 0
            ;;
        *)
            fail "Invalid option. Exiting."
            exit 1
            ;;
    esac
    return 0
}

# ── Create symlink ──────────────────────────────────────────────────
create_symlink() {
    if $DRY_RUN; then
        info "[DRY RUN] ln -s ${AGENTS_HOME} ${HOME}/.agents"
        return
    fi

    ln -s "$AGENTS_HOME" "$HOME/.agents"
    ok "Symlinked: ~/.agents -> ${AGENTS_HOME}"

    echo ""
    echo "Available skills:"
    ls -1 "$HOME/.agents/skills"
}

# ── Summary ─────────────────────────────────────────────────────────
show_summary() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║       .agents Protocol Initialized                      ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    echo "  Source:  ${AGENTS_HOME}"
    echo "  Target:  ${HOME}/.agents"
    echo ""
    echo "Your AI tools (Claude Code, Cursor, Copilot, etc.) can"
    echo "now use the skills, prompts, and agent configs from this hub."
    echo ""
}

# ── Main ────────────────────────────────────────────────────────────
main() {
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║     Fei Skills Hub — Initialize .agents                 ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""

    if $DRY_RUN; then
        echo "*** DRY RUN MODE — no changes will be made ***"
        echo ""
    fi

    # Step 1: Validate repo structure
    validate_agents

    # Step 2: Confirm (unless --auto)
    if ! $AUTO_YES && ! $DRY_RUN; then
        echo "This will link ~/.agents -> ${AGENTS_HOME}"
        echo ""
        read -p "Continue? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            info "Cancelled."
            exit 0
        fi
    fi

    # Step 3: Handle existing ~/.agents
    if [ -e "$HOME/.agents" ] || [ -L "$HOME/.agents" ]; then
        handle_existing
        if [ $? -eq 1 ]; then
            # Already linked to our repo
            show_summary
            return
        fi
    fi

    # Step 4: Create the symlink
    create_symlink

    if $DRY_RUN; then
        info "Dry run complete. Run without --dry-run to apply changes."
    else
        show_summary
    fi
}

main
