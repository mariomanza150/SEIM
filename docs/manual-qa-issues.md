# Manual QA issue log

_Logged during [manual feature & workflow test loop](prompts/manual-feature-workflow-test-loop-prompt.md) sessions. Scope and feature state: [`feature-tracking.md`](feature-tracking.md). Cluster coverage matrix: [`feature-test-tracking.md`](feature-test-tracking.md)._

## How to use

- Assign **MQ-** IDs sequentially per session (or per defect).
- Reference an ID from **Notes** in `feature-test-tracking.md` and from PRs/commits.
- Close items by moving them to **Resolved** with date and verification note.

---

## Open

| ID | Date found | Summary | Cluster / area |
|----|------------|---------|----------------|
| _None_ |  |  |  |

---

## Resolved

| ID | Date resolved | Verification |
|----|---------------|----------------|
| **MQ-2026-04-09-014** | 2026-04-09 | **Staff-only SPA routes on cold load:** **`frontend-vue/src/router/authNavigation.js`:** `resolveAuthenticatedNavigation(to, authStore)` centralizes auth restore + `meta.staffReviewQueue` / `canUseStaffReviewQueue`. **`frontend-vue/src/router/index.js`:** `beforeEach` calls it for every `requiresAuth` route (fixes skip after `checkAuth()`). Vitest: `frontend-vue/src/router/authNavigation.spec.js` + full suite **164 passed** (`npm run test:run`). **Live verify (2026-04-09):** `npm run build` → `docker compose cp .\frontend-vue\dist\. web:/app/frontend-vue/dist/` → `docker compose restart web` → browser MCP `http://localhost:8001`, `student@test.com` cold **`/seim/notification-routing`** → **`/seim/applications`** (**Pass**). **Ops:** host-only build without copying into `web` left stale JS (redirect did not run until dist sync). |
| MQ-2026-04-09-001 | 2026-04-09 | Dockerfile copies baked `dist` to `/opt/seim-vue-dist`; `scripts/ensure_vue_dist.sh` runs before `collectstatic` in `docker-compose.yml` / `docker-compose.e2e.yml` and seeds `/app/frontend-vue/dist` when `index.html` is missing (bind mount + empty named volume). Rebuild web image: `docker compose build web`, then `docker compose up -d web`. |
| MQ-2026-04-09-002 | 2026-04-09 | `core/views.py` renders `core/contact_message.html` (extends site `base.html`) when no active custom/feedback form exists or on contact errors/thanks — no longer plain-text `HttpResponse`. |
| MQ-2026-04-09-003 | 2026-04-09 | `SPECTACULAR_SETTINGS["SERVERS"]` in `seim/settings/base.py`: default server URL is relative `/` so Try it out matches the docs origin; `:8001` and `:8000` listed as alternates. |
| CMS footer year | 2026-04-09 | `cms/templates/cms/base.html` uses `{% now "Y" %}` for the copyright year. |
| MQ-2026-04-09-004 | 2026-04-09 | `GET /data-management/` serves `DataManagementIndexView` (hub template with links filtered by `has_data_permission` … `VIEW`); login required. |
| MQ-2026-04-09-005 | 2026-04-09 | `seim/urls.py`: register `admin-dashboard/` **before** Wagtail’s `""` include so `GET /admin-dashboard/` hits `frontend.admin_dashboard_view`. |
| MQ-2026-04-09-006 | 2026-04-09 | `auth.js` normalizes DRF error bodies for login messages; `Login.vue` adds `aria-invalid`, `aria-describedby`, `id="login-form-error"`, `aria-live="assertive"` on the error alert. |
| MQ-2026-04-09-007 | 2026-04-09 | `LoginView.authentication_classes = []` so a prior Django session does not trigger `SessionAuthentication` CSRF on JSON login; regression: `test_login_switch_user_with_existing_django_session` in `tests/integration/api/test_auth_api.py`. |
| **MQ-2026-04-09-008** | 2026-04-09 | `LogoutView.authentication_classes = [JWTAuthentication]` (no Session CSRF on JSON POST). **`frontend-vue/src/stores/auth.js`:** call `POST /api/accounts/logout/` with `Authorization: Bearer <access>` **before** clearing tokens (JWT-only view needs header; prior order caused **401**). Regression: `test_logout_post_json_succeeds_with_django_session_and_jwt_header` in `tests/integration/api/test_auth_api.py`; Vitest `auth.spec.js` (logout `axios.post` third-arg headers). Rebuild/serve updated `frontend-vue/dist` for manual verify. |
| **MQ-2026-04-09-009** | 2026-04-09 | Applications list uses API `program_name` (`programDisplayName` in `Applications.vue`). Deploy: rebuild `frontend-vue/dist` + `collectstatic` (or `docker compose cp` dist into `web` + restart). Integration: `test_list_applications_includes_program_name`; Vitest `Applications.spec.js`. |
| **MQ-2026-04-09-010** | 2026-04-09 | **`exchange/serializers.py`:** `ApplicationSerializer.validate` skips `check_eligibility` for **draft** create/update; eligibility enforced on `submit_application`. **`ApplicationForm.vue`:** debounced `GET /api/programs/:id/check_eligibility/` on program change (new app); assertive program alert merges preview + flattened `program` / `non_field_errors`; select `aria-describedby` / `aria-invalid`. Tests: `test_draft_create_skips_eligibility_check` (`test_exchange_serializers.py`), `test_create_draft_application_when_student_not_eligible` (`test_applications_api.py`), Vitest eligibility alert in `ApplicationForm.spec.js`. |
| **MQ-2026-04-09-011** | 2026-04-09 | **`DocumentSerializer.to_representation`:** nested `type` (`id`, `name`, `description`) and `application` (`id`, `program_name`) for list/detail JSON. **Vue:** `documentApi.js` helpers; `Documents.vue`, `DocumentDetail.vue` (breadcrumb uses type name or filename, not stale “Loading…”); `ApplicationDetail.vue` document list uses type label. Integration: `test_documents_list_filters.py`; Vitest: `documentApi.spec.js`. Rebuild `frontend-vue/dist` for static deploys. |
| **MQ-2026-04-09-012** | 2026-04-09 | **`documentApi.js`:** `coerceDocumentNested` parses JSON strings for `application` / `type` before labels and router ids. **`Documents.vue`:** filter options use `program_name || program?.name`. **`core/cache.py`:** `json.dumps(..., default=str)` when compressing large API cache payloads. Vitest: `documentApi.spec.js`. Rebuild `frontend-vue/dist` for manual verify. |
| **MQ-2026-04-09-013** | 2026-04-09 | SSR **`frontend:analytics`** moved from **`/analytics/`** to **`/dashboard/analytics/`** (`frontend/urls.py`, before `dashboard/`) so `seim/urls.py` `path("analytics/", include analytics.urls))` no longer serves DRF API root for that URL. **`templates/frontend/dashboard.html`** quick-action URLs; **`tests/unit/frontend/test_frontend_views.py`**; **`tests/e2e_playwright/utils/navigation.py`**. Pytest `-k analytics` (9 tests). |

---

*Last updated: 2026-04-09 — rebuild + Vitest + Docker dist sync + browser MCP retest; **no new open MQ**. **MQ-014** live-verified. Matrix: [`feature-test-tracking.md`](feature-test-tracking.md) `notifications`.*
