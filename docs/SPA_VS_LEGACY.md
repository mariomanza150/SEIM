# SPA vs leftover Django surfaces

**Current split (2026-08):** the student/staff application UI is the Vue 3 SPA. The Django `frontend` app is gone. Do not add new pages under a `frontend/` Django app.

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
| Dynforms builder | `/seim/admin/dynforms` and `/seim/admin/dynforms/:id` | `frontend-vue` | **SPA-canonical** visual builder; `/dynforms/` redirects here |
| Data management | `/seim/admin/data-management` | `frontend-vue` + `data_management/` API | **SPA-canonical** catalog, execute, import, cleanup, and reset; `/data-management/` redirects here |

Legacy root auth URLs (`/login/`, `/register/`, `/dashboard/`, `/password-reset/`) redirect to `/seim/...`. `/logout/` clears the session and is not a Vue route.

## Vue routes (application UI)

Mounted at `/seim/` (see `frontend-vue/src/router/index.js`): login, register, verify-email, password-reset, dashboard, applications (list/new/detail/edit), documents, notifications, profile, settings, calendar, program compare, coordinator review/workload, agreements, nominations, eligibility rulesets, analytics forecasts, partner portal, SPA admin (`/seim/admin/programs|forms|dynforms|data-management|workflows`).

## Intentionally not migrated

These remain Django by design:

1. Wagtail CMS public pages and `/cms/` admin
2. Django admin at `/seim/django-admin/`
3. Contact form at `/contact/`
4. Grades API alias `/grades/api/` (canonical is `/api/grades/`)
5. CMS seed narratives remain the Spanish example set (tokens use `INSTITUTION_*`)

## Docs that are historical

`docs/VUE_MIGRATION_PLAN.md` and `docs/FRONTEND_NEXT_STEPS.md` describe the old Django SSR frontend. Use this file and `frontend-vue/README.md` for the current state.
