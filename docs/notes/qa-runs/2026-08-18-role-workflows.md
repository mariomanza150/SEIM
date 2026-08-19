# Manual QA — 2026-08-18 (role-by-role workflows)

**Stack:** Compose `seim-localprod` @ `http://localhost:8020`  
**Do not recreate** `seim-web-local-prod` (docker cp of Python/Vue would be wiped).

Walked student, coordinator, admin, and partner on the live SPA. Role nav/guards and core pages loaded. Three defects found and fixed this pass.

## MQ-2026-08-18-034 — calendar status slugs

**Repro:** Student/coordinator `/seim/calendar` application rows: `Application: … (under_review)` / `(draft)`.

**Fix:** `exchange/calendar_events.py` uses `_humanize_status_name`; Vue `formatCalendarEventTitle` localizes leftover slugs.

**Live verify:** Coordinator calendar **(Draft)** / **(Nominated)** / **(Waitlist)**. No `under_review`.

## MQ-2026-08-18-035 — admin session user column

**Repro:** `/seim/admin/sessions` User cells blank. `GET /api/user-sessions/` keys were only `id`, `device`, `location`, `last_activity`, `is_active` (container Python behind host).

**Fix:** Deploy host `accounts`/`notifications` serializers + admin queryset/revoke. Live rows show `admin@test.com`, IPs, Revoke; Reminders tab lists users.

## MQ-2026-08-18-036 — tab title after role redirect

**Repro:** Partner on `/seim/partner` opening Applications/Documents kept title `Applications - SEIM` while staying on the portal.

**Fix:** `document.title` + social/canonical in `router.afterEach`. Live: both redirects settle on **Partner portal - SEIM**.

## Role smoke (after fixes)

| Role | Result | Notes |
|------|--------|-------|
| Student | Pass | Dashboard 15 apps; Tokyo draft submit disabled; documents/notifications/profile/settings/compare. |
| Coordinator | Pass | Review queue, workload, DAAD nominations, Fulbright under review, staff lists. |
| Admin | Pass | Console including Sessions and Statuses & types after dist deploy. |
| Partner | Pass | 2 applicants / 1 doc; Applications/Documents hidden and redirected. |
