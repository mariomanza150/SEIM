# Manual Cleanup Execution Guide

**Date:** 2025-12-05  
**Issue:** Automated moves not executing - manual execution required

---

## ⚠️ Current Status

The cleanup implementation was planned and documented, but the actual file moves need to be executed manually. The PowerShell commands are not creating directories or moving files as expected.

---

## 🔧 Manual Execution Steps

### Step 1: Create Directory Structure

**PowerShell:**
```powershell
New-Item -ItemType Directory -Path .tools\agents -Force
New-Item -ItemType Directory -Path .tools\ide-config -Force
New-Item -ItemType Directory -Path docs\status -Force
New-Item -ItemType Directory -Path docs\guides -Force
```

**Verify:**
```powershell
Test-Path .tools\agents
Test-Path docs\status
```

---

### Step 2: Move AI Agent Directories

**For tracked files (use git mv):**
```powershell
# Check if tracked first
git ls-files | Select-String "^\.agent"

# If tracked, use git mv
git mv .agent .tools/agents/
git mv .agentvibes .tools/agents/
git mv .augment .tools/agents/
git mv .bmad .tools/agents/
git mv .claude .tools/agents/
git mv .clinerules .tools/agents/
git mv .codex .tools/agents/
git mv .crush .tools/agents/
git mv .gemini .tools/agents/
git mv .iflow .tools/agents/
git mv .opencode .tools/agents/
git mv .qwen .tools/agents/
git mv .rovodev .tools/agents/
git mv .trae .tools/agents/
git mv .cursor .tools/ide-config/
git mv .windsurf .tools/ide-config/
```

**For untracked files (use Move-Item then git add):**
```powershell
# If not tracked, use regular move
Move-Item -Path .agent -Destination .tools/agents/ -Force
git add .tools/agents/.agent
git add .agent  # Stages deletion
```

**Commit:**
```powershell
git add .tools/
git commit -m "refactor: consolidate AI agent directories to .tools/"
```

---

### Step 3: Move Root-Level Files

**Status Files:**
```powershell
# Check if tracked
git ls-files | Select-String "^(TEST_COVERAGE|SYSTEM_STATUS|E2E_)"

# Move files
if (Test-Path TEST_COVERAGE_IMPROVEMENTS.md) {
    if (git ls-files --error-unmatch TEST_COVERAGE_IMPROVEMENTS.md 2>$null) {
        git mv TEST_COVERAGE_IMPROVEMENTS.md docs/status/test-coverage-improvements.md
    } else {
        Move-Item TEST_COVERAGE_IMPROVEMENTS.md docs/status/test-coverage-improvements.md -Force
        git add docs/status/test-coverage-improvements.md
    }
}

# Repeat for:
# - SYSTEM_STATUS.md → docs/status/system-status.md
# - E2E_EXPANSION_PROGRESS.md → docs/status/e2e-expansion-progress.md
# - E2E_TEST_IMPLEMENTATION_STATUS.md → docs/status/e2e-test-implementation-status.md
# - VIDEO_DEMOS_READY.md → docs/status/video-demos-ready.md
```

**Guide Files:**
```powershell
# Move guide files
if (Test-Path VIDEO_DEMOS_GUIDE.md) {
    git mv VIDEO_DEMOS_GUIDE.md docs/guides/video-demos-guide.md
}
if (Test-Path VIDEO_REVIEW_CHECKLIST.md) {
    git mv VIDEO_REVIEW_CHECKLIST.md docs/guides/video-review-checklist.md
}
if (Test-Path E2E_QUICK_FIX_GUIDE.md) {
    git mv E2E_QUICK_FIX_GUIDE.md docs/guides/e2e-quick-fix-guide.md
}
```

**Commit:**
```powershell
git add docs/
git commit -m "refactor: move root-level status and guide files to docs/"
```

---

### Step 4: Verify Moves

**Check directories exist:**
```powershell
Get-ChildItem .tools/agents/ | Select-Object Name
Get-ChildItem docs/status/ | Select-Object Name
Get-ChildItem docs/guides/ | Select-Object Name
```

**Check root is clean:**
```powershell
Get-ChildItem -File | Where-Object { $_.Name -match '^(VIDEO_|TEST_|SYSTEM_|E2E_)' }
# Should return empty or only untracked files
```

**Check git status:**
```powershell
git status --short
# Should show renames (R) for moved files
```

**Verify git history:**
```powershell
git log --follow -- docs/status/test-coverage-improvements.md
# Should show history including original TEST_COVERAGE_IMPROVEMENTS.md
```

---

## 📝 Alternative: Use File Explorer

If PowerShell commands continue to fail:

1. **Create directories manually:**
   - `.tools/agents/`
   - `.tools/ide-config/`
   - `docs/status/`
   - `docs/guides/`

2. **Move files using File Explorer:**
   - Drag and drop files to new locations
   - Then use `git add` to stage the moves

3. **Stage moves in git:**
   ```powershell
   git add .tools/
   git add docs/
   git commit -m "refactor: organize project structure"
   ```

---

## ✅ Success Criteria

After manual execution, verify:

- [ ] `.tools/agents/` contains moved agent directories
- [ ] `.tools/ide-config/` contains moved IDE configs
- [ ] `docs/status/` contains moved status files
- [ ] `docs/guides/` contains moved guide files
- [ ] Root directory no longer has clutter files
- [ ] `git status` shows renames (R)
- [ ] `git log --follow` works on moved files

---

## 🆘 Troubleshooting

**Issue: "Directory not found"**
- Check current directory: `pwd`
- Use absolute paths if needed
- Verify you're in the SEIM project root

**Issue: "Permission denied"**
- Run PowerShell as Administrator
- Check file/directory permissions
- Ensure files aren't locked by other processes

**Issue: "git mv fails"**
- File might not be tracked: use `Move-Item` then `git add`
- Check git status first: `git status`
- Ensure you're on the correct branch

---

**Status:** ⚠️ Manual execution required  
**Estimated Time:** 30-60 minutes  
**Difficulty:** Low (straightforward file moves)
