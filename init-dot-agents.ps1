# Fei Skills Hub — Initialize the .agents Protocol
#
# This script links this repository's .agents directory to ~/.agents,
# following the .agents Protocol (https://dotagentsprotocol.com/).
#
# Usage:  .\init-dot-agents.ps1                  # interactive mode
#         .\init-dot-agents.ps1 -Auto             # auto-confirm all prompts
#         .\init-dot-agents.ps1 -DryRun           # preview only

param(
    [switch]$DryRun,
    [switch]$Auto
)

# ── Colors ──────────────────────────────────────────────────────────
function Info    { param($msg) Write-Host "[info]  $msg" -ForegroundColor Cyan }
function Ok      { param($msg) Write-Host "[ok]    $msg" -ForegroundColor Green }
function Warn    { param($msg) Write-Host "[warn]  $msg" -ForegroundColor Yellow }
function Fail    { param($msg) Write-Host "[fail]  $msg" -ForegroundColor Red }

# ── Paths ───────────────────────────────────────────────────────────
$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$AgentsHome  = Join-Path $ScriptDir ".agents"

# ── Validate repo .agents directory ─────────────────────────────────
function Validate-Agents {
    if (-not (Test-Path $AgentsHome -PathType Container)) {
        Fail "Cannot find .agents directory at: $AgentsHome"
        Fail "Make sure you are running this script from the repository root."
        exit 1
    }

    $required = @("skills", "agents.md", "system-prompt.md", "mcp.json", "models.json")
    $missing = $required | Where-Object { -not (Test-Path (Join-Path $AgentsHome $_)) }

    if ($missing) {
        Fail "The .agents directory is missing required items:"
        foreach ($m in $missing) { Fail "  - $m" }
        Fail "Please update your repository and try again."
        exit 1
    }
}

# ── Handle existing ~/.agents ───────────────────────────────────────
function Handle-Existing {
    $userAgents = Join-Path $env:USERPROFILE ".agents"

    # Check if it's already a symlink/junction pointing to our repo (idempotent)
    if (Test-Path $userAgents) {
        $item = Get-Item $userAgents -ErrorAction SilentlyContinue
        if ($item.Target -and $item.Target -eq $AgentsHome) {
            Ok "~/.agents is already linked to this repository."
            return $false  # nothing to do
        }
    }

    Warn "~/.agents already exists."
    Write-Host ""
    Write-Host "  (b) Back up the existing directory (rename with timestamp)"
    Write-Host "  (q) Quit — do nothing"
    Write-Host ""

    if ($Auto) {
        $choice = "b"
    } else {
        $choice = Read-Host "Choose an option (b/q)"
    }

    switch ($choice) {
        "b" {
            $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
            $bkp = "${userAgents}.bak.${timestamp}"
            if ($DryRun) {
                Info "[DRY RUN] Move-Item ~/.agents $bkp"
            } else {
                Move-Item $userAgents $bkp
                Ok "Backed up existing ~/.agents to $bkp"
            }
            return $true
        }
        "q" {
            Info "Cancelled. No changes made."
            exit 0
        }
        default {
            Fail "Invalid option. Exiting."
            exit 1
        }
    }
}

# ── Create symlink ──────────────────────────────────────────────────
function Create-Symlink {
    $userAgents = Join-Path $env:USERPROFILE ".agents"

    if ($DryRun) {
        Info "[DRY RUN] New-Item -ItemType Junction -Path ~/.agents -Target $AgentsHome"
        return
    }

    # Use directory junction (no admin required on Windows)
    New-Item -ItemType Junction -Path $userAgents -Target $AgentsHome | Out-Null
    Ok "Linked: ~/.agents -> $AgentsHome"

    Write-Host ""
    Write-Host "Available skills:"
    Get-ChildItem (Join-Path $userAgents "skills") -Directory | ForEach-Object { Write-Host "  $($_.Name)" }
}

# ── Summary ─────────────────────────────────────────────────────────
function Show-Summary {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════╗"
    Write-Host "║       .agents Protocol Initialized                      ║"
    Write-Host "╚══════════════════════════════════════════════════════════╝"
    Write-Host ""
    Write-Host "  Source:  $AgentsHome"
    Write-Host "  Target:  $(Join-Path $env:USERPROFILE '.agents')"
    Write-Host ""
    Write-Host "Your AI tools (Claude Code, Cursor, Copilot, etc.) can"
    Write-Host "now use the skills, prompts, and agent configs from this hub."
    Write-Host ""
}

# ── Main ────────────────────────────────────────────────────────────
function Main {
    Write-Host "╔══════════════════════════════════════════════════════════╗"
    Write-Host "║     Fei Skills Hub — Initialize .agents                 ║"
    Write-Host "╚══════════════════════════════════════════════════════════╝"
    Write-Host ""

    if ($DryRun) {
        Write-Host "*** DRY RUN MODE — no changes will be made ***"
        Write-Host ""
    }

    # Step 1: Validate repo structure
    Validate-Agents

    # Step 2: Confirm (unless -Auto)
    if (-not $Auto -and -not $DryRun) {
        Write-Host "This will link ~/.agents -> $AgentsHome"
        Write-Host ""
        $confirm = Read-Host "Continue? (y/n)"
        if ($confirm -notmatch '^[Yy]$') {
            Info "Cancelled."
            exit 0
        }
    }

    # Step 3: Handle existing ~/.agents
    $userAgents = Join-Path $env:USERPROFILE ".agents"
    if (Test-Path $userAgents) {
        $proceed = Handle-Existing
        if (-not $proceed) {
            Show-Summary
            return
        }
    }

    # Step 4: Create the symlink
    Create-Symlink

    if ($DryRun) {
        Info "Dry run complete. Run without -DryRun to apply changes."
    } else {
        Show-Summary
    }
}

Main
