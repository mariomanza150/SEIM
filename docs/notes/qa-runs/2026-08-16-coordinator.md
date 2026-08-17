# Manual QA — Coordinator / staff (Section 4)

**Date:** 2026-08-16  
**Stack:** Compose project `seim-localprod` (`docker-compose.local-prod.yml`)  
**App:** `http://localhost:8020`  
**SPA:** `http://localhost:8020/seim/`  
**Role:** Coordinator only — `coordinator@test.com` / `coordinator123`  
**Method:** user-browser (Puppeteer) MCP, isolated Chrome profile. Did not use student/admin/partner logins. Did not run Section 8.  
**Did not edit:** `manual-qa-full-checklist.md`, `feature-tracking.md`, `feature-test-tracking.md`.

**Env (from Public QA; confirmed live, not re-diagnosed):** container `/app/exchange/urls.py` is a stub (`urlpatterns = []`). Host source has the real SimpleRouter. `GET /api/programs/`, `/api/applications/`, `/api/calendar/events/` (and other exchange routes: agreements, saved-searches, eligibility-rulesets, nominations, comments) return Wagtail HTML 404. Do not treat those as separate product bugs.

## Counts

| Result | Count |
|--------|------:|
| Pass | 4 |
| Fail | 2 |
| Blocked | 10 |
| Not executed | 1 (`4.8` — admin workload; other role) |

**Pass:** 4.7, 4.11, 4.14, 4.15  
**Fail:** coordinator reached `/seim/admin/programs`; coordinator reached `/seim/partner`  
**Blocked:** 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.9, 4.10, 4.12, 4.13

---

## Session setup

1. SPA login page at `/seim/login` is the real Vue shell (not “Vue build required”). Version line `SEIM · 2.0.0-vue · Vue 3.5.27`.
2. **First login** with documented credentials returned **“Email not verified. Please check your inbox for the verification link.”** DB at that moment: `coordinator@test.com` existed as “Coordinator User”, role `coordinator`, `is_email_verified=False`, `is_staff=False`. `partner@test.com` missing. `seed_demo_readiness` data absent (0 agreements, 2 programs, 1 unrelated draft). Users look like `create_vue_test_users` (that command does not set `is_email_verified`).
3. **Env repair (login only, no image rebuild):** set coordinator `is_email_verified=True` and `is_staff=True` so documented login could proceed. Aligns with `seed_demo_readiness` / `create_vue_test_users` (`is_staff=True`). Did **not** run `seed_demo_readiness` (would collide with other roles).
4. After repair, login landed on `/seim/dashboard` — “Welcome, Coordinator User!” Staff sidebar present (Review queue, Workload, Notification routing, Exchange agreements, Eligibility rulesets, Nominations, Demand forecasts). Also **Partner portal** and full **ADMIN** / “App admin” chrome.

---

## Section 4

### 4.1 Review queue filters (`coord-review`) — **Blocked** (env)

- **Path:** `/seim/review-queue`
- **Saw:** Page chrome **Pass** — search, Pending review, Document resubmit, Assigned to me, status (All / Draft / Submitted / Under review / Approved / Rejected / Completed), sort, Clear, Advanced filters, “My applications”.
- Exercised search `Diego`, toggled all three quick filters, set status **Under review**. Controls accept input.
- **Blocked:** banner **“Failed to load applications.”** No rows, no Open links. `GET /api/applications/` → Wagtail HTML 404 (stub `exchange/urls.py`). Empty-state-for-no-matches was **not** observed; this is a load failure.

### 4.2 Review queue presets (`coord-review`) — **Blocked** (env)

- Preset name/save/apply live under **Advanced filters** (`data-testid="review-queue-preset-name"` / `review-queue-preset-save`).
- Did not persist a preset: `GET /api/saved-searches/` → same HTML 404. No apply/default/delete exercised.

### 4.3 Open application from queue (`coord-review`) — **Blocked** (env)

- Queue had **zero** Open links (4.1 load failure).
- Direct URL `/seim/applications/e878ed55-6c94-491a-af22-d40843e311cb` (the only DB application: draft for `mmanzano@uadec.edu.mx`, **not** a demo review seed) → **“Failed to load application details.”** Same `/api/applications/` 404.
- No Diego Lopez / `student.review@test.com` seed on this stack.

