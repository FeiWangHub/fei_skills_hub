<#
.SYNOPSIS
    Fei Skills Hub — Initialize ~/.agents directory structure
.DESCRIPTION
    Creates the directory structure for ~/.agents, following the .agents 
    Protocol (https://dotagentsprotocol.com/).
.PARAMETER DryRun
    Preview what would be created without making changes.
.PARAMETER Auto
    Auto-create all directories without prompting.
.EXAMPLE
    .\init-agents-home.ps1
    .\init-agents-home.ps1 -Auto
    .\init-agents-home.ps1 -DryRun
#>

[CmdletBinding()]
param(
    [switch] $DryRun,
    [switch] $Auto
)

$PSDefaultParameterValues['*:ErrorAction'] = 'Stop'

# ── Paths ───────────────────────────────────────────────────────────
$AgentsHome = Join-Path $env:USERPROFILE '.agents'
$SkillsDir = Join-Path $AgentsHome 'skills'
$AgentsDir = Join-Path $AgentsHome 'agents'
$TasksDir = Join-Path $AgentsHome 'tasks'
$MemoriesDir = Join-Path $AgentsHome 'memories'

# ── Helper Functions ────────────────────────────────────────────────
function Create-DirectoryIfNotExists {
    param([string] $Path, [string] $Description)
    
    if ($DryRun) {
        Write-Host "[info] [DRY RUN] mkdir: $Path" -ForegroundColor Cyan
        return
    }

    if (Test-Path $Path -PathType Container) {
        Write-Host "[warn] Directory already exists: $Path" -ForegroundColor Yellow
        return
    }

    New-Item -ItemType Directory -Path $Path -Force | Out-Null
    Write-Host "[ok]   Created: $Path ($Description)" -ForegroundColor Green
}

function Create-FileIfNotExists {
    param([string] $Path, [string] $Content, [string] $Description)
    
    if ($DryRun) {
        Write-Host "[info] [DRY RUN] create: $Path" -ForegroundColor Cyan
        return
    }

    $ParentDir = Split-Path $Path -Parent
    if (-not (Test-Path $ParentDir)) {
        New-Item -ItemType Directory -Path $ParentDir -Force | Out-Null
    }

    if (Test-Path $Path) {
        Write-Host "[warn] File already exists: $Path" -ForegroundColor Yellow
        return
    }

    Set-Content -Path $Path -Value $Content -Encoding UTF8
    Write-Host "[ok]   Created: $Path ($Description)" -ForegroundColor Green
}

# ── Directory Structure ─────────────────────────────────────────────
function Create-Structure {
    Write-Host ""
    Write-Host "Creating ~/.agents directory structure (.agents Protocol)..."
    Write-Host ""

    # Main directories
    Create-DirectoryIfNotExists $AgentsHome "Agents home directory"
    Create-DirectoryIfNotExists $SkillsDir "Skills directory"
    Create-DirectoryIfNotExists $AgentsDir "Sub-agents directory"
    Create-DirectoryIfNotExists $TasksDir "Tasks directory"
    Create-DirectoryIfNotExists $MemoriesDir "Memories directory"

    # Skills subdirectories (organized by domain - optional but useful)
    Create-DirectoryIfNotExists (Join-Path $SkillsDir 'frontend') "Frontend skills"
    Create-DirectoryIfNotExists (Join-Path $SkillsDir 'backend') "Backend skills"
    Create-DirectoryIfNotExists (Join-Path $SkillsDir 'devops') "DevOps skills"
    Create-DirectoryIfNotExists (Join-Path $SkillsDir 'data') "Data skills"
    Create-DirectoryIfNotExists (Join-Path $SkillsDir 'platform') "Platform skills"
    Create-DirectoryIfNotExists (Join-Path $SkillsDir 'security') "Security skills"
    Create-DirectoryIfNotExists (Join-Path $SkillsDir 'ai') "AI skills"
    Create-DirectoryIfNotExists (Join-Path $SkillsDir 'mobile') "Mobile skills"
    Create-DirectoryIfNotExists (Join-Path $SkillsDir 'infrastructure') "Infrastructure skills"
}

# ── Protocol Files ──────────────────────────────────────────────────
function Create-ProtocolFiles {
    Write-Host ""
    Write-Host "Creating .agents Protocol files..."
    Write-Host ""

    $agentsMd = @'
# Agent Instructions

This file contains global instructions and conventions for your AI agents.
It is compatible with the AGENTS.md standard.

## Conventions
- Write clean, self-documenting code.
- Think step-by-step before making changes.
'@
    Create-FileIfNotExists (Join-Path $AgentsHome 'agents.md') $agentsMd "agents.md"

    $systemPromptMd = @'
You are an expert AI assistant.
Follow the instructions in agents.md and utilize available tools in mcp.json.
Use the skills provided in the skills/ directory to accomplish tasks efficiently.
'@
    Create-FileIfNotExists (Join-Path $AgentsHome 'system-prompt.md') $systemPromptMd "system-prompt.md"

    $mcpJson = @'
{
  "mcpServers": {}
}
'@
    Create-FileIfNotExists (Join-Path $AgentsHome 'mcp.json') $mcpJson "mcp.json"

    $modelsJson = @'
{
  "models": []
}
'@
    Create-FileIfNotExists (Join-Path $AgentsHome 'models.json') $modelsJson "models.json"

    $rootReadme = @'
# ~/.agents Directory

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
   ```powershell
   .\setup-for-agents.ps1 -AgentsHome
   ```

2. Configure your AI tools (Claude Code, Cursor, Windsurf, etc.) to use these skills and settings.
'@
    Create-FileIfNotExists (Join-Path $AgentsHome 'README.md') $rootReadme "Main README"
}

# ── .gitignore ─────────────────────────────────────────────────────
function Create-GitIgnore {
    Write-Host ""
    Write-Host "Creating .gitignore..."
    Write-Host ""

    $gitignore = @'
# OS-specific
.DS_Store
Thumbs.db

# IDE-specific
.vscode/
.idea/

# Temporary files
*.tmp
*.swp
*~
'@

    Create-FileIfNotExists (Join-Path $AgentsHome '.gitignore') $gitignore "Gitignore file"
}

# ── Summary ─────────────────────────────────────────────────────────
function Show-Summary {
    Write-Host ""
    Write-Host "========================================================="
    Write-Host "    ~/.agents Directory Initialized"
    Write-Host "========================================================="
    Write-Host ""
    Write-Host "Location: $AgentsHome"
    Write-Host ""
    Write-Host "Created following the .agents Protocol standards:"
    Write-Host "  - mcp.json & models.json"
    Write-Host "  - agents.md & system-prompt.md"
    Write-Host "  - skills/, agents/, tasks/, memories/ directories"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "  1. Link skills: .\setup-for-agents.ps1 -AgentsHome"
    Write-Host "  2. Update your MCP servers in $(Join-Path $AgentsHome 'mcp.json')"
    Write-Host "  3. Add persistent context in $(Join-Path $AgentsHome 'memories\')"
    Write-Host ""
    Write-Host "Documentation: $(Join-Path $AgentsHome 'README.md')"
    Write-Host ""
}

# ── Main ────────────────────────────────────────────────────────────
Write-Host "========================================================="
Write-Host "  Fei Skills Hub — Initialize ~/.agents"
Write-Host "========================================================="
Write-Host ""

if ($DryRun) {
    Write-Host "*** DRY RUN MODE — no changes will be made ***"
    Write-Host ""
}

# Confirm before proceeding (unless -Auto)
if (-not $Auto -and -not $DryRun) {
    Write-Host "This will create the directory structure at: $AgentsHome"
    Write-Host ""
    $confirm = Read-Host "Continue? (y/n)"
    if ($confirm -notmatch '^[Yy]$') {
        Write-Host "[info] Cancelled." -ForegroundColor Cyan
        exit 0
    }
}

# Create everything
Create-Structure
Create-ProtocolFiles
Create-GitIgnore

if ($DryRun) {
    Write-Host "[info] Dry run complete. Run without -DryRun to actually initialize." -ForegroundColor Cyan
} else {
    Show-Summary
}
