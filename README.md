# Fei Skills Hub

**A centralized, organized repository for AI agent skills designed for Fei engineers.**

---

## What is This?

This hub provides reusable, tested skills for AI coding assistants that enhance developer productivity across our teams. Instead of individuals creating their own workflows, we maintain a shared, curated collection that anyone can install and use.

### What Are Skills?

Skills are **multi-step workflows** with templates and helper scripts for complex development tasks (e.g., "Generate React components with tests", "Set up API contract testing", "Create deployment pipelines").

### Context

- **Internal use only**: This repository is for our engineers. All skills are designed with enterprise security and compliance requirements in mind, especially information security.
- **Intranet-friendly**: Skills do not depend on external services or require internet access beyond our internal network. They should work in restricted environments.
- **Tool-agnostic**: Skills are designed to work across multiple AI coding tools:
  - VS Code + GitHub Copilot Chat
  - IntelliJ IDEA + GitHub Copilot
  - Windsurf / Codeium / Cursor
  - Claude Code CLI
  - Gemini CLI
  - OpenCode
  - Any tool that supports `.prompt` or slash commands

### Supported Tools

| Tool | Prompt Location | Notes |
|------|----------------|-------|
| VS Code + Copilot | `prompts/` subdirectory of extensions directory | Works with `/` slash commands |
| IDEA + Copilot | Same as VS Code | JetBrains plugin respects workspace prompts |
| Claude Code | `~/.claude/` or workspace `.claude/` | Uses `.prompt` files |
| Gemini CLI | Workspace-local config | Similar slash command patterns |
| Windsurf / Cursor | IDE settings or workspace config | May require manual prompt import |

## Quick Start

### Installation

**Recommended: Clone + Run Install Script (One Command Per Platform)**

This handles all supported tools automatically via symlinks — no manual path guessing needed.

**macOS / Linux:**
```bash
git clone https://github.com/FeiWangHub/fei_skills_hub.git ~/fei-skills
cd ~/fei-skills
bash setup-for-agents.sh
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/FeiWangHub/fei_skills_hub.git $HOME\fei-skills
cd $HOME\fei-skills
.\setup-for-agents.ps1
```

The install script automatically creates symlinks to all detected AI coding tools on your machine. Restart your tool to see the skills.

#### Install Script Options

Both scripts support these flags:

| Flag | Description |
|------|-------------|
| `--dry-run` | Preview what would be created without making changes |
| `--force` | Overwrite existing symlinks/junctions |
| `--vscode` | Install only for VS Code + Copilot |
| `--claude` | Install only for Claude Code |
| `--cursor` | Install only for Cursor |
| `--windsurf` | Install only for Windsurf |
| `--intellij` | Install only for IntelliJ IDEA + Copilot |
| `--gemini` | Install only for Gemini CLI |
| `--opencode` | Install only for OpenCode |

**Examples:**
```bash
# Preview before installing
bash setup-for-agents.sh --dry-run

# Install only for Claude Code and VS Code
bash setup-for-agents.sh --claude --vscode

# Force reinstall (overwrite existing links)
bash setup-for-agents.sh --force

# Windows: Install only for IntelliJ
.\setup-for-agents.ps1 -IntelliJ
```

#### Alternative: Manual Clone to Specific Tool Paths

If you prefer manual installation, see [SETUP-GUIDE.md](./SETUP-GUIDE.md) for exact paths per tool.

#### Workspace-Level (Per Project)

Clone into your project's repo for project-specific skill usage:

```bash
cd your-project-repo/
git submodule add https://github.com/FeiWangHub/fei_skills_hub.git .github/skills/fei-skills
# OR without submodules:
git clone https://github.com/FeiWangHub/fei_skills_hub.git .github/skills/fei-skills
```

### Using a Skill

1. Open your AI coding assistant's chat
2. Type `/` to see available skills
3. Select a skill and follow the prompts

### Finding What You Need

- **Browse all skills**: See [SKILLS.md](./SKILLS.md) for a complete index
- **By domain**: Frontend, Backend, DevOps, Data, Platform, Security, AI/ML

## Repository Structure