### 4.4 Status change (`coord-review`) — **Blocked** (env)

- No queued/demo-safe submitted app. Application detail API 404. **Did not** change status (would not have worked; also would have touched a non-seed draft).

### 4.5 Public vs internal comment (`coord-review`) — **Blocked** (env)

- No seeded review application. Detail API 404. **Did not** post comments. **Did not** log in as the student (session exclusive to coordinator).

### 4.6 Document validate / request resubmission — **Blocked** (env / skip)

- Staff documents list empty (`GET /api/documents/` **200** `{count:0, results:[]}`). No document to validate. Skipped destructive validate/resubmit by design.

### 4.7 Workload — coordinator (`coord-review`) — **Pass**

- **Path:** `/seim/coordinator-workload`
- **Saw:** “Your workload” only: Assigned to you **0**, Your programs (any coordinator) **0**, Assigned + open resubmit **0**, Avg. days in queue (assigned) **—**.
- **No** global totals, **no** per-coordinator distribution table.
- Live `GET /api/accounts/dashboard/coordinator-workload/` **200**:  
  `{"you":{...zeros...},"global":null,"distribution":null}`  
  Matches coordinator-scoped API (admin-only fields null).

### 4.8 Workload — admin — **Not executed**

Requires logout + `admin@test.com`. Out of scope for this coordinator-only session.

### 4.9 Exchange agreements (`agreements`) — **Blocked** (env)

- **Path:** `/seim/exchange-agreements`
- **Saw:** Staff chrome **Pass** — search, status (incl. Active / Renewal pending), type, linked program, partner, expiring days, sort, Clear, **Save filters as preset**, “Default when opening this page”.
- **Blocked:** **“Failed to load agreements.”** No `DEMO-SEED-AGR-*` rows. Renewal Pending/Draft not clickable (no rows). `GET /api/exchange-agreements/` HTML 404.
- `/seim/exchange` **redirects** to `/seim/exchange-agreements` (**Pass** as redirect).

### 4.10 Agreement documents (`agreements`) — **Blocked** (env)

- `/seim/agreement-documents` **redirects** to `/seim/exchange-agreements` (**Pass** as redirect).
- Per-agreement `/seim/exchange-agreements/<id>/documents` not opened: no agreement id and agreement API 404.

### 4.11 Notification routing (`notifications`) — **Pass** (read)

- **Path:** `/seim/notification-routing`
- **Saw:** **Schema version: 12**. Category matrix (applications / comments / documents / programs / system) with email/in-app fields. Transactional catalog. Overrides table empty: “No overrides yet. Add one above.” **Create override** visible.
- **Skipped** create/edit/delete (checklist: skip destructive override delete).
- `GET /api/notifications/routing-reference/` **200** (not an exchange stub route).

### 4.12 Nominations (`nominations`) — **Blocked** (env)

- **Path:** `/seim/nominations`
- **Saw:** Page loads. Program select = only “Select a program” (no seeded/DB programs in the dropdown). No capacity/slots/table.
- DB has 2 programs; dropdown empty because `GET /api/programs/` HTML 404. Did not change ranks.

### 4.13 Eligibility rulesets (`eligibility-rulesets`) — **Blocked** (env)

- **Path:** `/seim/eligibility-rulesets` (IN PROGRESS — load/read only)
- **Saw:** Page chrome, Refresh, New ruleset. **“Failed to load rulesets.”** No table, no read dialog. `GET /api/eligibility-rulesets/` HTML 404.
- Did not create/save.

### 4.14 Analytics forecasts (`analytics`) — **Pass**

- **Path:** `/seim/analytics-forecasts`
- **Saw:** Demand forecasts SPA (not a Django API root). Program = “All programs”, Saved views / Save view chrome. No charts/tables (empty allowed).
- `/seim/analytics` **redirects** here.
- Note: `GET /api/programs/` 404 so the program dropdown cannot list DB programs; `GET /api/admin/dashboard/forecasts/` also HTML 404. Page still rendered empty rather than a Django error page.

### 4.15 Staff documents presets (`documents-core`) — **Pass**

