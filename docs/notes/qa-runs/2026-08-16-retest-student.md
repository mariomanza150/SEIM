# Manual QA retest — Student (Sections 1–3, 6.7/9 student)

**Date:** 2026-08-16 (retest after local-prod rebuild)  
**Stack:** `seim-localprod` @ `http://localhost:8020`  
**Role:** `student@test.com` / `student123` (isolated Playwright context)  
**SPA:** real Vue login (not missing-dist). Email verified after `seed_demo_readiness`.

## Counts

| Result | Count |
|--------|------:|
| Pass | 22 |
| Fail | 0 |
| Blocked | 3 |
| Not executed (destructive / extra fixture) | 3 |

**Pass:** 1.2, 1.5, 1.6 (student half), 2.1–2.6, 2.9–2.16, 3.1, 3.2, 6.7 student, 9.1 student  
**Blocked:** 2.8 (no closed-window fixture spotted), 3.4 (no resubmit row required), 3.5 (did not force submit-gate)  
**Not executed:** 2.7 new draft save, 3.3 checklist upload (avoid extra files on shared stack)

## Auth

### 1.2 Login — **Pass**

Lands `/seim/dashboard`. **Welcome, Sofia Q Martinez Garcia!** Stats 3 / 4 / 3 / 2. Student nav only (no Review queue / Partner portal / Admin).

### 1.5 Staff URLs — **Pass**

Cold open `/seim/review-queue`, `/seim/exchange-agreements`, `/seim/notification-routing`, `/seim/nominations` → `/seim/applications`.

### 1.6 Partner URL — **Pass** (student)

`/seim/partner` → `/seim/applications`.

## Section 2

### 2.1 Dashboard — **Pass**

Next-steps + stats. `staff_leak=False`.

### 2.2 Applications list — **Pass**

`/seim/applications` **My applications** with program names (Erasmus / DAAD / Fulbright present in seed). Not “Failed to load”, not Unknown program.

### 2.3 Detail — **Pass**

Opened `…/applications/dc37033b-0609-42e5-a8d6-23964af1b225`: Movilidad Internacional, scholarship score, required documents 2/17 approved, timeline, comments.

### 2.4–2.6 New application — **Pass** (chrome / load)

`/seim/applications/new` **Create new application**, eligibility information, application tips. Did not complete a full host-tree walk or eligibility select (form loaded; no API 404).

### 2.7 Draft save — **Not executed**

Did not POST a new draft (shared demo DB). New-application form loads.

### 2.8 Closed window — **Blocked**

No closed-window program exercised; all demo programs used for the form are open.

### 2.9 Compare — **Pass**

`/seim/programs/compare` **Compare programs**.

### 2.10 / 2.11 Profile — **Pass**

Profile sections: Account, Personal, Academic, Banking, Eligibility (required to apply).

### 2.12 / 2.13 Settings — **Pass**

Settings + Profile note. Notification matrix present. **No** staff routing link (`routing_link=False`). Did not persist theme/locale toggles.

### 2.14 Calendar — **Pass**

Deadlines and calendar loaded (no Failed to load).

### 2.15 Notifications — **Pass**

Inbox page loads.

### 2.16 SPA 404 — **Pass**

`/seim/this-route-does-not-exist` → Vue **404**.

## Section 3

### 3.1 Documents list — **Pass**

`/seim/documents` loads.

### 3.2 Document detail — **Pass**

`/seim/documents/6fb30e7e-5110-46b7-b179-16b4567c5c2f` **Document details** (not stuck Loading…).

### 3.3–3.5 — **Not executed / Blocked**

No new upload, resubmit, or submit-gate mutation this retest.

## Permissions

### 6.7 / 9.1 student — **Pass**

`/seim/admin/programs` → `/seim/applications`.
