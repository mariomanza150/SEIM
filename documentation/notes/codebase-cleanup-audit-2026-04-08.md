# SEIM Codebase Cleanup Audit

**Date:** 2026-04-08  
**Scope:** Repository-wide discovery pass with an initial cleanup wave focused on non-breaking documentation and command drift.

## Discovery Summary

### Critical

| Area | Finding | Evidence |
|---|---|---|
| CI / Docker | GitHub Docker Compose workflow appears to use DB credentials that do not match `docker-compose.yml`. | `.github/workflows/docker-compose-test.yml`, `docker-compose.yml` |

### High

| Area | Finding | Evidence |
|---|---|---|
| Docs / Commands | Default local access port is documented as `8000`, but the default Docker Compose mapping exposes the app on `8001`. | `README.md`, `docs/index.md`, `Makefile`, `docker-compose.yml`, `frontend-vue/vite.config.js` |
| Frontend Routing | Vue SPA uses `/seim/applications/new`, while multiple docs and legacy references still use `/seim/applications/create/`. | `frontend-vue/src/router/index.js`, `docs/url-structure.md`, `templates/frontend/dashboard.html` |
| Frontend Docs | `frontend-vue/README.md` does not match the current scripts, routes, or implemented feature set. | `frontend-vue/README.md`, `frontend-vue/package.json` |
| E2E Docs | Playwright quick-start references a missing Make target. | `tests/e2e_playwright/README.md`, `Makefile` |
| Backend Routing | Project URLconf duplicates JWT routes already defined in `api.urls`, which can mislead maintenance and docs. | `seim/urls.py`, `api/urls.py` |

### Medium

| Area | Finding | Evidence |
|---|---|---|
| Documentation Accuracy | `docs/index.md` duplicates sections and has stale metadata. | `docs/index.md` |
| Frontend Inventory | `docs/FRONTEND_FILE_INDEX.md` still marks frontend tests as TODO even though Vue/Vitest and Playwright tests exist. | `docs/FRONTEND_FILE_INDEX.md`, `frontend-vue/src/**/*.spec.js`, `tests/e2e_playwright/test_vue_ui.py` |
| Project Assessment | `docs/PROJECT_PRIORITIES_ASSESSMENT.md` points to a TODO in `seim/urls.py` that now lives in `seim/urls_OLD_BACKUP.py`. | `docs/PROJECT_PRIORITIES_ASSESSMENT.md`, `seim/urls_OLD_BACKUP.py` |
| Agent Guidance | `CLAUDE.md` lists Django `5.2.3`, while `requirements.txt` pins `5.1.4`. | `CLAUDE.md`, `requirements.txt` |
| Repo Hygiene | Generated artifacts and caches are present in the working tree. | `frontend-vue/dist/`, `__pycache__/`, Playwright screenshots/videos |

### Low

| Area | Finding | Evidence |
|---|---|---|
| Logging | A few backend modules still use `print()` instead of structured logging. | `notifications/tasks.py`, `accounts/signals.py`, `exchange/forms.py` |
| Legacy Files | Backup or duplicate files remain in the tree and create audit noise. | `seim/urls_OLD_BACKUP.py`, `docker-compose copy.yml` |
| Tooling Drift | ESLint / Prettier are installed for Vue but are not fully wired into scripts/config. | `frontend-vue/package.json` |

## Ordered Execution Plan

1. Documentation and command truthfulness
   Fix port, URL, route, and Make target drift in docs and developer-facing commands.

2. Frontend route consistency
   Decide and document one canonical SPA create-application path, then align templates, tests, and helper utilities.

3. Backend routing and configuration cleanup
   Remove or document shadowed JWT routes and reconcile settings-module drift across entrypoints.

4. Repo hygiene
   Remove generated artifacts from version control paths, tighten ignore coverage, and delete obsolete backup files only after confirming they are unused.

5. Quality follow-up
   Replace remaining `print()` calls with logging, review partial tooling setup, and address low-risk cleanup items module by module.

## Initial Cleanup Wave

The first cleanup wave in this session targets only **non-breaking documentation and command fixes** from step 1 above:

- Correct documented local port usage to match `docker-compose.yml`
- Fix Playwright Make target references
- Refresh frontend documentation to match current Vue scripts and routes
- Correct stale route and assessment references in docs

## Completed In This Session

- Added this audit document and ordered execution plan
- Corrected local access URLs in `README.md` and `docs/index.md`
- Fixed the stale Playwright quick-start target in `tests/e2e_playwright/README.md`
- Updated Playwright `Makefile` targets to use the externally exposed local port
- Refreshed `frontend-vue/README.md` to match the current scripts, routes, and implemented features
- Updated `docs/url-structure.md` to use the current Vue application-creation route and note the legacy server-rendered route
- Corrected stale references in `docs/FRONTEND_FILE_INDEX.md`, `docs/PROJECT_PRIORITIES_ASSESSMENT.md`, and `CLAUDE.md`
- Marked `docs/PROJECT_PRIORITIES_ASSESSMENT.md` as the canonical November 2025 status summary and `docs/VUE_TEST_RESULTS.md` as the canonical Vue test summary
- Deleted superseded Markdown clutter: `docs/WHAT_NEXT.md`, `docs/VUE_MANUAL_TEST_RESULTS.md`, `docs/FINAL_SUMMARY.txt`
- Deleted superseded Vue planning notes: `docs/VUE_MIGRATION_EXECUTION_PLAN.md`, `docs/VUE_DAY2_TEST_GUIDE.md`, `docs/VUE_DAY3_TESTING.md`, `docs/VUE_WEEK1_TASKS.md`
- Deleted redundant generated guide duplicates after switching references to the maintained manuals: `docs/development-guide.md`, `docs/architecture.md`
- Deleted exact duplicate root status files already present under `docs/status/`: `E2E_EXPANSION_PROGRESS.md`, `VIDEO_DEMOS_READY.md`, `TEST_COVERAGE_IMPROVEMENTS.md`
- Deleted obvious scratch / duplicate artifacts: `query`, `docker-compose copy.yml`
- Removed generated local artifacts and caches: Playwright screenshots/videos, Vue `dist`, `frontend-vue/node_modules/.vite`, and app `__pycache__` directories
- Updated `.gitignore` to ignore Playwright screenshots, videos, and reports going forward
- Deleted the stale generated workflow summary `docs/NEXT_STEPS.md` after confirming no live references remained
- Consolidated overlapping CMS docs by keeping `docs/CMS_QUICK_START.md` as the short operational guide, trimming stale static counts, and deleting `docs/CMS_INDEX.md` plus `docs/CMS_CURRENT_STATE.md`
- Pruned historical proposal / review bundles that were only archival noise: `docs/CODE_REVIEW_CLEANUP_2025-12-05.md`, `docs/CODE_REVIEW_FIXES_APPLIED.md`, `docs/sprint-change-proposal-2025-12-05.md`, `docs/sprint-change-proposal-2025-12-05-IMPLEMENTATION.md`, `docs/QUICK_START_CLEANUP.md`, `docs/VUE_MIGRATION_REVIEW.md`
- Verified the cleanup by searching the repository for remaining references to the removed document names and finding none
- Reconciled SPA application-creation routing by keeping `/seim/applications/new` as the canonical Vue route, adding a compatibility redirect for `/seim/applications/create`, and updating stale SPA-oriented helpers, tests, and docs
- Removed shadowed JWT route declarations from `seim/urls.py` so `/api/token/` and `/api/token/refresh/` are owned only by `api/urls.py`
- Fixed the CI Docker Compose workflow to use the same PostgreSQL credentials and readiness check as `docker-compose.yml`
