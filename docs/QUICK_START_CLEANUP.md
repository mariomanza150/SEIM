# Quick Start: Project Structure Cleanup Implementation

**Date:** 2025-12-05  
**Task:** Implement codebase and documentation clutter cleanup  
**Estimated Time:** 9-14 hours

---

## 🚀 Step-by-Step Start Guide

### Step 1: Check Current Status

```bash
# Check current branch
git branch

# Check for uncommitted changes
git status

# If you have uncommitted changes, commit or stash them first
git stash  # or git commit -am "WIP: current work"
```

### Step 2: Update Main Branch

```bash
# Switch to main branch
git checkout main

# Pull latest changes
git pull origin main
```

### Step 3: Create Feature Branch

```bash
# Create and switch to new feature branch
git checkout -b cleanup/project-structure-2025-12-05

# Verify you're on the new branch
git branch
```

### Step 4: Review Implementation Guide

```bash
# Open the implementation guide
# Windows: start docs/sprint-change-proposal-2025-12-05-IMPLEMENTATION.md
# Or view in your editor
```

**Key Files to Review:**
- `docs/sprint-change-proposal-2025-12-05.md` - Full proposal
- `docs/sprint-change-proposal-2025-12-05-IMPLEMENTATION.md` - Step-by-step guide
- `docs/PROJECT_STRUCTURE.md` - Structure reference

### Step 5: Start Phase 1

**Phase 1: Consolidate AI Agent Directories (2-4 hours)**

```bash
# Create directory structure
mkdir -p .tools/agents
mkdir -p .tools/ide-config

# Move AI agent directories (use git mv to preserve history)
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

# Move IDE configs
git mv .cursor .tools/ide-config/
git mv .windsurf .tools/ide-config/

# Verify moves
ls -la .tools/agents/
ls -la .tools/ide-config/

# Commit Phase 1
git add .tools/
git commit -m "refactor: consolidate AI agent directories to .tools/"
```

### Step 6: Continue with Remaining Phases

Follow the detailed guide in `docs/sprint-change-proposal-2025-12-05-IMPLEMENTATION.md`:

- **Phase 2:** Move root-level files (2-3 hours)
- **Phase 3:** Clarify documentation structure (3-4 hours)
- **Phase 4:** Update all references (2-3 hours)

### Step 7: Final Verification

```bash
# Verify all changes
git status

# Check for any broken references
grep -r "TEST_COVERAGE_IMPROVEMENTS" . || echo "✓ No old references found"

# Run tests (should all pass)
docker-compose exec web pytest tests/ -v

# Review changes
git log --oneline
git diff main..HEAD --stat
```

### Step 8: Push and Create Pull Request

```bash
# Push branch to remote
git push origin cleanup/project-structure-2025-12-05

# Create PR on GitHub (or your Git platform)
# Title: "refactor: cleanup project structure and documentation organization"
# Description: Reference docs/sprint-change-proposal-2025-12-05.md
```

---

## 📋 Quick Checklist

Before starting:
- [ ] On main branch and up to date
- [ ] No uncommitted changes
- [ ] Reviewed implementation guide
- [ ] Understood all 4 phases

During implementation:
- [ ] Complete Phase 1, commit
- [ ] Complete Phase 2, commit
- [ ] Complete Phase 3, commit
- [ ] Complete Phase 4, commit
- [ ] Verify all changes

Before PR:
- [ ] All tests pass
- [ ] All references updated
- [ ] All links verified
- [ ] Success criteria met

---

## 🆘 Troubleshooting

### Issue: "Directory not found" when moving

**Solution:** Some directories might not exist. Skip them:
```bash
# Check if directory exists first
[ -d .agent ] && git mv .agent .tools/agents/ || echo ".agent not found, skipping"
```

### Issue: Git says "fatal: bad source"

**Solution:** Use regular `mv` if `git mv` fails, then `git add`:
```bash
mv .agent .tools/agents/
git add .tools/agents/.agent
git add .agent  # This stages the deletion
```

### Issue: Tools stop working after moving directories

**Solution:** Some tools might have hardcoded paths. Check tool documentation:
- Most tools will auto-detect new location
- Some may need configuration update
- Check `.tools/agents/.bmad/` for BMAD-specific configs

### Issue: Broken references after moves

**Solution:** Use comprehensive search:
```bash
# Find all references
grep -r "old-path" . --exclude-dir=.git

# Update systematically
# Use find/replace in your editor
```

---

## 📚 Reference Documents

- **Full Proposal:** `docs/sprint-change-proposal-2025-12-05.md`
- **Implementation Guide:** `docs/sprint-change-proposal-2025-12-05-IMPLEMENTATION.md`
- **Structure Guide:** `docs/PROJECT_STRUCTURE.md`
- **Contributing Guide:** `CONTRIBUTING.md`

---

## ✅ Success Criteria

When complete, verify:
- [ ] Root directory has < 10 visible markdown files
- [ ] All AI agent directories under `.tools/`
- [ ] All status files in `docs/status/`
- [ ] All guide files in `docs/guides/`
- [ ] PROJECT_STRUCTURE.md exists and is comprehensive
- [ ] README.md updated with clear documentation section
- [ ] All internal links work
- [ ] All tests pass
- [ ] Git history preserved

---

**Ready to start?** Begin with Step 1 above! 🚀
