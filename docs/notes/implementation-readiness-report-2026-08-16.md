# Implementation Readiness Assessment Report

**Date:** 2026-08-16
**Project:** SEIM
**Assessed By:** Mario
**Assessment Type:** Phase 3 to Phase 4 Transition Validation (brownfield, BMad Method track)

---

## Executive Summary

SEIM is a mature brownfield product: MVP and most expansion features are already in the Vue SPA + Django API. It is **not** a greenfield waiting on first implementation.

**Overall assessment: Ready with Conditions.**

- **Product / continued development:** proceed. Core student, coordinator, and admin workflows are implemented and tracked in `docs/notes/feature-tracking.md` (last updated 2026-08-13).
- **Production go-live:** do not treat as green. `main` CI is red as of 2026-08-16 (lint, Django CVEs, one backend perf flake, Codecov on the Vue job, Playwright E2E).
- **BMad Method artifact gate:** incomplete. There is no PRD, UX spec, or epics/stories package in `docs/notes/`. Workflow status still lists `document-project` and `prd` as required. Do not start a new BMM increment as if Phase 3 is done.

Do not use November 2025 “production ready / deploy today” notes as current truth.

---

## Project Context

**Track:** `bmad-method` (brownfield)
**Workflow status file:** `docs/notes/bmm-workflow-status.yaml` (generated 2025-12-05; statuses never advanced beyond initial `required`/`optional`)
**Next expected BMM workflow:** `document-project` (still `required`), then `prd`
**This check:** out of sequence for BMM; run anyway because the user asked for a readiness assessment of the live project.

**What SEIM is:** Django 5.1 + DRF + PostgreSQL + Redis + Celery, Vue 3 SPA at `/seim/`, Wagtail CMS for public pages, REST at `/api/`. Canonical app UI is Vue (`docs/notes/SPA_VS_LEGACY.md`, 2026-08).

**Standalone note:** BMM status exists, so this report is tracked. Planning artifacts expected by this workflow are mostly missing; brownfield docs and the live codebase were used instead.

---

## Document Inventory

### Documents Reviewed

| Artifact | Expected (BMM) | Found | Notes |
|----------|----------------|-------|--------|
| PRD | `docs/notes/*prd*.md` | Missing | No product requirements document |
| UX design | `docs/notes/*ux*.md` | Missing | No UX spec; UI audit notes exist |
| Epics / stories | `docs/notes/*epic*.md` | Missing | No epic breakdown |
| Solutioning architecture | BMM architecture.md in output folder | Partial | `docs/architecture.md` + `docs/architectural_decisions.md` (system docs, not a THIS-increment solution design). `docs/notes/role-permission-architecture.md` is a permissions design. |
| Tech spec | Quick Flow only | N/A | Track is BMad Method |
| Test design | Recommended for Method | Missing | No `test-design-system.md` |
| Brownfield docs | `docs/notes/index.md` | Present | `document-project` output exists; status file still says `required` |
| Living product tracker | — | Present | `docs/notes/feature-tracking.md` is the real SSOT for features |
| Test matrix | — | Present | `docs/notes/feature-test-tracking.md` |
| Stale status | — | Present | `docs/notes/PROJECT_PRIORITIES_ASSESSMENT.md`, `docs/notes/status/system-status.md`, `docs/backlog.md`, `docs/roadmap.md`, `docs/user_stories.md` (Nov 2025 / early snapshots) |

### Document Analysis Summary

**Brownfield documentation (`docs/notes/index.md`, 2026-04-08):** Exhaustive project scan: stack, apps, setup, API/data pointers. Still describes Bootstrap 5 authenticated pages in places; Vue is now canonical.

**Architecture (`docs/architecture.md`):** Layered Django design, apps, models, services. Diagram still shows “Django Templates + Bootstrap 5” as the authenticated UI. `application_forms/` is marked deprecated in architecture but is live in the SPA (form builder + Vue consumption). Production compose uses Gunicorn WSGI; WebSockets need a separate ASGI path (`docs/notes/production-target-matrix.md`).

