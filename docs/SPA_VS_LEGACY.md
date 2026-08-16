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
| Grade translation API | `/grades/api/*` | `grades/` | API only; SPA should call this prefix |
| Analytics API + shims | `/analytics/*` and `/api/analytics/*` | `analytics/` | HTML views redirect into the SPA |
| Contact form | `/contact/` | `core/views.py` | Small Django form (CMS also has `/contacto/`) |
| Dynforms builder | `/dynforms/` | `core/dynforms_urls.py` | **Still Django**; admin-only leftover |
| Data management | `/data-management/` | `data_management/` | **Still Django templates**; operator tool |

Legacy root auth URLs (`/login/`, `/register/`, `/dashboard/`, `/password-reset/`) redirect to `/seim/...`. `/logout/` clears the session and is not a Vue route.

## Vue routes (application UI)

Mounted at `/seim/` (see `frontend-vue/src/router/index.js`): login, register, verify-email, password-reset, dashboard, applications (list/new/detail/edit), documents, notifications, profile, settings, calendar, program compare, coordinator review/workload, agreements, nominations, eligibility rulesets, analytics forecasts, partner portal, SPA admin (`/seim/admin/programs|forms|workflows`).

## Intentionally not migrated in this pass

Finishing the entire Vue migration is out of scope. Remaining slices are tracked as GitHub issues:

1. django-dynforms builder still under `/dynforms/`
2. `data_management` operator UI still Django templates
3. Grades API still outside the `/api/` prefix (SPA path was corrected to `/grades/api/scales/active/`)
4. CMS seed copy remains UAdeC-example Spanish content

## Docs that are historical

`docs/VUE_MIGRATION_PLAN.md` and `docs/FRONTEND_NEXT_STEPS.md` describe the old Django SSR frontend. Use this file and `frontend-vue/README.md` for the current state.
