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
    [switch] $AgentsHome,
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
$SkillsSource = Join-Path $ScriptDir 'skills'

if (-not (Test-Path $SkillsSource -PathType Container)) {
    Write-Host "[fail] Skills source directory not found: $SkillsSource" -ForegroundColor Red
    exit 1
}

# ── Helper ──────────────────────────────────────────────────────────
$TargetsChosen = $false
if ($VsCode -or $Claude -or $Cursor -or $Windsurf -or $IntelliJ -or $Gemini -or $OpenCode -or $AgentsHome) {
    $TargetsChosen = $true
}

function ShouldInstall { param([string] $Name)
    if (-not $TargetsChosen) { return $true }
    $flag = "--$($Name.ToLowerInvariant())"
    return switch ($Name.ToLowerInvariant()) {
        'vscode'      { $VsCode }
        'claude'      { $Claude }
        'cursor'      { $Cursor }
        'windsurf'    { $Windsurf }
        'intellij'    { $IntelliJ }
        'gemini'      { $Gemini }
        'opencode'    { $OpenCode }
        'agentshome'  { $AgentsHome }
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

function Install-AgentsHome {
    Write-Host ""
    Write-Host "-- Local ~/.agents Directory --"
    $homeDir = $env:USERPROFILE
    $target = Join-Path $homeDir '.agents\skills'
    Link-OrCreate 'Agents Home' $target
}

# ── Main ────────────────────────────────────────────────────────────
Write-Host "========================================================"
Write-Host "       Fei Skills Hub -- Cross-Tool Installer"
Write-Host "========================================================"
Write-Host ""
Write-Host "Source: $SkillsSource"
if ($DryRun) { Write-Host "*** DRY RUN -- no changes will be made ***" }
Write-Host ""

if (ShouldInstall 'vscode')      { Install-VsCode }
if (ShouldInstall 'claude')      { Install-Claude }
if (ShouldInstall 'cursor')      { Install-Cursor }
if (ShouldInstall 'windsurf')    { Install-Windsurf }
if (ShouldInstall 'intellij')    { Install-IntelliJ }
if (ShouldInstall 'gemini')      { Install-Gemini }
if (ShouldInstall 'opencode')    { Install-OpenCode }
if (ShouldInstall 'agentshome')  { Install-AgentsHome }

Write-Host ""
if ($DryRun) {
    Write-Host "[info] Dry run complete. Run without -DryRun to actually install." -ForegroundColor Cyan
} else {
    $repoPath = (Resolve-Path $ScriptDir).Path
    Write-Host "[info] Done! Restart your tools to see the skills." -ForegroundColor Cyan
    Write-Host "[info] To update skills later: cd $repoPath && git pull" -ForegroundColor Cyan
}