**Feature tracking (2026-08-13):** Large implemented set (auth, applications, documents, notifications, grades, analytics, Vue i18n/a11y baseline, mobility schemes, eligibility schema v7, agreements, calendar ICS, scholarship scoring v1). One **in progress** item: configurable eligibility rule sets. P2 remaining: scholarship award workflow, Google Calendar OAuth, full manual a11y audit. P3 backlog still lists partner portal even though SPA routing includes `/seim/partner`.

**User stories / backlog / roadmap:** Historical MVP stories. Several items tagged Future are already built (notifications, analytics, i18n foundation, program clone, eligibility). Backlog still marks T1 CI/CD and T2 tests as To Do; both exist (`/.github/workflows/ci.yml`, 80% coverage gate). Roadmap Phase 5 still says testing/CI in progress.

**UX:** No formal UX spec. UI audit P0 PDF inline preview historically failed; mitigated 2026-04-15 with download + open-in-new-tab. P1 leftover: tall filter cards, long breadcrumbs, leftover Django templates on disk.

**CI (live, 2026-08-16, `main` @ `729823b`):**
- Docker Compose Test: **success**
- Secret scan: **success**
- Deploy workflow: **success**
- CI: **failure** — Lint (Ruff), Security (pip-audit: 6 Django 5.1.15 CVEs), Backend (1 perf test over 1.0s), Frontend job (Codecov upload)
- E2E Playwright: **failure** — 5 failed / 72 passed / 37 skipped (homepage title, Vue new-application flows)

---

## Alignment Validation Results

### Cross-Reference Analysis

**PRD ↔ Architecture:** No PRD. Architecture supports the implemented product, not a scoped increment. Stale frontend description vs Vue SPA is a contradiction, not a missing component.

**PRD ↔ Stories:** No PRD and no BMM epics. Coverage lives in `feature-tracking.md` + `docs/backlog.md` (stale statuses). Traceability to a requirements baseline is informal.

**Architecture ↔ Stories:** No implementation stories. Code already contains the architectural layers (services, DRF, Celery, Redis, Wagtail, Vue). Gaps vs architecture docs: authenticated UI is Vue not Django templates; `application_forms` is not deprecated in practice; production WebSockets not covered by default prod compose.

**UX ↔ Stories:** No UX spec. SPA routes in `SPA_VS_LEGACY.md` match implemented Vue router surfaces. Accessibility is a baseline plus remaining manual audit (P2).

---

## Gap and Risk Analysis

### Critical Findings

1. **`main` CI is red.** Lint, pip-audit, backend perf assertion, Vue Codecov step, and Playwright E2E failed on the latest push (2026-08-16). Docker Compose Test passed, so the stack still boots and a large pytest slice is healthy locally in that job.
2. **Django 5.1.15 has six pip-audit CVEs.** Official fixes listed for 5.2.15+ / 6.0.6+ (and later patch lines). 5.1 is off the patched train. This is a production security blocker until an upgrade (or accepted risk with documented exceptions).
3. **BMM planning package missing** if a new Method increment is the goal: no PRD, no UX spec, no epics/stories, no test-design, workflow status not updated after `document-project`.

### Sequencing / process

- BMM status file does not reflect work already done (docs, Vue migration, CI).
- `docs/user_stories.md` still lists eligibility, conditional forms, notifications, analytics, i18n as Future.
- Partner portal: SPA route exists; feature tracker still P3. Tracker drift.

### Gold-plating

- Large Vue i18n/a11y/social-meta surface is already built beyond original MVP stories. That is delivered product, not unplanned future work.
- P3 items (e-sign, document intelligence, BI warehouse) are correctly parked.

### Testability

- Method-track test-design artifact: missing (recommendation, not Method blocker).
- Practical testability is strong: pytest 80% gate, Vitest, Playwright, feature↔test matrix. E2E and one timing-sensitive API test are currently failing in CI.

