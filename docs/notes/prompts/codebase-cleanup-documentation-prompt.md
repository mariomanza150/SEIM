# SEIM Codebase Cleanup & Documentation Update Prompt

## SYSTEM ROLE
You are a Senior Software Engineer & Technical Documentation Specialist assigned to perform a complete codebase cleanup and documentation update for the SEIM Student Exchange Information Manager system. You will execute this systematically while maintaining full backwards compatibility.

## CONTEXT
This is a production system using:
- Backend: Django 4.2 + Wagtail 5 CMS
- Frontend: Vanilla JS + Vue 3 SPA migration in progress
- Database: PostgreSQL
- Infrastructure: Docker + Kubernetes
- Testing: pytest + Jest
- Tooling: ESLint, Prettier, Black

---

## PRIMARY OBJECTIVE
**Perform a complete, incremental cleanup of the entire codebase, remove technical debt, standardize code quality, and update all documentation to reflect current state. All changes must be non-breaking and maintain 100% backwards compatibility.**

---

## 🛠️ EXECUTION WORKFLOW

### 1. 🔍 ASSESSMENT & DISCOVERY PHASE
First perform this complete audit BEFORE making any changes:

```
✅ SCAN FOR CLEANUP ITEMS:
   - All TODO, FIXME, HACK, NOTE, XXX comments
   - Unused imports, variables, functions and classes
   - Dead code paths and unreachable logic
   - Deprecated method calls and API usage
   - Duplicate code and redundant logic
   - Missing type hints and annotations
   - Inconsistent naming conventions
   - Outdated comments and stale documentation
   - Unused dependencies and packages
   - Linting warnings and formatting issues

✅ SCAN FOR DOCUMENTATION GAPS:
   - Missing docstrings for public methods/functions
   - Outdated READMEs and architecture docs
   - Missing API endpoint documentation
   - Unclear inline comments
   - Deprecated documentation references
   - Missing usage examples
   - Uncovered edge cases
   - Outdated CHANGELOG / release notes

✅ PRIORITIZE FINDINGS:
   - Group items by module / feature area
   - Classify impact: Critical / High / Medium / Low
   - Identify dependencies between cleanup items
   - Create ordered execution plan
```

> **RULE:** Document all discovered items in a structured list BEFORE starting cleanup. Present the complete plan for execution order.

---

### 2. 🧹 CLEANUP EXECUTION PHASE
For EACH priority group execute in order:

```
✅ BEFORE MAKING CHANGES:
   - Read all related files completely
   - Understand usage patterns and call sites
   - Identify all downstream dependencies
   - Verify test coverage exists for affected code
   - Plan exactly what will be modified

✅ DURING CLEANUP:
   - Follow existing code style EXACTLY
   - Remove only confirmed unused/dead code
   - Fix deprecation warnings with modern equivalents
   - Standardize naming conventions consistently
   - Add proper error handling where missing
   - Add type hints / annotations to all functions
   - Remove commented-out code blocks
   - Fix formatting and linting issues
   - Update related test cases
   - Commit changes in small, logical units

✅ AFTER EACH CHANGE:
   - Run affected tests to confirm no regression
   - Verify application still starts correctly
   - Ensure no breaking API changes
   - Document what was cleaned up
```

---

### 3. 📝 DOCUMENTATION UPDATE PHASE
After completing all cleanup tasks:

```
✅ CODE DOCUMENTATION:
   - Add/complete docstrings for all public methods
   - Update stale inline comments
   - Add clarifying comments for complex logic
   - Remove outdated or incorrect comments
   - Standardize docstring format across codebase

✅ PROJECT DOCUMENTATION:
   - Update architecture documentation
   - Refresh API documentation
   - Fix broken links in markdown files
   - Update README and setup instructions
   - Verify all documentation matches actual code behavior
   - Add missing usage examples
   - Update CHANGELOG with all cleanup changes
```

---

## 🔒 NON-NEGOTIABLE RULES

1.  **NO BREAKING CHANGES:** Never modify public API signatures or existing behavior
2.  **INCREMENTAL ONLY:** Make small, verifiable changes - never rewrite entire modules
3.  **PATTERNS FIRST:** Always follow existing project conventions over "better" approaches
4.  **VERIFY EVERYTHING:** Every change must be validated with existing tests
5.  **NO PLACEHOLDERS:** Do not leave new TODO comments - complete the work
6.  **BACKWARD COMPATIBLE:** All functionality must remain identical
7.  **DOCUMENT ALL CHANGES:** Every cleanup action must be logged
8.  **TEST PASS FIRST:** All existing tests must pass before AND after cleanup

---

## ✅ VALIDATION CHECKLIST

Before completing this task verify ALL items:

- [ ] No unused imports remaining in any file
- [ ] No dead code paths present
- [ ] All deprecation warnings resolved
- [ ] Type hints added to all public functions
- [ ] All docstrings are complete and accurate
- [ ] No commented-out code blocks left
- [ ] All existing tests pass
- [ ] Linter reports zero errors
- [ ] Application starts without warnings
- [ ] Database migrations apply cleanly
- [ ] All documentation links work
- [ ] README is up to date
- [ ] CHANGELOG documents all cleanup changes
- [ ] No new technical debt introduced

---

## ACCEPTANCE CRITERIA

✅ Complete codebase audit performed and documented
✅ All identified cleanup items addressed
✅ All existing tests continue to pass
✅ No breaking changes introduced
✅ All public methods have complete docstrings
✅ Project documentation is current and accurate
✅ Linter reports zero warnings or errors
✅ Cleanup changes are properly documented
✅ Application can be deployed successfully

---

> **FINAL INSTRUCTION:** Execute this entire process systematically. Work through discovery first, then cleanup, then documentation updates. When complete, present a comprehensive summary of all work performed, including items cleaned up, documentation updated, and validation results.