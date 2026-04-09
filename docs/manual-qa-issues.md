# Manual QA issue log

_Logged during [manual feature & workflow test loop](prompts/manual-feature-workflow-test-loop-prompt.md) sessions. Scope and feature state: [`feature-tracking.md`](feature-tracking.md). Cluster coverage matrix: [`feature-test-tracking.md`](feature-test-tracking.md)._

## How to use

- Assign **MQ-** IDs sequentially per session (or per defect).
- Reference an ID from **Notes** in `feature-test-tracking.md` and from PRs/commits.
- Close items by moving them to **Resolved** with date and verification note.

---

## Open

| ID | Date | Area | Summary |
|----|------|------|---------|
| **MQ-2026-04-09-010** | 2026-04-09 | `programs-applications`, Vue new app | **`/seim/applications/new`:** select program that fails language eligibility → in-page **You don't meet this program's requirements** appears, but **Save as draft** triggers **`POST` 400** and only **`Failed to save draft: AxiosError`** in browser console (no assertive visible error; overlaps **MQ-006** pattern). Confirm whether ineligible students should be allowed to save drafts; if yes, fix API; if no, improve UI copy + a11y. |

**Repro (010):** Login `student@test.com` (password per [`feature-tracking.md`](feature-tracking.md) / `documentation/installation.md`) → **New application** → choose **DAAD Exchange - Technical University of Munich** → **Save as draft** (student profile English vs required German) → check console / network.

---

## Resolved

| ID | Date resolved | Verification |
|----|---------------|----------------|
| MQ-2026-04-09-001 | 2026-04-09 | Dockerfile copies baked `dist` to `/opt/seim-vue-dist`; `scripts/ensure_vue_dist.sh` runs before `collectstatic` in `docker-compose.yml` / `docker-compose.e2e.yml` and seeds `/app/frontend-vue/dist` when `index.html` is missing (bind mount + empty named volume). Rebuild web image: `docker compose build web`, then `docker compose up -d web`. |
| MQ-2026-04-09-002 | 2026-04-09 | `core/views.py` renders `core/contact_message.html` (extends site `base.html`) when no active custom/feedback form exists or on contact errors/thanks — no longer plain-text `HttpResponse`. |
| MQ-2026-04-09-003 | 2026-04-09 | `SPECTACULAR_SETTINGS["SERVERS"]` in `seim/settings/base.py`: default server URL is relative `/` so Try it out matches the docs origin; `:8001` and `:8000` listed as alternates. |
| CMS footer year | 2026-04-09 | `cms/templates/cms/base.html` uses `{% now "Y" %}` for the copyright year. |
| MQ-2026-04-09-004 | 2026-04-09 | `GET /data-management/` serves `DataManagementIndexView` (hub template with links filtered by `has_data_permission` … `VIEW`); login required. |
| MQ-2026-04-09-005 | 2026-04-09 | `seim/urls.py`: register `admin-dashboard/` **before** Wagtail’s `""` include so `GET /admin-dashboard/` hits `frontend.admin_dashboard_view`. |
| MQ-2026-04-09-006 | 2026-04-09 | `auth.js` normalizes DRF error bodies for login messages; `Login.vue` adds `aria-invalid`, `aria-describedby`, `id="login-form-error"`, `aria-live="assertive"` on the error alert. |
| MQ-2026-04-09-007 | 2026-04-09 | `LoginView.authentication_classes = []` so a prior Django session does not trigger `SessionAuthentication` CSRF on JSON login; regression: `test_login_switch_user_with_existing_django_session` in `tests/integration/api/test_auth_api.py`. |
| **MQ-2026-04-09-008** | 2026-04-09 | `LogoutView.authentication_classes = [JWTAuthentication]` (no Session CSRF on JSON POST). **`frontend-vue/src/stores/auth.js`:** call `POST /api/accounts/logout/` with `Authorization: Bearer <access>` **before** clearing tokens (JWT-only view needs header; prior order caused **401**). Regression: `test_logout_post_json_succeeds_with_django_session_and_jwt_header` in `tests/integration/api/test_auth_api.py`; Vitest `auth.spec.js` (logout `axios.post` third-arg headers). Rebuild/serve updated `frontend-vue/dist` for manual verify. |
| **MQ-2026-04-09-009** | 2026-04-09 | Vue list/detail use `program_name || program?.name`. `ApplicationViewSet` list/retrieve cache keys include user + path/pk (`exchange/views.py`). Tests: `test_application_viewset_cache_keys.py`, `test_list_applications_includes_program_name`, Vitest `Applications.spec.js` / `ApplicationDetail.spec.js`. |

---

*Last updated: 2026-04-09 — **Open:** **MQ-010** only. **MQ-009** resolved. Prior: **MQ-008** resolved.*