```
fei-skills-repo/
├── .github/
│   └── skills/                 # Multi-step workflows
│       ├── frontend/
│       │   ├── react-component-gen/
│       │   │   ├── SKILL.md
│       │   │   ├── templates/
│       │   │   └── scripts/
│       │   └── ...
│       ├── backend/
│       ├── devops/
│       ├── data/
│       ├── platform/
│       ├── security/
│       └── ai/
├── .github/copilot-instructions.md   # Workspace configuration
├── SETUP-GUIDE.md              # Cross-tool installation guide
├── README.md                   # This file
├── CONTRIBUTING.md             # How to add new skills
├── SKILLS.md                   # Complete skills index
└── LICENSE
```

## Contributing

We welcome **new skills** from Fei engineers!

### Before You Create

Read [CONTRIBUTING.md](./CONTRIBUTING.md) to:
- Understand what makes a good skill
- Follow naming conventions and structure
- Write clear descriptions for discoverability
- Test locally before submitting
- Understand the review process

### Quick Example: Submitting a New Skill

1. Create folder: `.github/skills/backend/my-skill-name/`
2. Add `SKILL.md` with proper frontmatter
3. Add templates/ and scripts/ as needed
4. Test in VS Code
5. Open a PR with description

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed steps.

## FAQ

**Q: Which AI tool should I use?**  
A: We support them all. Pick the one you prefer — skills are designed to be tool-agnostic.

**Q: Can I use these outside of work?**  
A: These skills are designed for Fei work with enterprise security and compliance requirements. Personal use is fine if tools don't depend on internal systems or credentials.

**Q: Do skills work offline or on intranet?**  
A: Skills are designed to run in restricted environments. They don't call external URLs, download packages at runtime, or require internet access. Each skill documents its network requirements clearly.

**Q: How often are skills updated?**  
A: Skills are updated as needed. Check the repo for recent changes before using a skill in development. We recommend `git pull` periodically.

**Q: Can skills for different teams conflict?**  
A: Skills are organized by domain to avoid conflicts. If you find overlaps, open an Issue to discuss.

**Q: What if a skill stops working after a tool update?**  
A: Report the issue internally. Maintainers will investigate and patch as needed.

**Q: How do we handle security and compliance?**  
A: All skills pass through a security review before merging. Skills must not: send code or data to external endpoints, hardcode credentials, suggest insecure practices, or depend on unapproved external services.

## Security & Compliance

Skills targeting Fei environments must follow these rules:

1. **No external network calls**: Helper scripts should not curl/wget external APIs
2. **No credential storage**: Never include tokens, API keys, or certificates
3. **No external AI model calls**: Skills should not call other LLMs or AI APIs
4. **Composable and inspectable**: All templates and scripts must be human-readable
5. **Clear data boundaries**: Skills should document what data they read and write

## Support

- **Issues**: Report bugs, security concerns, or request new skills
- **Discussions**: Share feedback and ideas
- **Email**: [team contact, if applicable]

## Environment

- **IDEs**: VS Code, IntelliJ IDEA, Windsurf, Claude Code, Gemini CLI, OpenCode
- **AI Models**: Claude Haiku 4.5, Claude 3.5 Sonnet+, Gemini, and others (tested and supported)
- **Platforms**: macOS, Linux, Windows

## License

See the [MIT License](./LICENSE) file for details.

---

**Ready to use Copilot more effectively?** Head to [SKILLS.md](./SKILLS.md) to explore available skills, or [CONTRIBUTING.md](./CONTRIBUTING.md) to create your own!

**Last Updated**: April 2, 2026
**Maintained by**: Fei Engineering Team

---

## Appendix: Install Script Source Code

These scripts are included here for easy review and reference.

### setup-for-agents.sh (macOS / Linux / Git Bash on Windows)

```bash
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
```

### setup-for-agents.ps1 (Windows PowerShell)

