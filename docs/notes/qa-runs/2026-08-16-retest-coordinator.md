> **Snapshot at test time** � ports/URLs reflect the environment when this QA run was recorded.

# Manual QA retest — Coordinator (Section 4 + permission leaks)

**Date:** 2026-08-16 (retest after local-prod rebuild)  
**Stack:** `seim-localprod` @ `http://localhost:8020`  
**Role:** `coordinator@test.com` / `coordinator123` (isolated Playwright context; not shared with student JWT)  
**Seed:** `is_email_verified=True`, role `coordinator` only, `is_admin=False` (staff flag remains for Django, not SPA admin).

## Counts

| Result | Count |
|--------|------:|
| Pass | 10 |
| Fail | 0 |
| Blocked | 0 |
| Not executed (destructive / extra) | 5 |

**Pass:** 1.4, 4.1, 4.3, 4.7, 4.9, 4.11, 4.12, 4.13, MQ-001 retest, MQ-002 retest  
**Not executed:** 4.2 preset persist, 4.4 status change, 4.5 public/internal comment round-trip, 4.6 validate/resubmit, 4.8 (admin workload — other role), 4.10/4.14/4.15 deep agreement/analytics clicks

## Login

### 1.4 Coordinator after logout — **Pass**

Dashboard **Welcome, Camila Coordinator!** Staff sidebar: Review queue, Workload, Notification routing, Exchange agreements (plus compare/docs). JWT login 200.

## Section 4

### 4.1 Review queue — **Pass**

`/seim/review-queue` **Application review queue**. No “Failed to load applications.” (exchange API live). Opened a row in 4.3.

### 4.3 Open from queue — **Pass**

`/seim/applications/68696218-040f-4fa2-8259-0b1527547451` **DAAD Exchange - Technical University of Munich, Germany** — Application details.

### 4.7 Workload (coordinator) — **Pass**

**Your workload** only (no Institution overview on this role).

### 4.9 Exchange agreements — **Pass**

List loads (no Failed to load). Seed `DEMO-SEED-AGR-*` present from seed command.

### 4.11 Notification routing — **Pass**

Routing overrides / settings categories chrome.

### 4.12 Eligibility rulesets — **Pass** (load/read; still IN PROGRESS product)

Page loads.

### 4.13 Nominations — **Pass** (live SPA)

Page loads.

## Permission leaks (morning Fails)

### MQ-2026-08-16-001 `/seim/admin/programs` — **Pass** (fixed)

Cold open redirects to `/seim/applications` **My applications**. Does not stay on Admin — Programs.

### MQ-2026-08-16-002 `/seim/partner` — **Pass** (fixed)

Cold open redirects to `/seim/applications`. Partner table not shown.

## Not executed

Did not save review-queue presets, change application status, post comments, or validate documents (shared demo data).
