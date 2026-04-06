#!/usr/bin/env bash
# Fei Skills Hub — Cross-tool installer
#
# This script symlinks or copies skills directories to the prompt locations
# of all supported tools on the current machine. It is safe to re-run (idempotent).
#
# Usage:  bash setup-for-agents.sh                    # auto-detect tools
#         bash setup-for-agents.sh --vscode --claude  # only these targets
#         bash setup-for-agents.sh --dry-run          # show what would happen

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
SKILLS_SOURCE="${SCRIPT_DIR}/.github/skills"
PROMPTS_TARGET="${SKILLS_SOURCE}"  # for Copilot slash-command tools

if [ ! -d "$SKILLS_SOURCE" ]; then
    fail "Skills source directory not found: ${SKILLS_SOURCE}"
    exit 1
fi

# ── Options ─────────────────────────────────────────────────────────
DRY_RUN=false
FORCE=false
TOOL_TARGETS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)  DRY_RUN=true; shift ;;
        --force)    FORCE=true; shift ;;
        *)          TOOL_TARGETS+=("$1"); shift ;;
    esac
done

HAS_FLAG() {
    local flag="$1"
    if [ ${#TOOL_TARGETS[@]} -eq 0 ]; then return 0; fi
    for t in "${TOOL_TARGETS[@]}"; do [[ "$t" == "$flag" ]] && return 0; done
    return 1
}

# ── Platform detection ──────────────────────────────────────────────
case "$(uname -s)" in
    Darwin*)  PLATFORM="mac" ;;
    Linux*)   PLATFORM="linux" ;;
    MINGW*|MSYS*|CYGWIN*)  PLATFORM="windows" ;;
    *)        PLATFORM="other" ;;
esac

