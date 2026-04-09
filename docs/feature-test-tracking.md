# SEIM feature ↔ test coverage matrix

_Companion to [`docs/feature-tracking.md`](feature-tracking.md). Use this file as the source of truth for **unit**, **smoke**, and **browser** coverage per feature or workflow cluster. Update rows when you add tests or re-verify._

## Status legend

| Symbol | Meaning |
|--------|---------|
| `—` | Not started / unknown |
| `Partial` | Some paths covered; list gaps in Notes |
| `Done` | Current suite green; paths recorded |

**Layers**

- **Unit**: Django `pytest` under `tests/unit/` and `tests/integration/api/` where appropriate; Vue `npm --prefix frontend-vue run test:run` (Vitest) for SPA logic and components.
- **Smoke**: Playwright tests marked `smoke` (`make e2e-smoke` with app reachable at `BASE_URL`).
- **Browser**: Playwright workflow or UI journeys (`tests/e2e_playwright/`), including `-m vue` / `make vue-e2e` when the SPA is under test.

## How to run (reference)

- Backend unit + integration (Docker): `make test-unit` and `make test-integration` (or `make test` / `./scripts/run_tests.sh` per project docs).
- Frontend unit: `npm --prefix frontend-vue run test:run`
- Playwright smoke: `make e2e-smoke` (expects `http://localhost:8001` unless overridden).
- Vue browser E2E: `make vue-e2e` (seeds + `BASE_URL`/`API_URL` per Makefile).

Adjust hosts and compose profiles to match your environment (`docker-compose.yml`, `CLAUDE.md`).

---

## Matrix (feature / workflow clusters)

_Map each row to one or more rows in `docs/feature-tracking.md` § **IMPLEMENTED** (or **IN PROGRESS**). Prefer updating an existing row over adding duplicates._

| Cluster ID | Feature / workflow (tracker reference) | Unit | Smoke | Browser | Last verified | Notes |
|------------|----------------------------------------|------|-------|---------|---------------|-------|
| `auth-api` | User authentication and account management | Done | Partial | Partial | 2026-04-08 | **Unit:** `tests/integration/api/test_auth_api.py` (26 tests, `docker compose exec web … pytest -o addopts='--strict-markers --tb=short'` + `DJANGO_SETTINGS_MODULE=seim.settings.test`); `tests/unit/api/test_api_views.py` (`test_token_obtain_pair`, `test_token_refresh`); Vue `frontend-vue/src/stores/auth.spec.js` (`npm run test:run -- --run src/stores/auth.spec.js`). **Smoke/Browser:** Playwright `-m smoke` not re-run here: `Dockerfile.test` image lacks Chromium system libs after `playwright install`; use **host** `make e2e-smoke` with app at `BASE_URL` (see Makefile). Smoke markers include `test_smoke.py`, `test_auth_workflows.py::TestAuthenticationSmoke::test_login_logout_smoke` (needs Vue users + `BASE_URL` e.g. 5173). **Browser:** `test_auth_workflows.py` (registration/login/logout; `-m auth`). |
| `roles` | Role management (student / coordinator / admin) | — | — | — | | Permissions across API + UI |
| `programs-applications` | Exchange programs and application workflow | — | — | — | | Catalog, state transitions, timeline |
| `documents-core` | Document management + checklist + preview | — | — | — | | Upload, validate, resubmit, preview API |
| `dynamic-forms` | Dynamic form builder + Vue consumption + steps / branching | — | — | — | | `application_forms`, `df_*`, visibility |
| `notifications` | Notifications center, real-time, digests, routing reference | Partial | — | — | 2026-04-09 | Routing ref: `tests/unit/notifications/test_routing_reference.py`, `test_notifications_tasks.py`, `tests/integration/api/test_notification_routing_reference_api.py`; Vue `NotificationRouting.spec.js`, `Settings.spec.js` (staff link). WebSocket / inbox E2E still open. |
| `grades` | Grade translation | — | — | — | | |
| `analytics` | Analytics dashboard + exports (CSV/XLSX/PDF) | — | — | — | | |
| `vue-portal` | Vue student/coordinator portal (shell, routing, a11y) | — | — | — | | Dashboard, nav, i18n baseline |
| `cms-public` | Wagtail CMS public site | — | — | — | | Often manual or separate checks |
| `coord-review` | Coordinator review queue + workload + saved searches | — | — | — | | |
| `agreements` | Exchange agreements + documents + renewal + expiration reminders | — | — | — | | |
| `calendar-ics` | Calendar events + deadlines + ICS subscribe | — | — | — | | |
| `data-management` | Staff data management + bulk student import | — | — | — | | |
| `settings-ui` | User settings (appearance, notifications, i18n) | — | — | — | | |
| `readiness-compare` | Application readiness, program filters, compare | — | — | — | | |

_Add rows for any **IN PROGRESS** or high-risk **IMPLEMENTED** feature from the tracker that is not represented above._

---

## Workflow → suggested Playwright entrypoints

_Use these as hints when filling the **Browser** column; replace with exact `test_file.py::test_name` once stable._

| Journey | Typical markers / files |
|---------|-------------------------|
| Critical path sanity | `tests/e2e_playwright/test_smoke.py`, `-m smoke` |
| Auth | `test_auth_workflows.py`, `test_auth_simple.py`, `-m auth` |
| Student | `test_student_workflows.py`, `-m student` |
| Coordinator | `test_coordinator_workflows.py`, `-m coordinator` |
| Admin | `test_admin_workflows.py`, `-m admin` |
| Vue SPA | `test_vue_ui.py`, `-m vue` |
| Accessibility | `-m accessibility` |

---

*Last updated: 2026-04-08 — `auth-api` unit verified (Docker + Vitest); JWT integration tests aligned with `api:` URLs and email-based token view; Playwright smoke/browser Partial (host / browser system libs). Notifications row unchanged from prior routing-ref note.*
