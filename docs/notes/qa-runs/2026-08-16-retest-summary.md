> **Snapshot at test time** � ports/URLs reflect the environment when this QA run was recorded.

# Manual QA retest rollup — 2026-08-16

**Date:** 2026-08-16  
**App:** `http://localhost:8020`  
**Stack:** Compose project `seim-localprod` (`docker-compose.local-prod.yml`), image rebuilt `--no-cache` from host source (`Dockerfile.prod` → `web` on host 8020).  
**Did:** rebuild, `up -d`, migrate (entry), `create_initial_data`, `seed_demo_readiness`, `restore_cms`, product fixes, isolated-browser retest.  
**Did not:** commit, force-push, or edit `manual-qa-full-checklist.md` / `feature-test-tracking.md`.

Morning role reports (env-blocked): [`2026-08-16-summary.md`](2026-08-16-summary.md). This file is the **retest** after those blockers were cleared.

**Retest role reports:**

- [Public](2026-08-16-retest-public.md)
- [Student](2026-08-16-retest-student.md)
- [Coordinator](2026-08-16-retest-coordinator.md)
- [Admin](2026-08-16-retest-admin.md)
- [Partner](2026-08-16-retest-partner.md)

## What was rebuilt / seeded

- Images: `seim-localprod-web`, `seim-localprod-celery`, `seim-localprod-celery-beat` from current host (Vue baked in `Dockerfile.prod`).
- Container `/app/exchange/urls.py` is the real SimpleRouter (81 lines).
- Migrations applied on this DB including `exchange.0020` … `0029` (adds `required_gpa`).
- Demo users verified: admin / coordinator / student / partner (`partner@test.com` created).
- CMS: UAdeC home + `/programas/` (Salamanca detail live).

## Code changed (product)

- SPA admin/partner gates: `User.is_admin` no longer treats Django `is_staff` as SEIM admin; Vue `isAdmin` ignores coordinator/partner/student even if API `is_admin` is stale; `canUsePartnerPortal` is partner-only.
- Seed: lookup by email or username; always set `is_email_verified=True`. `create_vue_test_users` also verifies emails.
- Tests: accounts model, seed_demo_readiness, Vitest auth/router (`40 passed` on those files).

## API smoke (host)

| Check | Result |
|-------|--------|
| `GET /health/` | 200 healthy |
| `GET /api/programs/` anonymous | 401 JSON (not Wagtail 404) |
| `GET /api/schema/` | programs + applications + calendar present |
| `POST /api/login/` all four demo users | 200 access token (after throttle window) |
| `/` and `/programas/` | CMS HTML |
| `/seim/login` | Vue `#app` + 2.0.0-vue |
| Django admin agreements | 200 |

## Per-role counts (retest)

Do not sum across roles (items overlap).

| Role | Pass | Fail | Blocked | Other |
|------|-----:|-----:|--------:|-------|
| Public | 12 | 0 | 0 | |
| Student | 22 | 0 | 3 | Not executed: 3 (draft save / upload / submit-gate) |
| Coordinator | 10 | 0 | 0 | Not executed: status/comment/validate mutations |
| Admin | 11 | 0 | 0 | 7.3–7.5 not re-clicked |
| Partner | 4 | 0 | 0 | Thread/docs click-through not fully walked |

**Approximate session totals (unique checklist ids exercised):** **Pass ~55**, **Fail 0**, **Blocked 3**, remainder not executed (destructive or fixture).

## Section 8 (thin)

Student can log in; exchange APIs work; seeded applications list and detail load; coordinator review queue opens a DAAD application with comments chrome. **Did not** create a new draft, upload files, submit, or approve (shared demo DB). That is a thin lifecycle observation, not 8.1–8.7 mutation.

## Morning Fails — retest

| ID | Morning | Retest |
|----|---------|--------|
| **MQ-2026-08-16-001** | Coordinator stayed on `/seim/admin/programs` | **Pass** — redirect to `/seim/applications` |
| **MQ-2026-08-16-002** | Coordinator stayed on `/seim/partner` | **Pass** — redirect to `/seim/applications` |
| **MQ-2026-08-16-003** | Agreements changelist 500 (`required_gpa`) | **Pass** — 200 after migrate 0020 |

Env blockers (stub urls, Wagtail welcome, unverified student, missing partner) **cleared**. Closed in [`manual-qa-issues.md`](../manual-qa-issues.md).

## Remaining open defects

**None filed from this retest.** Open MQ list is empty for 2026-08-16 items.

Gaps (not Fail): no closed-window program fixture (2.8); no resubmit fixture (3.4); full §8 submit/approve not run; eligibility-rulesets still IN PROGRESS (load/read only).
