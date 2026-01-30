# Sprint Change Proposal: Codebase and Documentation Clutter Cleanup

**Date:** 2025-12-05  
**Workflow:** Correct Course - Sprint Change Management  
**Mode:** Batch  
**Status:** Draft for Review

---

## Section 1: Issue Summary

### Problem Statement

The SEIM project root directory and documentation structure have accumulated significant clutter over time, making navigation difficult and creating confusion about where to find specific information. The clutter includes:

1. **Multiple AI Agent Configuration Directories** (15+ directories)
   - `.agent/`, `.agentvibes/`, `.augment/`, `.bmad/`, `.claude/`, `.clinerules/`, `.codex/`, `.crush/`, `.cursor/`, `.gemini/`, `.iflow/`, `.opencode/`, `.qwen/`, `.rovodev/`, `.trae/`, `.windsurf/`
   - These are tool-specific configuration directories that should be consolidated or moved

2. **Root-Level Status/Summary Files**
   - `TEST_COVERAGE_IMPROVEMENTS.md` - Test coverage summary (completed work)
   - `VIDEO_DEMOS_GUIDE.md` - Video demo documentation
   - `VIDEO_DEMOS_READY.md` - Status file
   - `VIDEO_REVIEW_CHECKLIST.md` - Review checklist
   - `SYSTEM_STATUS.md` - System status report
   - `E2E_EXPANSION_PROGRESS.md` - Progress tracking
   - `E2E_QUICK_FIX_GUIDE.md` - Quick fix guide
   - `E2E_TEST_IMPLEMENTATION_STATUS.md` - Status tracking
   - These should be moved to appropriate documentation locations

3. **Documentation Duplication**
   - `docs/` directory contains generated/auto-generated documentation
   - `documentation/` directory contains manual documentation
   - Some overlap and confusion about which is authoritative
   - Need clear separation of concerns

4. **Coverage Directory at Root**
   - `coverage/` directory should be in `.gitignore` (already is) but visible structure is cluttered

5. **Multiple Docker Compose Files**
   - `docker-compose.yml` (main)
   - `docker-compose.e2e.yml` (E2E testing)
   - `docker-compose.local-prod.yml` (local production)
   - `docker-compose.override.yml` (overrides)
   - `docker-compose.prod.yml` (production)
   - These are legitimate but could be better organized

### Context

This issue was discovered during routine project maintenance when attempting to locate specific documentation. The clutter makes it difficult for:
- New developers to understand project structure
- AI assistants to find relevant documentation
- Maintainers to locate specific files
- Automated tools to parse project structure

### Evidence

- Root directory listing shows 15+ hidden directories (`.agent/`, `.bmad/`, etc.)
- Multiple markdown status files at root level
- Documentation exists in both `docs/` and `documentation/` with unclear boundaries
- README.md references both documentation locations without clear guidance

---

## Section 2: Impact Analysis

### Epic Impact

**No existing epics are directly affected.** This is a project maintenance and organization change that doesn't modify functionality.

**Potential New Epic:**
- **Epic: Project Organization & Documentation Structure** (if not already exists)
  - This change would be part of or initiate this epic

### Story Impact

**No current stories need modification.** This is a structural reorganization that doesn't change:
- Application functionality
- API contracts
- Database schema
- User workflows

**New Stories May Be Needed:**
- Story: Consolidate AI agent configuration directories
- Story: Reorganize root-level documentation files
- Story: Clarify documentation directory structure
- Story: Update README and documentation references

### Artifact Conflicts

#### PRD Impact
- **No PRD conflicts** - This is a maintenance task, not a feature change
- **Potential PRD Addition:** Add section on project structure and documentation organization standards

#### Architecture Document Impact
- **No architecture conflicts** - System architecture remains unchanged
- **Potential Update:** Add section on project directory structure and organization principles

#### UI/UX Specification Impact
- **No UI/UX impact** - This is purely a developer/maintainer concern

#### Documentation Impact
- **Major Documentation Updates Required:**
  1. Update `README.md` to clarify documentation structure
  2. Update `documentation/README.md` to explain manual vs generated docs
  3. Update `docs/index.md` to clarify its purpose
  4. Create `PROJECT_STRUCTURE.md` guide
  5. Update all documentation references to new file locations

