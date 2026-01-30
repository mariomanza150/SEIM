# Implementation Guide: Codebase and Documentation Clutter Cleanup

**Based on:** Sprint Change Proposal 2025-12-05  
**Status:** Ready for Implementation  
**Estimated Time:** 9-14 hours (1-2 days)

---

## Quick Start

1. Create feature branch: `git checkout -b cleanup/project-structure-2025-12-05`
2. Follow phases in order
3. Test after each phase
4. Submit PR when complete

---

## Phase 1: Consolidate AI Agent Directories

**Time:** 2-4 hours  
**Risk:** Low

### Steps

1. **Create directory structure:**
   ```bash
   mkdir -p .tools/agents
   mkdir -p .tools/ide-config
   ```

2. **Move agent directories:**
   ```bash
   # Move AI agent configs
   mv .agent .tools/agents/
   mv .agentvibes .tools/agents/
   mv .augment .tools/agents/
   mv .bmad .tools/agents/
   mv .claude .tools/agents/
   mv .clinerules .tools/agents/
   mv .codex .tools/agents/
   mv .crush .tools/agents/
   mv .gemini .tools/agents/
   mv .iflow .tools/agents/
   mv .opencode .tools/agents/
   mv .qwen .tools/agents/
   mv .rovodev .tools/agents/
   mv .trae .tools/agents/
   
   # Move IDE configs
   mv .cursor .tools/ide-config/
   mv .windsurf .tools/ide-config/
   ```

3. **Update .gitignore (if needed):**
   - Check if any patterns need adjustment
   - Verify hidden directories are still ignored

4. **Test:**
   - Verify tools still work (if any are actively used)
   - Check git status shows moves correctly

5. **Commit:**
   ```bash
   git add .tools/
   git add .gitignore
   git commit -m "refactor: consolidate AI agent directories to .tools/"
   ```

---

## Phase 2: Move Root-Level Status/Summary Files

**Time:** 2-3 hours  
**Risk:** Low

### Steps

1. **Create directories:**
   ```bash
   mkdir -p docs/status
   mkdir -p docs/guides
   ```

2. **Move and rename files:**
   ```bash
   # Status files
   git mv TEST_COVERAGE_IMPROVEMENTS.md docs/status/test-coverage-improvements.md
   git mv SYSTEM_STATUS.md docs/status/system-status.md
   git mv E2E_EXPANSION_PROGRESS.md docs/status/e2e-expansion-progress.md
   git mv E2E_TEST_IMPLEMENTATION_STATUS.md docs/status/e2e-test-implementation-status.md
   git mv VIDEO_DEMOS_READY.md docs/status/video-demos-ready.md
   
   # Guide files
   git mv VIDEO_DEMOS_GUIDE.md docs/guides/video-demos-guide.md
   git mv VIDEO_REVIEW_CHECKLIST.md docs/guides/video-review-checklist.md
   git mv E2E_QUICK_FIX_GUIDE.md docs/guides/e2e-quick-fix-guide.md
   ```

   **Note:** Use `git mv` to preserve history

3. **Update docs/index.md:**
   - Add sections for status and guides
   - Link to new file locations

4. **Search for references:**
   ```bash
   # Search for references to old file names
   grep -r "TEST_COVERAGE_IMPROVEMENTS" .
   grep -r "VIDEO_DEMOS_GUIDE" .
   grep -r "SYSTEM_STATUS" .
   # ... etc for all moved files
   ```

5. **Update references:**
   - Update any files that reference the old locations
   - Update README.md if it references these files

6. **Test:**
   - Verify all links work
   - Check documentation navigation

7. **Commit:**
   ```bash
   git add docs/
   git add README.md
   git commit -m "refactor: move root-level status and guide files to docs/"
   ```

---

## Phase 3: Clarify Documentation Structure

**Time:** 3-4 hours  
**Risk:** Low

### Steps

1. **Review current documentation:**
   - Identify any files in wrong location
   - Note any duplicates or conflicts