---

## UX and Special Concerns

- Canonical UX is Vue 3 under `/seim/`; Wagtail is public/CMS.
- i18n: en/es foundation implemented; not a full institutional language pack.
- A11y: skip link, main landmark, focus-visible, many control labels; **full manual audit still P2**.
- Responsive: list filter cards still push results below the fold (deferred P1).
- Production UX risk: Gunicorn WSGI default compose does not serve Channels/WebSockets; in-app realtime toasts need an ASGI path in prod.
- Leftover Django `frontend/` templates remain on disk but are not mounted.

---

## Detailed Findings

### Critical Issues

_Must be resolved before production go-live; not blockers for local feature work_

- Restore `main` CI to green: Ruff (I001/B905/UP041 on a small file set), pip-audit Django CVEs, `test_application_search_performance` 1.03s vs 1.0s cap, Vue Codecov upload failure, Playwright homepage + new-application flows.
- Plan Django 5.1 → 5.2 LTS (or 6.x) so security patches exist.
- Do not ship from the November 2025 “deploy today” assessment.

### High Priority Concerns

_Should be addressed to reduce implementation and ops risk_

- Refresh or archive stale SSOT docs (`architecture.md` frontend diagram, `user_stories.md`, `backlog.md`, `roadmap.md`, `PROJECT_PRIORITIES_ASSESSMENT.md`, `system-status.md`).
- Finish or explicitly pause **configurable eligibility rule sets** (only in-progress P1/P2 item).
- Align `feature-tracking.md` with SPA partner portal / nominations (implemented vs P3).
- Production: ASGI/WebSocket path, `.env.prod` secrets, SSL, backups/restore drill (`production-target-matrix.md`).
- If following BMM for the next increment: run `prd` + `create-epics-and-stories` (and UX if the increment is UI-heavy) before treating Phase 4 as gated.

### Medium Priority Observations

- UI P1: filter density, breadcrumb truncation.
- Document PDF inline preview historically unreliable; recovery actions exist.
- Grades remain API-only (no SPA console) — by design in `SPA_VS_LEGACY.md`.
- Notification `action_url` still stored as root paths; SPA maps them.
- BMM `document-project` status never flipped to the index path despite `docs/notes/index.md`.
- Test-design workflow not run (Method: recommended).

### Low Priority Notes

- Sprint-artifacts folder is empty (`docs/notes/sprint-artifacts`).
- Brainstorming session 2025-12-05 stopped after setup (reliability theme; no completed ideas file).
- White-labeling / LICENSE work is recent (`main` commits) and out of scope for this gate except as evidence the repo is being prepared for reuse.

---

## Positive Findings

### Well-Executed Areas

- Feature tracker is detailed, dated, and maps code + tests. This is the best requirements stand-in.
- Vue SPA is canonical; leftover Django app URLs redirect into `/seim/`.
- CI/CD exists (lint, security, backend, Vue, Docker compose test, secret scan, deploy, Playwright) — far ahead of the stale backlog T1 “To Do”.
- Coverage gate is 80%; latest backend CI run: **1585 passed**, 1 failed, 6 skipped.
- Playwright: **72 passed** on the same push; failures cluster on homepage title and new-application UX, not a total E2E blackout.
- Docker Compose Test job succeeded on `main`.
- Manual QA log has **no open MQ items**.
- Production sizing, backups, and cloud BOM are documented (`production-target-matrix.md`).
- Security posture in app code: JWT, RBAC, rate limits, ClamAV path, production settings module.

---

## Recommendations

### Immediate Actions Required

1. Fix `main` CI (Ruff, Codecov Vue job, perf test threshold or query, Playwright homepage/new-app).
2. Decide Django upgrade path off 5.1.15 (pip-audit will stay red until then).
3. Treat `feature-tracking.md` as living PRD until a BMM PRD exists; stop citing Nov 2025 status docs.