### Technical Impact

#### Code Changes
- **Minimal code changes** - Primarily import path updates if any
- **No breaking changes** - All changes are organizational

#### Infrastructure Impact
- **No infrastructure changes** - Docker, database, deployment unaffected

#### Build System Impact
- **No build system changes** - Makefile, webpack, etc. remain unchanged

---

## Section 3: Recommended Approach

### Selected Path: **Direct Adjustment** (Option 1)

**Rationale:**
- This is a straightforward organizational change with no functional impact
- Can be implemented incrementally without disrupting development
- Low risk, high value for maintainability
- No need for rollback or MVP scope changes

### Implementation Strategy

**Phase 1: Consolidate AI Agent Directories**
- Move all `.agent*`, `.claude*`, `.bmad*`, etc. directories to `.tools/` or `.ide-config/`
- Update `.gitignore` if needed
- Document which tools use which directories

**Phase 2: Reorganize Root-Level Documentation**
- Move status/summary files to `docs/status/` or `documentation/status/`
- Move guides to appropriate documentation sections
- Archive completed work summaries

**Phase 3: Clarify Documentation Structure**
- Establish clear purpose for `docs/` (generated/auto-generated)
- Establish clear purpose for `documentation/` (manual/maintained)
- Create `PROJECT_STRUCTURE.md` guide
- Update all cross-references

**Phase 4: Update References**
- Update `README.md` with clear documentation structure
- Update all internal documentation links
- Verify all references still work

### Effort Estimate

- **Phase 1:** 2-4 hours (directory moves, .gitignore updates)
- **Phase 2:** 2-3 hours (file moves, organization)
- **Phase 3:** 3-4 hours (documentation updates, guide creation)
- **Phase 4:** 2-3 hours (reference updates, verification)

**Total:** 9-14 hours (1-2 days)

### Risk Assessment

- **Risk Level:** **Low**
  - No functional changes
  - No breaking changes
  - Can be done incrementally
  - Easy to verify correctness
  - Git history preserved

- **Mitigation:**
  - Work in feature branch
  - Test all documentation links after changes
  - Update references incrementally
  - Keep backup of current structure until verified

### Timeline Impact

- **No sprint timeline impact** - Can be done as maintenance task
- **No feature delivery delay** - Independent of feature work
- **Recommended:** Complete during low-activity period or as dedicated cleanup sprint

---

## Section 4: Detailed Change Proposals

### Change 1: Consolidate AI Agent Configuration Directories

**Current State:**
```
.agent/
.agentvibes/
.augment/
.bmad/
.claude/
.clinerules/
.codex/
.crush/
.cursor/
.gemini/
.iflow/
.opencode/
.qwen/
.rovodev/
.trae/
.windsurf/
```

**Proposed State:**
```
.tools/
  ├── agents/          # AI agent configurations
  │   ├── .agent/
  │   ├── .claude/
  │   ├── .bmad/
  │   └── ... (others)
  └── ide-config/      # IDE-specific configs
      ├── .cursor/
      └── ... (others)
```

**Rationale:**
- Consolidates 15+ directories into organized structure
- Reduces root directory clutter
- Makes it clear these are tool configurations
- Easier to manage and document

**Implementation:**
1. Create `.tools/agents/` and `.tools/ide-config/` directories
2. Move appropriate directories (preserve hidden status with `.` prefix if needed)
3. Update `.gitignore` if any patterns need adjustment
4. Document structure in `PROJECT_STRUCTURE.md`

**Files Affected:**
- Root directory structure
- `.gitignore` (if needed)
- `PROJECT_STRUCTURE.md` (new file)

---

### Change 2: Move Root-Level Status/Summary Files

**Current State:**
```
TEST_COVERAGE_IMPROVEMENTS.md
VIDEO_DEMOS_GUIDE.md
VIDEO_DEMOS_READY.md
VIDEO_REVIEW_CHECKLIST.md
SYSTEM_STATUS.md
E2E_EXPANSION_PROGRESS.md
E2E_QUICK_FIX_GUIDE.md
E2E_TEST_IMPLEMENTATION_STATUS.md
```

