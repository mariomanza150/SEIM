# Manual QA retest — Partner (Section 5)

**Date:** 2026-08-16 (retest after local-prod rebuild)  
**Stack:** `seim-localprod` @ `http://localhost:8020`  
**Role:** `partner@test.com` / `partner123` (isolated Playwright context)  
**Seed:** user created by `seed_demo_readiness` (`username=partner`, verified, role `partner` only).

## Counts

| Result | Count |
|--------|------:|
| Pass | 4 |
| Fail | 0 |
| Blocked | 0 |
| Not executed | 1 |

**Pass:** 5.1-login, 5.1 portal chrome, 5.2a, 5.2b  
**Not executed:** 5.1 View documents / Open thread click-through (table chrome loaded; skipped extra clicks)

## 5.1 Partner portal — **Pass**

JWT login 200. Dashboard **Welcome, Ines Partner!** Sidebar includes **Partner portal** (not staff review queue).

`/seim/partner`: **Partner portal**, **Your agreements**, **Applicants**. No “Failed to load partner portal.” (agreements API live).

## 5.2 Staff/admin URLs denied — **Pass**

- `/seim/review-queue` → `/seim/applications`
- `/seim/admin/programs` → `/seim/applications`

Coordinator/student denial of `/seim/partner` is in the coordinator and student retest reports (**Pass**).