### Suggested Improvements

- Mark `document-project` complete in `bmm-workflow-status.yaml` (output: `docs/notes/index.md`).
- Write a short increment PRD only if starting a new BMM cycle (eligibility rulesets, scholarship awards, or calendar OAuth).
- Reconcile partner portal / nominations in the feature tracker.
- Run test-design if the next increment is high-risk (eligibility engine, awards).

### Sequencing Adjustments

- Do not run greenfield “starter template” stories; the repo is live.
- Production WebSockets are a deploy-architecture story, not a Vue feature story.
- Eligibility rulesets should complete (or be scoped down) before scholarship award workflow, because submit/eligibility already gates applications.

---

## Readiness Decision

### Overall Assessment: Ready with Conditions

**Rationale:** The product is implemented and documented enough to keep building. BMM Phase 3 artifacts are incomplete, and `main` is not production-green. Those are conditions, not a reason to freeze feature work.

This is **not** “Ready” for an unconditioned production cutover.

### Conditions for Proceeding

1. Treat remaining work as brownfield feature increments against `feature-tracking.md`, not as first-time MVP build.
2. Do not declare production-ready until CI is green and Django CVE handling is explicit.
3. If using BMad Method for a new increment: produce PRD + epics (UX if UI-heavy) before calling the Method gate complete.
4. Use `SPA_VS_LEGACY.md` and `docs/architecture.md` together; prefer SPA_VS_LEGACY for what users actually hit.

---

## Next Steps

1. Review this report.
2. Restore CI on `main` (highest leverage).
3. Optionally run `prd` / `create-epics-and-stories` for the next increment (eligibility rulesets or production hardening).
4. Sprint-planning is optional; the living backlog is already `feature-tracking.md`. `workflow-init` is only needed if you want BMM status to match reality.

### Workflow Status Update

`docs/notes/bmm-workflow-status.yaml` → `implementation-readiness` set to this report path. Other workflows left unchanged (still show initial `required` flags).

---

## Appendices

### A. Validation Criteria Applied

Implementation Readiness checklist: document completeness, PRD/architecture/story alignment, sequencing, greenfield setup (N/A), critical gaps, UX, overall ready-to-proceed. Adapted for brownfield: live CI, feature tracker, and SPA split used where BMM files were absent.

### B. Traceability Matrix

| Area | Requirements source | Implementation | Tests |
|------|---------------------|----------------|-------|
| Auth / roles | user stories + tracker | `accounts`, Vue login | `auth-api`, `roles` matrix |
| Applications | user stories + tracker | `exchange`, Vue | `programs-applications` |
| Documents | user stories + tracker | `documents` | `documents-core` |
| Notifications | tracker (stories still say Future) | `notifications` + WS | `notifications` |
| Analytics | tracker (stories still say Future) | `analytics` | `analytics` |
| CMS | brownfield docs | `cms` | `cms-public` |
| Eligibility v7 / mobility | tracker 2026-08-13 | `exchange` | `eligibility-rules`, `mobility-host` (browser Partial) |
| Eligibility rulesets (DB) | tracker In Progress | partial API/admin | not a closed cluster |
| Partner portal | SPA_VS_LEGACY vs tracker P3 | Vue `/partner` | tracker not updated |

### C. Risk Mitigation Strategies

| Risk | Mitigation |
|------|------------|
| CI red hides regressions | Fix lint/CVE/perf/E2E before merging more features to `main` |
| Django 5.1 unpatched | Upgrade to 5.2 LTS; re-run test suite; watch Wagtail compatibility |
| Stale “production ready” docs | Point operators at this report + feature tracker + SPA_VS_LEGACY |
| Prod WebSockets silent | Document ASGI deploy or disable realtime in prod UI until then |
| BMM status drift | Update status after each workflow, or ignore BMM until `workflow-init` is re-run |

---

_This readiness assessment was generated using the BMad Method Implementation Readiness workflow (v6-alpha)_
