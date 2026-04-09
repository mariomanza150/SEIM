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
| `programs-applications` | Exchange programs and application workflow | Done | Partial | Partial | 2026-04-09 | **Unit (green):** `tests/integration/api/test_applications_api.py`, `test_programs_api.py`; `tests/unit/exchange/test_application_submission.py`, `test_application_readiness.py`, `test_timeline_events_api.py` (`docker compose exec web … pytest -o addopts='--strict-markers --tb=short'` + `DJANGO_SETTINGS_MODULE=seim.settings.test`). Vue: `Applications.spec.js`, `ApplicationDetail.spec.js`, `applicationReadiness.spec.js`. **Smoke/Browser:** same host Playwright constraint as `auth-api`; journeys `test_student_workflows.py` (`-m student` `-m workflow`), coordinator/admin flows touch applications. |
| `documents-core` | Document management + checklist + preview | Done | Partial | Partial | 2026-04-09 | **Unit (green):** `tests/integration/api/test_document_preview_api.py`, `test_documents_list_filters.py`; `tests/unit/exchange/test_document_checklist_api.py`; `tests/unit/documents/` (125 passed, 1 skipped — `docker compose exec web … pytest -o addopts='--strict-markers --tb=short'` + `DJANGO_SETTINGS_MODULE=seim.settings.test`). Vue: `Documents.spec.js`, `DocumentDetail.spec.js`, `DocumentUpload.spec.js`. **Smoke:** `test_document_workflows.py` (`TestDocumentWorkflowsSmoke::test_documents_page_smoke`, `-m smoke`); host Playwright / image browser libs same as `auth-api`. **Browser:** `test_document_workflows.py` (`-m document` where used). Agreement-doc REST: `tests/integration/api/test_agreement_documents_api.py` (run with `agreements` slice). |
| `dynamic-forms` | Dynamic form builder + Vue consumption + steps / branching | Done | Partial | Partial | 2026-04-09 | **Unit (green):** `tests/unit/application_forms/`; `tests/unit/exchange/test_application_dynamic_form_api.py`; `test_exchange_services_additional.py::TestDynamicFormProcessing`, `::TestProcessDynamicFormStepVisibleWhen`; `tests/integration/test_dynamic_forms_comprehensive.py` (152 tests, Docker + `DJANGO_SETTINGS_MODULE=seim.settings.test`). Vue: `ApplicationForm.spec.js`, `dynamicFormVisibility.spec.js`. `FormType.created_by` now `blank=True` + migration `0005_alter_formtype_created_by_blank` (aligns `full_clean()` with optional creator). **Smoke/Browser:** host Playwright; `test_vue_ui.py` (`-m vue`), student/coordinator flows may cover wizard. |
| `notifications` | Notifications center, real-time, digests, routing reference | Partial | — | — | 2026-04-09 | Routing ref (schema v6, `reference_api_access`, `primary_recipients` per category): `test_routing_reference.py`, `test_notification_routing_reference_api.py`, `test_notifications_tasks.py`; Vue `NotificationRouting.spec.js`, `Settings.spec.js`. WebSocket / inbox E2E still open. |
| `grades` | Grade translation | Done | — | — | 2026-04-09 | **Unit (green):** `tests/unit/grades/test_grades_services.py`, `tests/integration/api/test_grades_api.py` (56 tests, Docker + `DJANGO_SETTINGS_MODULE=seim.settings.test`). No dedicated Vue grades specs. **Smoke/Browser:** not mapped; API used from profile/program flows if exercised by E2E. |
| `analytics` | Analytics dashboard + exports (CSV/XLSX/PDF) | — | — | — | | |
| `vue-portal` | Vue student/coordinator portal (shell, routing, a11y) | — | — | — | | Dashboard, nav, i18n baseline |
| `cms-public` | Wagtail CMS public site | — | — | — | | Often manual or separate checks |
| `coord-review` | Coordinator review queue + workload + saved searches | Done | Partial | Partial | 2026-04-09 | **Unit (green):** `tests/unit/exchange/test_filters.py` (program + application + review-queue filters), `tests/integration/api/test_coordinator_workload_api.py`, `tests/unit/exchange/test_saved_searches.py` (34 tests, Docker + `DJANGO_SETTINGS_MODULE=seim.settings.test`, `pytest -o addopts='--strict-markers --tb=short'`). Shared fixtures: `tests/conftest.py` adds `user_student` / `user_coordinator` aliases → `student_user` / `coordinator_user`. Vue: `reviewQueuePresets.spec.js`, `CoordinatorReviewQueue.spec.js`, `CoordinatorWorkload.spec.js`, `useStaffSavedPresets.spec.js`, `staffListSearchPresets.spec.js` (11 tests). **Smoke/Browser:** host Playwright; `test_coordinator_workflows.py` (`-m coordinator` `-m workflow`). |
| `agreements` | Exchange agreements + documents + renewal + expiration reminders | Done | Partial | Partial | 2026-04-09 | **Unit (green):** `tests/integration/api/test_exchange_agreements_api.py`, `test_agreement_documents_api.py`; `tests/unit/exchange/test_exchange_agreement.py`, `test_agreement_renewal.py`, `test_agreement_expiration_reminders.py`; `tests/unit/documents/test_exchange_agreement_document.py` (20 tests, Docker + `DJANGO_SETTINGS_MODULE=seim.settings.test`). Vue: `StaffExchangeAgreements.spec.js`, `StaffAgreementDocuments.spec.js`. **Smoke/Browser:** host Playwright; staff agreement/document lists overlap `staffListSearchPresets` / coordinator flows. |
| `calendar-ics` | Calendar events + deadlines + ICS subscribe | Done | Partial | Partial | 2026-04-09 | **Unit (green):** `tests/unit/exchange/test_calendar_api.py` (21 tests: events list filters, subscribe token, `.ics` — Docker + `DJANGO_SETTINGS_MODULE=seim.settings.test`). Vue: `DeadlinesCalendar.spec.js`. Calendar saved-filter (de)serialization: `staffListSearchPresets.spec.js` (see `coord-review`). **Smoke/Browser:** host Playwright; Dashboard **Deadlines** / SPA `/calendar` via `test_vue_ui.py` or manual. |
| `data-management` | Staff data management + bulk student import | — | — | — | | |
| `settings-ui` | User settings (appearance, notifications, i18n) | Partial | — | — | 2026-04-09 | Vitest `frontend-vue/src/views/Settings.spec.js` (load/save, UI language, staff link to notification routing). Playwright not recorded. |
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

*Last updated: 2026-04-09 — `grades` unit verified (56 pytest). Prior: `calendar-ics` slice.*