**Proposed State:**
```
docs/
  ├── status/                    # Status and progress tracking
  │   ├── test-coverage-improvements.md
  │   ├── system-status.md
  │   ├── e2e-expansion-progress.md
  │   └── e2e-test-implementation-status.md
  └── guides/                    # How-to guides
      ├── video-demos-guide.md
      ├── video-review-checklist.md
      ├── e2e-quick-fix-guide.md
      └── video-demos-ready.md (or archive)
```

**Rationale:**
- Removes clutter from root directory
- Organizes related files together
- Makes it easier to find status information
- Separates guides from status reports

**Implementation:**
1. Create `docs/status/` and `docs/guides/` directories
2. Move files with appropriate renaming (kebab-case)
3. Update any internal references
4. Update `docs/index.md` to include new sections

**Files Affected:**
- Root directory (8 files removed)
- `docs/status/` (4-5 new files)
- `docs/guides/` (3-4 new files)
- `docs/index.md` (updated)
- Any files referencing these (search and update)

---

### Change 3: Clarify Documentation Directory Structure

**Current State:**
- `docs/` - Contains generated documentation, status files, guides (mixed purpose)
- `documentation/` - Contains manual documentation, guides, architecture docs

**Proposed State:**
- `docs/` - **Generated/Auto-generated documentation**
  - `docs/architecture.md` - Auto-generated architecture
  - `docs/api-contracts.md` - Auto-generated API docs
  - `docs/data-models.md` - Auto-generated data models
  - `docs/status/` - Status and progress tracking
  - `docs/guides/` - Quick reference guides
  - `docs/index.md` - Index of generated docs

- `documentation/` - **Manual/Maintained documentation**
  - `documentation/README.md` - Documentation index
  - `documentation/architecture.md` - Manual architecture docs
  - `documentation/developer_guide.md` - Developer guide
  - `documentation/api_documentation.md` - Manual API docs
  - All other manual documentation

**Rationale:**
- Clear separation of concerns
- Easy to understand which docs are authoritative
- Prevents confusion about where to look
- Makes it clear which docs need manual updates

**Implementation:**
1. Create `PROJECT_STRUCTURE.md` explaining the structure
2. Update `README.md` with clear documentation section
3. Update `documentation/README.md` to explain manual docs
4. Update `docs/index.md` to explain generated docs
5. Move any misplaced files to correct locations

**Files Affected:**
- `PROJECT_STRUCTURE.md` (new)
- `README.md` (updated)
- `documentation/README.md` (updated)
- `docs/index.md` (updated)
- Any misplaced files (moved)

---

### Change 4: Update All Documentation References

**Current State:**
- README.md references both `docs/` and `documentation/` without clear distinction
- Internal documentation may have broken or unclear links
- No central guide to project structure

**Proposed State:**
- `README.md` has clear "Documentation" section explaining:
  - `docs/` for generated/auto-generated docs
  - `documentation/` for manual/maintained docs
  - Links to both with clear purposes
- `PROJECT_STRUCTURE.md` provides comprehensive structure guide
- All internal links updated and verified

**Rationale:**
- Prevents confusion for new developers
- Makes it easy to find the right documentation
- Sets clear expectations about documentation maintenance

**Implementation:**
1. Update `README.md` documentation section
2. Create `PROJECT_STRUCTURE.md`
3. Search for all references to moved files
4. Update all broken or unclear links
5. Verify all links work

**Files Affected:**
- `README.md` (updated)
- `PROJECT_STRUCTURE.md` (new)
- Any files with references to moved documentation (updated)

---

## Section 5: Implementation Handoff

### Change Scope Classification: **Minor** ✅

This change can be implemented directly by the development team without requiring:
- Backlog reorganization
- Product Owner coordination
- Scrum Master intervention
- Fundamental replanning

### Handoff Recipients ✅

**Primary:** Development Team
- Implement directory moves
- Update file references
- Create new documentation
- Verify all changes

**Secondary:** Technical Writer (if available)
- Review documentation updates
- Ensure clarity and consistency
- Verify all links work

### Handoff Status: **COMPLETE**

**Routed to:** Development Team for direct implementation  
**Deliverables Provided:**
- ✅ Comprehensive Sprint Change Proposal
- ✅ Detailed file move mappings
- ✅ Implementation checklist
- ✅ Success criteria
- ✅ PROJECT_STRUCTURE.md guide (created)

