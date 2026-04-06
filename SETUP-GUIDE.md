# Install Fei Skills Hub

One clone, all your AI tools get the skills automatically.

---

## Quick Install (Recommended)

### Step 1: Clone the repo

```bash
git clone https://github.com/FeiWangHub/fei_skills_hub.git ~/fei-skills
cd ~/fei-skills
```

### Step 2: Run the installer

```bash
bash setup-for-agents.sh
```

That's it. The script detects which tools you have installed and symlinks the skills
directory to each tool's prompt location. Use `--dry-run` first to preview:

```bash
bash setup-for-agents.sh --dry-run
```

### Install only for specific tools

```bash
bash setup-for-agents.sh --vscode          # only VS Code
bash setup-for-agents.sh --claude          # only Claude Code
bash setup-for-agents.sh --vscode --claude --windsurf  # pick multiple
```

### Force reinstall

```bash
bash setup-for-agents.sh --force           # overwrite existing symlinks/links
```

---

## Manual Install (Per Tool)

If the script doesn't work for you, here are the exact paths per tool.
Replace `~/fei-skills` with wherever you cloned the repo.

> All instructions create **symlinks** so that `git pull` in the repo directory
> instantly updates all tools — no need to reinstall.

### VS Code + GitHub Copilot

**macOS:**
```bash
ln -s ~/fei-skills/.github/skills \
  "$HOME/Library/Application Support/Code/User/prompts/fei-skills"
```

**Linux:**
```bash
ln -s ~/fei-skills/.github/skills \
  "$HOME/.config/Code/User/prompts/fei-skills"
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType SymbolicLink `
  -Path "$env:APPDATA\Code\User\prompts\fei-skills" `
  -Target "$HOME\fei-skills\.github\skills"
```

Restart VS Code, type `/` in Copilot Chat.

---

### Claude Code

```bash
mkdir -p ~/.claude/SKILLS
ln -s ~/fei-skills/.github/skills ~/.claude/SKILLS/fei-skills
```

Alternatively, Claude Code also reads workspace-level prompts — add as a git
submodule in any project:

```bash
cd your-project/
git submodule add https://github.com/FeiWangHub/fei_skills_hub.git .github/skills/fei-skills
```

---

### Cursor

```bash
mkdir -p ~/.cursor/rules
ln -s ~/fei-skills/.github/skills ~/.cursor/rules/fei-skills
```

---

### Windsurf

```bash
mkdir -p ~/.codeium/windsurf/prompts
ln -s ~/fei-skills/.github/skills ~/.codeium/windsurf/prompts/fei-skills
```

---

### IntelliJ IDEA + GitHub Copilot

**macOS:** JetBrains Copilot plugin paths vary by IDE version. Try:

```bash
mkdir -p "$HOME/Library/Application Support/CopilotChat/prompts"
ln -s ~/fei-skills/.github/skills \
  "$HOME/Library/Application Support/CopilotChat/prompts/fei-skills"
```

If your IDE uses a different config directory, find it via:
**Help → Show Config in Explorer**

Then create the `prompts/fei-skills` symlink there.

**Linux:**
```bash
mkdir -p "$HOME/.local/share/CopilotChat/prompts"
ln -s ~/fei-skills/.github/skills \
  "$HOME/.local/share/CopilotChat/prompts/fei-skills"
```

---

### Gemini CLI

```bash
mkdir -p ~/.gemini-cli/prompts
ln -s ~/fei-skills/.github/skills ~/.gemini-cli/prompts/fei-skills
```

---

### OpenCode

```bash
mkdir -p ~/.opencode/prompts
ln -s ~/fei-skills/.github/skills ~/.opencode/prompts/fei-skills
```

---

## Updating Skills

All symlinks point back to the same repo. To get new skills or updates:

```bash
cd ~/fei-skills
git pull
```

Every tool will see the changes after restart.

## Uninstall

Remove the symlinks and optionally the cloned repo:

```bash
bash setup-for-agents.sh --dry-run   # see what was created
# Then manually remove the symlinks:
rm "$HOME/Library/Application Support/Code/User/prompts/fei-skills"
rm ~/.claude/SKILLS/fei-skills
# ... etc
rm -rf ~/fei-skills         # remove the cloned repo
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `setup-for-agents.sh` says "Skills source directory not found" | Make sure you cloned the repo and are in the repo directory |
| Symlink creation fails | Run as Administrator on Windows. Script auto-falls back to `cp -R` if symlinks aren't supported |
| Skills don't appear in VS Code | Type `/` in Copilot Chat, or run `Developer: Reload Window` |
| Skills don't appear in Claude Code | Restart Claude Code or run `/clear` then try again |
| Tool version uses a different prompt path | See the manual section above — paths may vary by tool version |
| Want to use a fork or custom branch | Clone your fork instead and run the same install script |
