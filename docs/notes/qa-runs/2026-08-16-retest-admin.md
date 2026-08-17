# Manual QA retest — Admin (Sections 6, 7, 4.8)

**Date:** 2026-08-16 (retest after local-prod rebuild)  
**Stack:** `seim-localprod` @ `http://localhost:8020`  
**Role:** `admin@test.com` / `admin123` (isolated Playwright context)  
**Django admin:** also `manage.py` test client `GET /seim/django-admin/exchange/exchangeagreement/` → **200**.

## Counts

| Result | Count |
|--------|------:|
| Pass | 11 |
| Fail | 0 |
| Blocked | 0 |
| Not executed | 3 |

**Pass:** admin-login, 4.8, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7 coordinator half (see coordinator report), 7.1, 7.2, users changelist  
**Not executed this pass:** 7.3–7.5 SSR leftovers (data-management redirect / grades) — not re-clicked; morning admin pass had those green and stack is the same CMS/Django after migrate.

## SPA console

### Login — **Pass**

Dashboard **Welcome, Alex Administrator!** Navbar: App admin, Django Admin, CMS Admin.

### 4.8 Workload admin — **Pass**

Coordinator workload shows **Your workload** plus **Institution overview (admin)** and **Pending by assigned coordinator**.

### 6.1 Programs — **Pass**

`/seim/admin/programs` **Program management** (11 programs). No Failed to load.

### 6.2 Forms — **Pass**

`/seim/admin/forms` Form management.

### 6.3 Dynforms — **Pass**

`/seim/admin/dynforms` Form builders.

### 6.4 Data management — **Pass**

SPA data-management (bulk / export / import / demo setup / reset / cleanup chrome). Did not run destructive reset.

### 6.5 Workflows — **Pass**

Workflow management list.

### 6.6 Admin application edit — **Pass**

`/seim/admin/applications/dc37033b-0609-42e5-a8d6-23964af1b225` **Admin — Application**, Movilidad Internacional, Application ID shown. (A first script hit `/admin/applications/new` by following the wrong list link; UUID URL is the real 6.6 check.)

## Django / Wagtail

### 7.1 Exchange agreements changelist — **Pass** (was MQ-003 Fail)

`/seim/django-admin/exchange/exchangeagreement/` title **Select Exchange agreement to change**. HTTP 200. Column `exchange_exchangeagreement.required_gpa` exists after applying `exchange.0020` on this DB.

Users changelist also 200.

### 7.2 Wagtail `/cms/` — **Pass**

Wagtail explorer / site summary for Alex Administrator. Public `/` and `/programas/` restored separately (`restore_cms`).