**Next Steps:**
1. Development team reviews proposal
2. Creates feature branch for changes
3. Implements changes incrementally (4 phases)
4. Verifies all links and references
5. Submits for review and merge

### Deliverables

1. **Reorganized Directory Structure**
   - Consolidated AI agent directories
   - Organized status/guide files
   - Clear documentation separation

2. **Updated Documentation**
   - `PROJECT_STRUCTURE.md` guide
   - Updated `README.md`
   - Updated documentation indexes
   - All internal links verified

3. **Verification Report**
   - All file moves completed
   - All references updated
   - All links verified working
   - No broken references

### Success Criteria

- [ ] Root directory has < 5 visible markdown files (README, LICENSE, CONTRIBUTING, etc.)
- [ ] All AI agent directories consolidated under `.tools/`
- [ ] All status/summary files moved to `docs/status/` or `docs/guides/`
- [ ] `PROJECT_STRUCTURE.md` created and comprehensive
- [ ] `README.md` clearly explains documentation structure
- [ ] All internal documentation links verified working
- [ ] No broken references in documentation
- [ ] Git history preserved (files moved, not deleted/recreated)
- [ ] `.gitignore` updated if needed
- [ ] All team members can find documentation easily

### Implementation Checklist

**Phase 1: AI Agent Directories**
- [ ] Create `.tools/agents/` directory
- [ ] Create `.tools/ide-config/` directory
- [ ] Move appropriate agent directories
- [ ] Update `.gitignore` if needed
- [ ] Document in `PROJECT_STRUCTURE.md`

**Phase 2: Root-Level Files**
- [ ] Create `docs/status/` directory
- [ ] Create `docs/guides/` directory
- [ ] Move status files to `docs/status/`
- [ ] Move guide files to `docs/guides/`
- [ ] Update `docs/index.md`

**Phase 3: Documentation Structure**
- [ ] Create `PROJECT_STRUCTURE.md`
- [ ] Update `README.md` documentation section
- [ ] Update `documentation/README.md`
- [ ] Update `docs/index.md`
- [ ] Move any misplaced files

**Phase 4: References**
- [ ] Search for all references to moved files
- [ ] Update all internal links
- [ ] Verify all links work
- [ ] Test documentation navigation
- [ ] Get team review

---

## Appendix: File Move Mapping

### AI Agent Directories
```
.agent/          → .tools/agents/.agent/
.agentvibes/     → .tools/agents/.agentvibes/
.augment/        → .tools/agents/.augment/
.bmad/           → .tools/agents/.bmad/
.claude/         → .tools/agents/.claude/
.clinerules/     → .tools/agents/.clinerules/
.codex/          → .tools/agents/.codex/
.crush/          → .tools/agents/.crush/
.gemini/         → .tools/agents/.gemini/
.iflow/          → .tools/agents/.iflow/
.opencode/       → .tools/agents/.opencode/
.qwen/           → .tools/agents/.qwen/
.rovodev/        → .tools/agents/.rovodev/
.trae/           → .tools/agents/.trae/
.windsurf/       → .tools/agents/.windsurf/
.cursor/         → .tools/ide-config/.cursor/
```

### Root-Level Documentation Files
```
TEST_COVERAGE_IMPROVEMENTS.md        → docs/status/test-coverage-improvements.md
SYSTEM_STATUS.md                     → docs/status/system-status.md
E2E_EXPANSION_PROGRESS.md            → docs/status/e2e-expansion-progress.md
E2E_TEST_IMPLEMENTATION_STATUS.md    → docs/status/e2e-test-implementation-status.md
VIDEO_DEMOS_GUIDE.md                 → docs/guides/video-demos-guide.md
VIDEO_REVIEW_CHECKLIST.md            → docs/guides/video-review-checklist.md
E2E_QUICK_FIX_GUIDE.md               → docs/guides/e2e-quick-fix-guide.md
VIDEO_DEMOS_READY.md                 → docs/status/video-demos-ready.md (or archive)
```

---

**Prepared by:** BMAD Correct Course Workflow  
**Date:** 2025-12-05  
**Status:** ✅ **APPROVED** - Ready for Implementation  
**Approved by:** Mario  
**Approval Date:** 2025-12-05