- **Path:** `/seim/documents`
- **Saw:** Heading “Application uploads (all students, staff view)”. Filters: application, type, status, Pending review, Overdue, Clear, Advanced filters. Empty: “No documents yet”.
- Advanced filters shows **Save filters as preset** / Default checkbox. Persist not proven (`/api/saved-searches/` 404). Checklist: do not Fail if preset persist is unavailable; controls are present. List API itself **200**.

---

## Permission (coordinator must not access admin / partner)

### `/seim/admin/programs` — **Fail**

- Cold-open while logged in as Coordinator User.
- **Expected:** redirect away (typically applications/dashboard); no admin catalog.
- **Saw:** stayed on `/seim/admin/programs`, title “Admin — Programs”. Chrome: “Program management”, **New program**, Search/Active/Sort. Sidebar ADMIN section and top **App admin** dropdown also visible on every staff page.
- Data banner “Failed to load programs.” (same programs API 404) — still **not** a deny/redirect.
- **Likely cause (product, not the exchange stub):** SPA `isAdmin` treats `user.is_staff === true` as admin (`frontend-vue/src/stores/auth.js`). Documented demo coordinator is `is_staff=True`. Router `meta.adminOnly` therefore allows the console.

**Repro:**

1. Log in at `http://localhost:8020/seim/login` as `coordinator@test.com` / `coordinator123` (account must be email-verified).
2. Open `http://localhost:8020/seim/admin/programs` (or sidebar **Admin — Programs** / App admin).
3. Observe admin program catalog chrome; URL does not change to `/seim/applications` or dashboard.

### `/seim/partner` — **Fail**

- Cold-open `/seim/partner` as Coordinator User.
- **Expected:** redirect or deny; no partner table.
- **Saw:** stayed on `/seim/partner`, title “Partner portal”. Copy: “Agreements, required documents, and applicant status for your institution.” Sidebar **Partner portal** is shown to coordinator.
- “Failed to load partner portal.” (partner APIs live under stubbed `exchange/urls.py`) — still **not** a deny/redirect.
- **Likely cause (product):** `canUsePartnerPortal` is `isPartner || canUseStaffReviewQueue`, so coordinators are allowed (`auth.js` + `authNavigation.js` `meta.partnerPortal`).

**Repro:**

1. Log in as `coordinator@test.com` / `coordinator123`.
2. Open `http://localhost:8020/seim/partner` (or sidebar **Partner portal**).
3. Observe partner portal shell; URL stays `/seim/partner`.

---

## Defects

### DEF-2026-08-16-01 — Exchange API missing in `seim-localprod` image (env)

Already logged in the Public QA pass. Coordinator impact: 4.1–4.5, 4.9–4.10, 4.12–4.13 (and empty nominations/agreements/queue). **Not a new product bug.** Rebuild/replace image `exchange/urls.py`; do not Fail those items.

### DEF-2026-08-16-03 — Coordinator can open SPA admin programs (High)

- **Cluster:** `roles` / `admin-console`
- **Symptom:** Coordinator is not redirected from `/seim/admin/programs`. Admin catalog chrome and ADMIN nav render.
- **Repro:** see permission section above.
- **Expected:** coordinator denied (checklist 6.7 / 9.1).

### DEF-2026-08-16-04 — Coordinator can open partner portal (High)

- **Cluster:** `roles` / `partner`
- **Symptom:** Coordinator is not redirected from `/seim/partner`. Partner portal chrome and sidebar link render.
- **Repro:** see permission section above.
- **Expected:** coordinator denied (checklist 1.6 / 5.2 / 9.1).

### Env note — demo coordinator email unverified until repaired

- Documented login failed with “Email not verified” until `is_email_verified` was set. `create_vue_test_users` does not set that flag. Not a Section 4 UI Fail; blocks coordinator QA until repaired.

---

## Notes

- Did not rebuild the image. Did not run `restore_cms` or `seed_demo_readiness`.
- Puppeteer `fill` does not update Vue `v-model`; login used native value setters + `input` events, then `[data-testid="login-submit"]`.
- Isolated profile: `userDataDir` under `%LOCALAPPDATA%\Temp\seim-qa-coordinator-iso-20260816` with system Chrome `executablePath` (bundled Puppeteer Chrome cache missing).
- Session left on `about:blank`.