# ── Windows path helpers ────────────────────────────────────────────
if [ "$PLATFORM" = "windows" ]; then
    # Convert Windows env vars (C:\Users\...) to Git Bash paths (/c/Users/...)
    to_unix_path() {
        local p="$1"
        if [[ "$p" == *:*\\* ]] || [[ "$p" == *:*/* ]]; then
            cygpath -u "$p" 2>/dev/null || echo "$p"
        else
            echo "$p"
        fi
    }
else
    to_unix_path() { echo "$1"; }
fi

# ── Copy / Link strategy ───────────────────────────────────────────
# We use hard links on same volume, fall back to symlinks, fall back to rsync copy.
# Hard links and symlinks mean a single `git pull` in the repo updates all tools.
link_or_copy() {
    local src="$1" dst="$2" tool="$3"

    if $DRY_RUN; then
        info "[DRY RUN] ${tool}: link ${src} → ${dst}"
        return
    fi

    # Already exists?
    if [ -e "$dst" ] || [ -L "$dst" ]; then
        if $FORCE; then
            rm -rf "$dst"
        else
            warn "${tool}: ${dst} already exists (use --force to overwrite, --dry-run to preview)"
            return
        fi
    fi

    mkdir -p "$(dirname "$dst")"

    # On Windows, prefer directory junctions (no Admin required) via mklink /J
    if [ "$PLATFORM" = "windows" ]; then
        cmd.exe //C mklink //J "$(cygpath -w "$dst" 2>/dev/null || echo "$dst")" "$(cygpath -w "$src" 2>/dev/null || echo "$src")" 2>/dev/null && {
            ok "${tool}: junction → ${dst}"
            return
        }
    fi

    # Try symlink first (keeps single source of truth)
    if ln -s "$src" "$dst" 2>/dev/null; then
        ok "${tool}: symlinked → ${dst}"
        return
    fi

    # Fallback: hard link if on same filesystem
    if cp -al "$src" "$dst" 2>/dev/null; then
        ok "${tool}: hard-linked → ${dst}"
        return
    fi

    # Final fallback: regular recursive copy (not self-updating)
    cp -R "$src" "$dst"
    warn "${tool}: copied (not symlinked, changes won't auto-sync) → ${dst}"
}

# ── Targets ─────────────────────────────────────────────────────────
configure_tool() {
    local tool="$1" target="$2"
    link_or_copy "$PROMPTS_TARGET" "$target" "$tool"
}

setup_vscode() {
    echo ""
    echo "── VS Code + GitHub Copilot ──"

    local paths=()
    if [ "$PLATFORM" = "mac" ]; then
        paths+=("$HOME/Library/Application Support/Code/User/globalStorage/github.copilot-chat/fei-skills")
        paths+=("$HOME/Library/Application Support/Code/User/prompts/fei-skills")
    elif [ "$PLATFORM" = "linux" ]; then
        paths+=("$HOME/.config/Code/User/globalStorage/github.copilot-chat/fei-skills")
        paths+=("$HOME/.config/Code/User/prompts/fei-skills")
    elif [ "$PLATFORM" = "windows" ]; then
        local appdata
        appdata=$(to_unix_path "${APPDATA:-}")
        if [ -n "$appdata" ] && [ -d "$appdata" ]; then
            paths+=("$appdata/Code/User/globalStorage/github.copilot-chat/fei-skills")
            paths+=("$appdata/Code/User/prompts/fei-skills")
        else
            warn "VS Code: \$APPDATA not found or empty. Make sure you are running in Git Bash."
        fi
    fi

    for p in "${paths[@]}"; do
        if [ -d "$(dirname "$p")" ]; then
            configure_tool "VS Code" "$p"
        fi
    done
}

setup_claude_code() {
    echo ""
    echo "── Claude Code ──"
    local target="$HOME/.claude/SKILLS/fei-skills"
    if [ -d "$HOME/.claude" ] || $DRY_RUN; then
        configure_tool "Claude Code" "$target"
    else
        warn "Claude Code: ~/.claude/ not found, skipping"
    fi
}

setup_cursor() {
    echo ""
    echo "── Cursor / Codeium ──"
    local target="$HOME/.cursor/rules/fei-skills"
    configure_tool "Cursor" "$target"
}

setup_windsurf() {
    echo ""
    echo "── Windsurf ──"
    local target="$HOME/.codeium/windsurf/prompts/fei-skills"
    configure_tool "Windsurf" "$target"
}

setup_intellij() {
    echo ""
    echo "── IntelliJ IDEA + Copilot ──"

    local paths=()
    if [ "$PLATFORM" = "mac" ]; then
        paths+=("$HOME/Library/Application Support/JetBrains/copilot-chat/fei-skills")
        paths+=("$HOME/Library/Application Support/JetBrains/IntelliJIdea*/prompts/fei-skills")
        paths+=("$HOME/Library/Application Support/CopilotChat/prompts/fei-skills")
    elif [ "$PLATFORM" = "linux" ]; then
        paths+=("$HOME/.local/share/JetBrains/copilot-chat/fei-skills")
        paths+=("$HOME/.local/share/CopilotChat/prompts/fei-skills")
    elif [ "$PLATFORM" = "windows" ]; then
        local appdata
        appdata=$(to_unix_path "${APPDATA:-}")
        if [ -n "$appdata" ] && [ -d "$appdata" ]; then
            paths+=("$appdata/JetBrains/copilot-chat/fei-skills")
        else
            warn "IntelliJ IDEA: \$APPDATA not found or empty."
        fi
    fi

    for p in "${paths[@]}"; do
        # Skip glob patterns if parent dir doesn't exist
        if [[ "$p" == *'*'* ]]; then
            if compgen -G "$p" &>/dev/null 2>&1; then
                for expanded in $p; do
                    configure_tool "IntelliJ IDEA" "$expanded"
                done
            fi
            continue
        fi
        # Try creating parent
        if mkdir -p "$(dirname "$p")" 2>/dev/null; then
            configure_tool "IntelliJ IDEA" "$p"
        fi
    done
}

setup_gemini() {
    echo ""
    echo "── Gemini CLI ──"
    local target="$HOME/.gemini-cli/prompts/fei-skills"
    configure_tool "Gemini CLI" "$target"
}

setup_opencode() {
    echo ""
    echo "── OpenCode ──"
    local target="$HOME/.opencode/prompts/fei-skills"
    configure_tool "OpenCode" "$target"
}

# ── Main ────────────────────────────────────────────────────────────
echo "╔══════════════════════════════════════════════════════════╗"
echo "║          Fei Skills Hub — Cross-Tool Installer          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Source: ${SKILLS_SOURCE}"
$DRY_RUN && echo "*** DRY RUN — no changes will be made ***"
echo ""

HAS_FLAG "--vscode"      && setup_vscode
HAS_FLAG "--claude"      && setup_claude_code
HAS_FLAG "--cursor"      && setup_cursor
HAS_FLAG "--windsurf"    && setup_windsurf
HAS_FLAG "--intellij"    && setup_intellij
HAS_FLAG "--gemini"      && setup_gemini
HAS_FLAG "--opencode"    && setup_opencode

echo ""
# Portable: avoid realpath which isn't available on Windows Git Bash
REPO_DISPLAY="$(cd "$SCRIPT_DIR" && pwd)"
if $DRY_RUN; then
    info "Dry run complete. Run without --dry-run to actually install."
else
    info "Done! Restart your tools to see the skills."
    info "To update skills later: cd ${REPO_DISPLAY} && git pull"
fi
