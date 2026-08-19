# Manual workflow QA — session log

_Companion to [`feature-tracking.md`](feature-tracking.md). Runbook: [`prompts/manual-feature-workflow-test-loop-prompt.md`](prompts/manual-feature-workflow-test-loop-prompt.md). Canonical defect IDs also cross-posted in [`manual-qa-issues.md`](manual-qa-issues.md) when promoted._

## Issues (MWL — manual workflow log)

| ID | Date | Cluster | Severity | Summary |
|----|------|---------|----------|---------|
| MWL-2026-08-18-001 | 2026-08-18 | `calendar-ics` | Medium | Calendar application events used raw status slugs (`under_review`, `draft`) in titles. Promoted to **MQ-2026-08-18-034**. |
| MWL-2026-08-18-002 | 2026-08-18 | `admin-console` | Medium | Live `/api/user-sessions/` omitted user identity fields; admin Sessions table showed blank User cells. Promoted to **MQ-2026-08-18-035**. |
| MWL-2026-08-18-003 | 2026-08-18 | `vue-portal` | Low | Role-denied redirects set the tab title from the blocked route when already on the fallback page. Promoted to **MQ-2026-08-18-036**. |
| MWL-2026-04-09-001 | 2026-04-09 | `url-routing` | Medium | `GET /contact/` returns **200** with **plain text** body: `No contact form configured. Please create a dynamic form in the admin.` — no HTML shell, no `<title>`; browser a11y snapshot is empty. **Repro:** open `http://localhost:8001/contact/`. **Expected:** styled contact page or clear 404/503 with navigation. |
| MWL-2026-04-09-002 | 2026-04-09 | `url-routing` | Low | Swagger UI at `/api/docs/` default server is `http://localhost:8000` while this environment used **`http://localhost:8001`** — “Try it out” may target the wrong origin until the user changes the server dropdown. |

---

## Sessions

### 2026-08-18 — Role-by-role workflow pass (manual, browser MCP)

**Environment:** `http://localhost:8020` (Compose `seim-localprod`). **Roles:** student, coordinator, admin, partner.

**Steps & results**

1. Student (`student@test.com`) — dashboard, applications, Tokyo draft, documents, notifications, profile, settings, calendar, compare, new application. Staff/admin/partner routes redirect. **Pass** except calendar slugs (**MQ-034**) and stale `frontend-vue/dist` missing Sessions/Statuses admin routes until rebuild.
2. Coordinator (`coordinator@test.com`) — review queue, workload, DAAD nominations (Diego Nominated / Elena Waitlist), agreements, eligibility, routing, forecasts, Fulbright under-review detail. Admin/partner denied. **Pass.** Calendar titles humanized after API deploy.
3. Admin (`admin@test.com`) — programs, catalogs, grades, users, forms, dynforms, data-management, workflows, documents, workload overview. Sessions 404 until dist deploy; User column blank until serializer deploy (**MQ-035**). After deploy: sessions list with emails + reminders picker; workflow catalogs. **Pass.**
4. Partner (`partner@test.com`) — portal Active agreement, 2 applicants, nav without Applications/Documents, cold student/staff/admin routes → portal. Tab title after Applications/Documents (**MQ-036**) fixed in `afterEach`. **Pass.**

**Overall:** **Pass** after MQ-034/035/036. Evidence notes: [`qa-runs/2026-08-18-role-workflows.md`](qa-runs/2026-08-18-role-workflows.md).

**Checked paths (for next run):** student core SPA; coordinator queues/nominations/agreements; admin console including `/seim/admin/sessions` and `/seim/admin/workflow-catalogs`; partner portal + denies.

---

### 2026-04-09 — Cluster `url-routing` (manual, browser MCP)

**Environment:** `http://localhost:8001` (local web). **Roles:** none (anonymous).

**Steps & results**

1. `GET /health/` — reachable (minimal document in snapshot; likely JSON).
2. `GET /api/docs/` — **Pass**; title “SEIM API”, operations list present (large a11y tree).
3. `GET /seim/login` — **Fail / env-dependent**; page title “SEIM — Vue build required”, heading “Vue SPA assets missing” with link to `http://localhost:5173`. Blocks JWT login UI on `:8001` until `frontend-vue/dist` is present or Vite dev server is used. (See [`manual-qa-issues.md`](manual-qa-issues.md) — MQ-2026-04-09-001 resolved in image/scripts; this host may still need rebuild/mount.)
4. `GET /` (CMS home) — **Pass**; hero, nav, FAQ accordion, footer `© 2026 …`.
5. `GET /contact/` — **Fail**; see **MWL-2026-04-09-001**.

**Overall:** **Partial** — API docs and home OK; SPA login path blocked on this stack; contact route mis-delivers.

**Checked paths (for next run):** `/health/`, `/api/docs/`, `/seim/login`, `/`, `/contact/`.

---

*Last updated: 2026-08-18*
