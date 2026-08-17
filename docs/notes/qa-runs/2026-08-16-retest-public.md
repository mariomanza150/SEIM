# Manual QA retest — Public (Section 0 + anonymous 1.1 / 1.3)

**Date:** 2026-08-16 (retest after local-prod rebuild)  
**Stack:** Compose project `seim-localprod` (`docker-compose.local-prod.yml`)  
**App:** `http://localhost:8020`  
**Role:** Anonymous only  
**Method:** Isolated Playwright Chromium (`channel=chrome`) plus Puppeteer for `/programas/salamanca-espana/`. IDE browser MCP had no usable tab this session.

Did not edit `manual-qa-full-checklist.md` / feature trackers.

## Counts

| Result | Count |
|--------|------:|
| Pass | 12 |
| Fail | 0 |
| Blocked | 0 |

**Pass:** 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.1, 1.3 (register / verify-email / password-reset / confirm)

## Environment (cleared vs morning QA)

Morning blockers are gone after `--no-cache` rebuild, `seed_demo_readiness`, and `restore_cms`:

- Container `/app/exchange/urls.py` is the real 81-line router (not `urlpatterns = []`).
- `/` is UAdeC CMS home (not Wagtail welcome).
- `/programas/` is the Programas de Intercambio index.
- `/seim/login` is Vue `2.0.0-vue` / Vue 3.5.27 (not “Vue build required”).

## Section 0

### 0.1 Health — **Pass**

`GET /health/` → 200 JSON: `status=healthy`, database/cache/redis healthy.

### 0.2 OpenAPI docs — **Pass**

`/api/docs/` loads **SEIM API** Swagger. Groups include authentication, accounts, **programs**.

### 0.3 Schema — **Pass**

`/api/schema/` 200. Contains `/api/programs/`, `/api/applications/`, `/api/calendar/events/`. Anonymous `GET /api/programs/` is **401 JSON** (`Authentication credentials were not provided`), not Wagtail HTML 404.

### 0.4 CMS home — **Pass**

`/` title/hero: UAdeC Dirección de Intercambio Académico. Not Wagtail welcome.

### 0.5 `/programas/` — **Pass**

Heading **Programas de Intercambio**, Available Programs, location options include Salamanca.

### 0.6 Program detail + CTAs — **Pass**

`/programas/salamanca-espana/` renders Universidad de Salamanca — España, About This Program, Detalles del Programa. CTAs: **¿Cómo Aplicar?** → `/como-aplicar/`; **Iniciar Sesión** → `/seim/login?redirect=/applications/new`.

### 0.7 Contact — **Pass**

`/contacto/` heading Contacto, full CMS chrome.

### 0.8 Anonymous SPA login — **Pass**

`/seim/login`: Sign in form, email/password, Remember me, Forgot password, Create an account. Footer `SEIM · 2.0.0-vue · Vue 3.5.27`.

### 0.9 Protected redirect — **Pass**

- `/seim/applications` → `/seim/login?redirect=/applications`
- `/seim/review-queue` → `/seim/login?redirect=/review-queue`

## Anonymous auth pages

### 1.1 Wrong password — **Pass**

`student@test.com` / `wrongpassword` stays on login; alert **Invalid credentials**.

### 1.3 Register / verify / reset — **Pass**

`/seim/register`, `/seim/verify-email`, `/seim/password-reset`, `/seim/password-reset/confirm` all render Vue (not 404 / build-required). Did not send mail.