```powershell
<#
.SYNOPSIS
    Fei Skills Hub — Windows installer (PowerShell)
.DESCRIPTION
    Installs Fei Skills Hub by creating directory junctions to the target
    prompt locations for all supported AI coding tools on Windows.
.PARAMETER DryRun
    Preview what would be created without making changes.
.PARAMETER Force
    Remove existing junctions/links before creating new ones.
.PARAMETER VsCode
    Install only for VS Code + GitHub Copilot.
.PARAMETER Claude
    Install only for Claude Code.
.PARAMETER Cursor
    Install only for Cursor.
.PARAMETER Windsurf
    Install only for Windsurf.
.PARAMETER IntelliJ
    Install only for IntelliJ IDEA + Copilot.
.PARAMETER Gemini
    Install only for Gemini CLI.
.PARAMETER OpenCode
    Install only for OpenCode.
.EXAMPLE
    .\setup-for-agents.ps1
    .\setup-for-agents.ps1 -VsCode -Claude
    .\setup-for-agents.ps1 -DryRun
    .\setup-for-agents.ps1 -Force
#>

[CmdletBinding()]
param(
    [switch] $DryRun,
    [switch] $Force,
    [switch] $VsCode,
    [switch] $Claude,
    [switch] $Cursor,
    [switch] $Windsurf,
    [switch] $IntelliJ,
    [switch] $Gemini,
    [switch] $OpenCode
)

$PSDefaultParameterValues['*:ErrorAction'] = 'Stop'

# ── Source ──────────────────────────────────────────────────────────
$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Definition
$SkillsSource = Join-Path $ScriptDir '.github' 'skills'

if (-not (Test-Path $SkillsSource -PathType Container)) {
    Write-Host "[fail] Skills source directory not found: $SkillsSource" -ForegroundColor Red
    exit 1
}

# ── Helper ──────────────────────────────────────────────────────────
$TargetsChosen = $false
if ($VsCode -or $Claude -or $Cursor -or $Windsurf -or $IntelliJ -or $Gemini -or $OpenCode) {
    $TargetsChosen = $true
}

function ShouldInstall { param([string] $Name)
    if (-not $TargetsChosen) { return $true }
    $flag = "--$($Name.ToLowerInvariant())"
    return switch ($Name.ToLowerInvariant()) {
        'vscode'   { $VsCode }
        'claude'   { $Claude }
        'cursor'   { $Cursor }
        'windsurf' { $Windsurf }
        'intellij' { $IntelliJ }
        'gemini'   { $Gemini }
        'opencode' { $OpenCode }
    }
}

function Link-OrCreate {
    param([string] $Tool, [string] $Target)

    if ($DryRun) {
        Write-Host "[info] [DRY RUN] $`: link -> $Target" -ForegroundColor Cyan
        return
    }

    $Parent = Split-Path $Target -Parent

    # Already exists?
    if (Test-Path $Target) {
        if ($Force) {
            # Safe removal: for junctions/symlinks, remove the link point only
            if ((Get-Item $Target).Attributes.ToString() -match 'ReparsePoint') {
                Remove-Item $Target -Force -ErrorAction Stop
            } else {
                Remove-Item $Target -Recurse -Force -ErrorAction Stop
            }
        } else {
            Write-Host "[warn] $`: $Target already exists (use -Force to overwrite)" -ForegroundColor Yellow
            return
        }
    }

    # Ensure parent directory exists
    if (-not (Test-Path $Parent)) {
        New-Item -ItemType Directory -Path $Parent -Force | Out-Null
    }

    # Create directory junction (no Admin required, unlike symlinks)
    try {
        # Using mklink /J via cmd works for directories without needing Administrator
        $cmdArgs = @('/C', 'mklink', '/J', "`"$Target`"", "`"$SkillsSource`"")
        $result = Start-Process 'cmd.exe' -ArgumentList $cmdArgs -NoNewWindow -Wait -PassThru
        if ($result.ExitCode -eq 0) {
            Write-Host "[ok]   $`: junction -> $Target" -ForegroundColor Green
            return
        }
    } catch {
        # Junction creation failed, fall through to copy
    }

    # Fallback: copy (not self-updating)
    Copy-Item -Path $SkillsSource -Destination $Target -Recurse -Force
    Write-Host "[warn] $`: copied (junction failed, changes won't auto-sync) -> $Target" -ForegroundColor Yellow
}

