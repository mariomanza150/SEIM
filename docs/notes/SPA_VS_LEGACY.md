# SPA vs leftover Django surfaces

**Current split (2026-08):** the student/staff application UI is the Vue 3 SPA. The Django `frontend` app is not installed and is not mounted. Do not add new pages under a `frontend/` Django app.

## What serves what

| Surface | URL | Code | Status |
| --- | --- | --- | --- |
| Vue 3 SPA | `/seim/*` | `frontend-vue/` (Django serves `frontend-vue/dist/index.html`) | **Canonical app UI** |
| Wagtail public site | `/` and CMS pages | `cms/` | **Canonical marketing/CMS** |
| Wagtail admin | `/cms/` | Wagtail | Keep |
| Django admin | `/seim/django-admin/` (`/admin/` redirects here) | Django admin | Keep |
| REST API | `/api/*` | domain apps + `api/urls.py` | Canonical data plane |
| Grade translation API | `/api/grades/` (`/grades/api/` alias) | `grades/` | API only |
| Analytics API + shims | `/analytics/*` and `/api/analytics/*` | `analytics/` | HTML views redirect into the SPA |
| Contact form | `/contact/` | `core/views.py` | Small Django form (CMS also has `/contacto/`) |
| Dynforms builder | `/seim/admin/dynforms` and `/seim/admin/dynforms/:id` | `frontend-vue` | **SPA-canonical** visual builder; `/dynforms/` and `/api/application-forms/list|builder/` redirect here |
| Data management | `/seim/admin/data-management` | `frontend-vue` + `data_management/` API | **SPA-canonical** catalog, execute, import, cleanup, and reset; `/data-management/` redirects here |

Legacy root auth URLs (`/login/`, `/register/`, `/dashboard/`, `/admin-dashboard/`, `/dashboard/analytics/`, `/password-reset/`) redirect to `/seim/...`. `/logout/` clears the session and is not a Vue route.

Leftover student/staff bookmarks outside `/seim/` (`/applications/`, `/applications/create/`, `/applications/<uuid>/`, `/profile/`, `/settings/`, `/preferences/`, `/calendar/`, `/documents/`, `/notifications/`, `/review-queue/`, `/programs/compare/`) also redirect into the SPA. See `core/legacy_spa_urls.py`.

## Vue routes (application UI)

Mounted at `/seim/` (see `frontend-vue/src/router/index.js`): login, register, verify-email, password-reset, dashboard, applications (list/new/detail/edit), documents, notifications, profile, settings, calendar, program compare, coordinator review/workload, agreements, nominations, eligibility rulesets, analytics forecasts, partner portal, SPA admin (`/seim/admin/programs|catalogs|grades|forms|dynforms|data-management|workflows|documents`).

SPA aliases (not separate pages): `/seim/admin` → programs admin, `/seim/admin-dashboard` → dashboard, `/seim/analytics` → forecasts, `/seim/grades` → profile, `/seim/programs` → program compare, `/seim/exchange` → exchange agreements, `/seim/workload` → coordinator workload.

## Parity checklist

### Done

- [x] Student auth, dashboard, applications, documents, notifications, profile, settings, calendar
- [x] Program compare (`/seim/programs/compare`)
- [x] Coordinator review queue, workload, nominations, eligibility rulesets
- [x] Staff exchange agreements + agreement documents
- [x] Notification routing and analytics forecasts
- [x] Partner portal
- [x] SPA admin: programs, catalogs (home lists + host destinations hub), grade scales, forms (JSON), visual dynforms builder, data management, workflows, application edit
- [x] `/dynforms/` and application-forms HTML list/builder redirect to `/seim/admin/dynforms`
- [x] `/data-management/` HTML hub and section pages redirect to `/seim/admin/data-management`
- [x] Analytics HTML dashboard/statistics pages redirect to `/seim/dashboard` or `/seim/analytics-forecasts`
- [x] Root leftover app URLs listed above redirect into `/seim/`
- [x] Notification `action_url` values such as `/applications/<id>/` resolve inside the SPA (`frontend-vue/src/utils/navigation.js`)
- [x] Admin Forms list links through to the visual builder

### Leftover (do not treat as product UI)

- [ ] Django `frontend/` package, `templates/frontend/**`, and `tests/frontend/**` still exist on disk but are not installed or mounted
- [ ] `data_management/templates/**` and `application_forms/templates/**` are unused HTML leftovers (views redirect)
- [ ] `templates/dynforms/**` leftover after the `/dynforms/` redirect
- [ ] Root `/documents/<id>/` is **not** redirected (Wagtail files now live at `/cms-documents/`; SPA detail is `/seim/documents/:id`)
- [ ] Django admin remains the system-of-record editor for users, roles, sessions, and other operational models
- [ ] Agreement-expiration emails still deep-link to Django admin change pages (intentional)
- [ ] Backend notification `action_url` values are still stored as root paths (`/applications/...`); SPA maps them, but new writes should prefer `/seim/...`
- [ ] White-labeling / LICENSE / GitHub metadata are out of scope here

## Intentionally not migrated

These remain Django by design:

1. Wagtail CMS public pages and `/cms/` admin
2. Django admin at `/seim/django-admin/`
3. Contact form at `/contact/`
4. Grades API alias `/grades/api/` (canonical is `/api/grades/`)
5. CMS seed narratives remain the Spanish example set (tokens use `INSTITUTION_*`)

## Docs that are historical

`archive/VUE_MIGRATION_PLAN.md` and `archive/FRONTEND_NEXT_STEPS.md` describe the old Django SSR frontend. Use this file and `frontend-vue/README.md` for the current state.