2. **Update PROJECT_STRUCTURE.md:**
   - Already created, verify it's comprehensive
   - Add any missing details

3. **Update README.md:**
   - Add clear "Documentation" section
   - Explain `docs/` vs `documentation/`
   - Link to PROJECT_STRUCTURE.md

4. **Update documentation/README.md:**
   - Clarify this is for manual documentation
   - Link to docs/ for generated docs
   - Explain maintenance responsibility

5. **Update docs/index.md:**
   - Clarify this is for generated docs
   - Link to documentation/ for manual docs
   - Explain regeneration process

6. **Move any misplaced files:**
   - If any generated docs are in `documentation/`, move to `docs/`
   - If any manual docs are in `docs/`, move to `documentation/`

7. **Test:**
   - Verify all documentation links work
   - Check navigation makes sense

8. **Commit:**
   ```bash
   git add PROJECT_STRUCTURE.md
   git add README.md
   git add documentation/README.md
   git add docs/index.md
   git commit -m "docs: clarify documentation structure and add PROJECT_STRUCTURE guide"
   ```

---

## Phase 4: Update All References

**Time:** 2-3 hours  
**Risk:** Low

### Steps

1. **Comprehensive reference search:**
   ```bash
   # Search for all old file paths
   grep -r "TEST_COVERAGE_IMPROVEMENTS" .
   grep -r "VIDEO_DEMOS_GUIDE" .
   grep -r "SYSTEM_STATUS" .
   grep -r "\.agent/" .
   grep -r "\.bmad/" .
   grep -r "\.claude/" .
   # ... etc
   ```

2. **Update all references:**
   - Update markdown links
   - Update code comments
   - Update documentation cross-references
   - Update any scripts that reference old paths

3. **Verify all links:**
   ```bash
   # Use a link checker if available
   # Or manually verify key documentation links
   ```

4. **Update .gitignore if needed:**
   - Ensure new paths are covered
   - Remove any obsolete patterns

5. **Final verification:**
   - Run full test suite (should pass)
   - Check documentation builds (if applicable)
   - Verify no broken links

6. **Commit:**
   ```bash
   git add .
   git commit -m "docs: update all references to new file locations"
   ```

---

## Final Verification Checklist

Before submitting PR:

- [ ] All directories moved successfully
- [ ] All files moved with `git mv` (history preserved)
- [ ] All references updated
- [ ] All links verified working
- [ ] PROJECT_STRUCTURE.md is comprehensive
- [ ] README.md updated with clear documentation section
- [ ] documentation/README.md updated
- [ ] docs/index.md updated
- [ ] No broken references
- [ ] Git history preserved (use `git log --follow` to verify)
- [ ] Root directory has < 10 visible markdown files
- [ ] All team members can navigate structure easily

---

## Testing Commands

```bash
# Verify git history preserved
git log --follow -- docs/status/test-coverage-improvements.md

# Check for broken references
grep -r "TEST_COVERAGE_IMPROVEMENTS" . || echo "No references found - good!"

# Verify directory structure
tree -L 2 .tools/ docs/ documentation/ | head -50

# Run tests (should all pass)
docker-compose exec web pytest tests/ -v
```

---

## Rollback Plan

If issues arise:

1. **Git revert:**
   ```bash
   git revert HEAD
   # Or revert specific commits
   ```

2. **Manual restore:**
   - Files moved with `git mv` can be restored with `git mv` in reverse
   - Check git log for original locations

3. **No data loss:**
   - All changes preserve git history
   - No files deleted, only moved

---

## Success Criteria

- [ ] Root directory clean (< 10 visible markdown files)
- [ ] All AI agent directories consolidated
- [ ] All status/guide files organized
- [ ] Documentation structure clear
- [ ] All references updated
- [ ] All links working
- [ ] Team can navigate easily
- [ ] PROJECT_STRUCTURE.md comprehensive

---

## Questions or Issues?

- Check PROJECT_STRUCTURE.md for guidance
- Review original Sprint Change Proposal
- Consult with team if unclear

---

**Ready to implement!** Follow phases in order and test after each phase.