# ── Targets ─────────────────────────────────────────────────────────

function Install-VsCode {
    Write-Host ""
    Write-Host "-- VS Code + GitHub Copilot --"

    $appdata = [Environment]::GetFolderPath('ApplicationData')
    $paths = @(
        (Join-Path $appdata 'Code\User\globalStorage\github.copilot-chat\fei-skills'),
        (Join-Path $appdata 'Code\User\prompts\fei-skills')
    )

    foreach ($p in $paths) {
        $parent = Split-Path $p -Parent
        if (Test-Path $parent -PathType Container) {
            Link-OrCreate 'VS Code' $p
        }
    }
}

function Install-Claude {
    Write-Host ""
    Write-Host "-- Claude Code --"
    $homeDir = $env:USERPROFILE
    $target = Join-Path $homeDir '.claude\SKILLS\fei-skills'
    $claudeDir = Join-Path $homeDir '.claude'
    if ((Test-Path $claudeDir -PathType Container) -or $DryRun) {
        Link-OrCreate 'Claude Code' $target
    } else {
        Write-Host "[warn] Claude Code: $claudeDir not found, skipping" -ForegroundColor Yellow
    }
}

function Install-Cursor {
    Write-Host ""
    Write-Host "-- Cursor / Codeium --"
    $homeDir = $env:USERPROFILE
    $target = Join-Path $homeDir '.cursor\rules\fei-skills'
    Link-OrCreate 'Cursor' $target
}

function Install-Windsurf {
    Write-Host ""
    Write-Host "-- Windsurf --"
    $homeDir = $env:USERPROFILE
    $target = Join-Path $homeDir '.codeium\windsurf\prompts\fei-skills'
    Link-OrCreate 'Windsurf' $target
}

function Install-IntelliJ {
    Write-Host ""
    Write-Host "-- IntelliJ IDEA + Copilot --"
    $appdata = [Environment]::GetFolderPath('ApplicationData')
    $paths = @(
        (Join-Path $appdata 'JetBrains\copilot-chat\fei-skills')
    )

    foreach ($p in $paths) {
        $parent = Split-Path $p -Parent
        if (-not (Test-Path $parent)) {
            New-Item -ItemType Directory -Path $parent -Force | Out-Null
        }
        Link-OrCreate 'IntelliJ IDEA' $p
    }
}

function Install-Gemini {
    Write-Host ""
    Write-Host "-- Gemini CLI --"
    $homeDir = $env:USERPROFILE
    $target = Join-Path $homeDir '.gemini-cli\prompts\fei-skills'
    Link-OrCreate 'Gemini CLI' $target
}

function Install-OpenCode {
    Write-Host ""
    Write-Host "-- OpenCode --"
    $homeDir = $env:USERPROFILE
    $target = Join-Path $homeDir '.opencode\prompts\fei-skills'
    Link-OrCreate 'OpenCode' $target
}

# ── Main ────────────────────────────────────────────────────────────
Write-Host "========================================================"
Write-Host "       Fei Skills Hub -- Cross-Tool Installer"
Write-Host "========================================================"
Write-Host ""
Write-Host "Source: $SkillsSource"
if ($DryRun) { Write-Host "*** DRY RUN -- no changes will be made ***" }
Write-Host ""

if (ShouldInstall 'vscode')   { Install-VsCode }
if (ShouldInstall 'claude')   { Install-Claude }
if (ShouldInstall 'cursor')   { Install-Cursor }
if (ShouldInstall 'windsurf') { Install-Windsurf }
if (ShouldInstall 'intellij') { Install-IntelliJ }
if (ShouldInstall 'gemini')   { Install-Gemini }
if (ShouldInstall 'opencode') { Install-OpenCode }

Write-Host ""
if ($DryRun) {
    Write-Host "[info] Dry run complete. Run without -DryRun to actually install." -ForegroundColor Cyan
} else {
    $repoPath = (Resolve-Path $ScriptDir).Path
    Write-Host "[info] Done! Restart your tools to see the skills." -ForegroundColor Cyan
    Write-Host "[info] To update skills later: cd $repoPath && git pull" -ForegroundColor Cyan
}
```
