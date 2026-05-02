<#
.SYNOPSIS
    Fei Skills Hub — Initialize ~/.agents directory structure
.DESCRIPTION
    Creates the directory structure for ~/.agents, which is used as a local hub 
    for agent skills and configurations.
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
$ConfigDir = Join-Path $AgentsHome 'config'
$CacheDir = Join-Path $AgentsHome 'cache'
$DataDir = Join-Path $AgentsHome 'data'

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
    Write-Host "Creating ~/.agents directory structure..."
    Write-Host ""

    # Main directories
    Create-DirectoryIfNotExists $AgentsHome "Agents home directory"
    Create-DirectoryIfNotExists $SkillsDir "Skills directory"
    Create-DirectoryIfNotExists $ConfigDir "Configuration directory"
    Create-DirectoryIfNotExists $CacheDir "Cache directory"
    Create-DirectoryIfNotExists $DataDir "Data directory"

    # Skills subdirectories (organized by domain)
    Create-DirectoryIfNotExists (Join-Path $SkillsDir 'frontend') "Frontend skills"
    Create-DirectoryIfNotExists (Join-Path $SkillsDir 'backend') "Backend skills"
    Create-DirectoryIfNotExists (Join-Path $SkillsDir 'devops') "DevOps skills"
    Create-DirectoryIfNotExists (Join-Path $SkillsDir 'data') "Data skills"
    Create-DirectoryIfNotExists (Join-Path $SkillsDir 'platform') "Platform skills"
    Create-DirectoryIfNotExists (Join-Path $SkillsDir 'security') "Security skills"
    Create-DirectoryIfNotExists (Join-Path $SkillsDir 'ai') "AI skills"
    Create-DirectoryIfNotExists (Join-Path $SkillsDir 'mobile') "Mobile skills"
    Create-DirectoryIfNotExists (Join-Path $SkillsDir 'infrastructure') "Infrastructure skills"

    # Config subdirectories
    Create-DirectoryIfNotExists (Join-Path $ConfigDir 'agents') "Agent configurations"
    Create-DirectoryIfNotExists (Join-Path $ConfigDir 'tools') "Tool configurations"

    # Cache subdirectories
    Create-DirectoryIfNotExists (Join-Path $CacheDir 'search') "Search cache"
    Create-DirectoryIfNotExists (Join-Path $CacheDir 'analysis') "Analysis cache"

    # Data subdirectories
    Create-DirectoryIfNotExists (Join-Path $DataDir 'logs') "Log files"
    Create-DirectoryIfNotExists (Join-Path $DataDir 'projects') "Project metadata"
}

# ── README Files ────────────────────────────────────────────────────
function Create-ReadmeFiles {
    Write-Host ""
    Write-Host "Creating README files..."
    Write-Host ""

    $rootReadme = @'
# ~/.agents Directory

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
   ```powershell
   .\setup-for-agents.ps1 -AgentsHome
   ```

2. Install skills into specific domains:
   ```
   Frontend skills will appear in .\skills\frontend\
   Backend skills will appear in .\skills\backend\
   etc.
   ```

3. Configure tools to use ~/.agents as their skill root

## Tips

- Keep config files as YAML or JSON for easy parsing
- Log important operations in data/logs/
- Clear cache/ periodically to save disk space
- Version control: Consider committing config/ but not cache/

---

Created by: Fei Skills Hub Initializer
'@

    Create-FileIfNotExists (Join-Path $AgentsHome 'README.md') $rootReadme "Main README"

    $skillsReadme = @'
# Skills Directory

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

1. Create a subdirectory for your skill: `mkdir -p frontend\my-skill`
2. Add a SKILL.md or README.md with documentation
3. Include templates and scripts as needed

---

Skills are typically symlinked or copied from Fei Skills Hub.
'@

    Create-FileIfNotExists (Join-Path $SkillsDir 'README.md') $skillsReadme "Skills README"

    $configReadme = @'
# Configuration Directory

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
'@

    Create-FileIfNotExists (Join-Path $ConfigDir 'README.md') $configReadme "Config README"
}

# ── .gitignore ─────────────────────────────────────────────────────
function Create-GitIgnore {
    Write-Host ""
    Write-Host "Creating .gitignore..."
    Write-Host ""

    $gitignore = @'
# Cache (regenerated)
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
'@

    Create-FileIfNotExists (Join-Path $AgentsHome '.gitignore') $gitignore "Gitignore file"
}

# ── Environment Config ──────────────────────────────────────────────
function Create-EnvConfig {
    Write-Host ""
    Write-Host "Creating environment configuration..."
    Write-Host ""

    $envExample = @'
# Fei Skills Hub — Local Agent Configuration

# Set to true to enable debug logging
DEBUG=false

# Skills root directory
SKILLS_ROOT=${HOME}\.agents\skills

# Log level (debug, info, warn, error)
LOG_LEVEL=info

# Cache settings
CACHE_ENABLED=true
CACHE_TTL=3600

# Add custom paths as needed
CUSTOM_SKILLS_PATH=
'@

    Create-FileIfNotExists (Join-Path $ConfigDir '.env.example') $envExample "Environment example"
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
    Write-Host "Next steps:"
    Write-Host "  1. Link skills: .\setup-for-agents.ps1 -AgentsHome"
    Write-Host "  2. Configure tools to use: $AgentsHome\skills"
    Write-Host "  3. Add custom configurations in: $ConfigDir\"
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
Create-ReadmeFiles
Create-GitIgnore
Create-EnvConfig

if ($DryRun) {
    Write-Host "[info] Dry run complete. Run without -DryRun to actually initialize." -ForegroundColor Cyan
} else {
    Show-Summary
}
