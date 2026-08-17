# Manual QA full checklist

Session-ready walkthrough for **implemented** SEIM workflows and every live Vue route. Cluster IDs match [`feature-test-tracking.md`](feature-test-tracking.md) so later Manual QA notes can be copied into that matrix.

**Do not execute this file in the write-only authoring pass.** Fill **Result** and **Evidence notes** only during a later browser session.

## Related docs

- Coverage matrix (cluster IDs, last verified): [`feature-test-tracking.md`](feature-test-tracking.md)
- Defect IDs (`MQ-*`): [`manual-qa-issues.md`](manual-qa-issues.md)
- Manual loop runbook: [`prompts/manual-feature-workflow-test-loop-prompt.md`](prompts/manual-feature-workflow-test-loop-prompt.md)
- Product inventory (IMPLEMENTED / IN PROGRESS / backlog): [`feature-tracking.md`](feature-tracking.md)
- Prior session log (`MWL-*`): [`manual-workflow-qa-session-log.md`](manual-workflow-qa-session-log.md)
- Demo accounts: [`docs/installation.md`](../installation.md)
- Live Vue routes: `frontend-vue/src/router/index.js` (history base `/seim/`); sidebar/nav: `frontend-vue/src/layouts/AppShell.vue`

## Preconditions

**Canonical live stack (this checklist):** Compose project **`seim-localprod`** from [`docker-compose.local-prod.yml`](../../docker-compose.local-prod.yml) (`name: seim-localprod`). App URL: **`http://localhost:8020`**. SPA is under `/seim/`. Host `8020` maps to container `8000`; `8021` is also published — use **8020** as the primary URL.

Do **not** treat default-dev Compose (`web` on `8001` / `8000`) as this session’s stack.

**Confirm SPA is not the “Vue build required” / “Vue SPA assets missing” page** at `http://localhost:8020/seim/login`. If that fallback appears, stop and treat remaining SPA items as **Blocked** (env), not Fail.

**Seed** (after the `seim-localprod` stack is up):

```bash
docker compose -p seim-localprod -f docker-compose.local-prod.yml exec web python manage.py create_initial_data
docker compose -p seim-localprod -f docker-compose.local-prod.yml exec web python manage.py seed_demo_readiness
```

If the project is already running as `seim-localprod`, `docker compose -p seim-localprod exec web python manage.py …` is equivalent. Optional CMS content: `restore_cms` in the same `web` container if `/` has no marketing pages.

**Demo accounts** (from `seed_demo_readiness` / [`docs/installation.md`](../installation.md); already documented — do not invent new passwords):

| Role | Email | Password |
|------|-------|----------|
| Student | `student@test.com` | `student123` |
| Coordinator | `coordinator@test.com` | `coordinator123` |
| Admin | `admin@test.com` | `admin123` |
| Partner | `partner@test.com` | `partner123` |

Seed also creates extra students (`student.review@test.com`, `student.approved@test.com`, waitlist/rejected/completed variants, same password `student123`) and programs such as Erasmus+ Barcelona, DAAD Munich, Fulbright Harvard, plus agreements `DEMO-SEED-AGR-*`. QA fixtures: **DEMO-SEED Closed Window - University of Oslo** (2.8), **DEMO-SEED Submit Gate - University of Lisbon** (3.5), **DEMO-SEED Resubmit - University of Vienna** (3.4), **DEMO-SEED Lifecycle - University of Porto** (Section 8 — no pre-seeded student application).

**Logout between roles.** Do not switch users while still JWT-logged-in without a full logout (user menu → Logout). Historical defects: **MQ-007** (login as another role while already signed in → 403) and **MQ-008** (logout/login order). After logout, confirm `/seim/login` before the next account.

**Paths below** are site-relative. Prefix with `http://localhost:8020` (example: `/seim/login` → `http://localhost:8020/seim/login`). Vue history has no trailing slash.

## Recording rules

- One cluster (or one vertical slice) per later execution session.
- Failures: write repro steps suitable for [`manual-qa-issues.md`](manual-qa-issues.md) (`MQ-*`).
- Environment / seed / missing `dist` blockers stay **Blocked**, not Fail.
- After a future execute pass: append dated **Manual QA** notes to [`feature-test-tracking.md`](feature-test-tracking.md). Do not edit that matrix in this write-only task.
- **Result** is one of: `Pass` / `Fail` / `Blocked`. Leave the tokens in place and circle or replace with the outcome.
- Eligibility rulesets (`eligibility-rulesets`) are **IN PROGRESS** — load/read only; do not mark the product complete.
- Partner portal and Nominations are **in scope** because they are live SPA routes, even if the product tracker still lists them as P3.

## In scope vs out of scope

**In scope:** all **IMPLEMENTED** tracker features that have a live UI or documented API surface in this file; the **IN PROGRESS** eligibility-rulesets staff UI (load/read); every live Vue route in `frontend-vue/src/router/index.js` and nav in `frontend-vue/src/layouts/AppShell.vue`.

**Out of scope (mark N/A if encountered; do not Fail):**

- Google Calendar OAuth2 / two-way sync (ICS/webcal subscribe **is** in scope)
- Scholarship award state machine (staff award workflow, disbursement)
- Electronic signatures for agreements/approvals
- Other unimplemented P2/P3: advanced document intelligence, institutional BI warehouse, full WCAG audit, cross-institution comms hub beyond the partner thread UI that already exists

---

## Live Vue route map (reference)

| Cluster / surface | Path (under `/seim/`) | Who (nav / guard) |
|-------------------|----------------------|-------------------|
| `auth-api` | `/login`, `/register`, `/verify-email`, `/password-reset`, `/password-reset/confirm` | Anonymous |
| `vue-portal` | `/dashboard` | Authenticated |
| `programs-applications` | `/applications`, `/applications/new`, `/applications/:id`, `/applications/:id/edit` | Authenticated |
| `readiness-compare` | `/programs/compare` (`/programs` redirects here) | Authenticated |
| `documents-core` | `/documents`, `/documents/:id` | Authenticated |
| `notifications` | `/notifications` | Authenticated |
| `profile-catalogs` | `/profile` (`/grades` redirects here) | Authenticated |
| `settings-ui` | `/settings` (`/preferences` redirects here) | Authenticated |
| `calendar-ics` | `/calendar` | Authenticated |
| `coord-review` | `/review-queue`, `/coordinator-workload` | Staff (`staffReviewQueue`) |
| `agreements` | `/exchange-agreements`, `/exchange-agreements/:agreementId/documents` (`/agreement-documents` and `/exchange` redirect to agreements) | Staff |
| `notifications` | `/notification-routing` | Staff |
| `eligibility-rulesets` | `/eligibility-rulesets` | Staff — **IN PROGRESS**, load/read |
| `nominations` | `/nominations` | Staff — live SPA (tracker may still say P3) |
| `analytics` | `/analytics-forecasts` (`/analytics` redirects here) | Staff |
| `partner` | `/partner` | Partner only (`partnerPortal`) |
| `admin-console` | `/admin/programs`, `/admin/forms`, `/admin/dynforms`, `/admin/dynforms/:id`, `/admin/data-management`, `/admin/workflows`, `/admin/workflows/:id`, `/admin/applications/:id` (`/admin` → programs) | Admin |
| `vue-portal` | unknown path → NotFound | Any |

Sidebar (`AppShell.vue`): Dashboard, Applications, Program compare, Documents, Calendar, Notifications, Settings (all signed-in). Staff also: Review queue, Workload, Notification routing, Exchange agreements, Eligibility rulesets, Nominations, Analytics forecasts. Partner: Partner portal. Admin dropdown: Programs, Forms, Dynforms, Data management, Workflows, Eligibility rulesets; plus Django admin and Wagtail `/cms/` links.

---

## 0. Environment and public surfaces (`url-routing`, `cms-public`)

### 0.1 Health (`url-routing`)

- [ ] **Health JSON**
  - **Role:** Anonymous
  - **Path:** `/health/`
  - **Steps:** Open `http://localhost:8020/health/`.
  - **Expected:** JSON health payload (status / db / cache) without login. Not an HTML error page.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 0.2 OpenAPI docs (`url-routing`)

- [ ] **Swagger UI**
  - **Role:** Anonymous
  - **Path:** `/api/docs/`
  - **Steps:** Open `/api/docs/`. Confirm title and operation groups (programs, applications, documents, calendar, grades, analytics, notifications).
  - **Expected:** SEIM API Swagger loads. “Try it out” origin should match **8020** (or relative `/`). Wrong default server is a note, not a product Fail unless Try-it-out is unusable.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 0.3 OpenAPI schema (`url-routing`)

- [ ] **Schema download**
  - **Role:** Anonymous
  - **Path:** `/api/schema/`
  - **Steps:** Open `/api/schema/`.
  - **Expected:** OpenAPI document (YAML/JSON) returns 200.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 0.4 CMS home (`cms-public`)

- [ ] **Public homepage**
  - **Role:** Anonymous
  - **Path:** `/`
  - **Steps:** Open `/`. Scan hero, primary nav, FAQ if present, footer.
  - **Expected:** Wagtail marketing home (not the Vue shell, not a 404). If empty, **Blocked** pending `restore_cms`.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 0.5 Program index (`cms-public`)

- [ ] **`/programas/` listing**
  - **Role:** Anonymous
  - **Path:** `/programas/`
  - **Steps:** Open `/programas/`. Use search and any location/filter controls if shown.
  - **Expected:** Program cards/list and a compare and/or apply CTA region. Count may vary with CMS seed.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 0.6 Program detail + CTAs (`cms-public`)

- [ ] **Program detail apply/compare**
  - **Role:** Anonymous
  - **Path:** `/programas/<slug>/` (pick any listed program)
  - **Steps:** Open a program from `/programas/`. Find Apply and Compare CTAs; follow each far enough to see destination (CMS or `/seim/…`).
  - **Expected:** Detail headings render. Apply/compare CTAs are present and navigate (login redirect is OK for Apply).
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 0.7 Contact (`cms-public`, `url-routing`)

- [ ] **Contact page**
  - **Role:** Anonymous
  - **Path:** `/contact/` (also try `/contacto/` if CMS uses that slug)
  - **Steps:** Open `/contact/`.
  - **Expected:** Full site shell (nav/footer), not a bare-text `HttpResponse`. Body may say no Wagtail form is configured — that is acceptable if the HTML chrome is present.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 0.8 Anonymous SPA login (`url-routing`, `vue-portal`)

- [ ] **Login page is real SPA**
  - **Role:** Anonymous
  - **Path:** `/seim/login`
  - **Steps:** Open `/seim/login`. Confirm Sign In form (email/password), skip link, not “Vue build required”.
  - **Expected:** Vue login shell at `http://localhost:8020/seim/login`.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 0.9 Protected SPA redirect (`url-routing`, `roles`)

- [ ] **Anonymous protected route**
  - **Role:** Anonymous
  - **Path:** `/seim/applications` (also spot-check `/seim/review-queue`)
  - **Steps:** With no session, open `/seim/applications`, then `/seim/review-queue`.
  - **Expected:** Redirect to `/seim/login?redirect=/applications` and `/seim/login?redirect=/review-queue`. Login form visible.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

---

## 1. Auth (`auth-api`, `roles`)

### 1.1 Login failure (`auth-api`)

- [ ] **Wrong password shows UI error**
  - **Role:** Anonymous
  - **Path:** `/seim/login`
  - **Steps:** Submit `student@test.com` / `wrongpassword`. Inspect the form (not only the console).
  - **Expected:** Visible error in the page (`aria-live` / alert). Stay on login. No dashboard.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 1.2 Login success (`auth-api`)

- [ ] **Student login**
  - **Role:** Student
  - **Path:** `/seim/login`
  - **Steps:** Sign in `student@test.com` / `student123`.
  - **Expected:** Lands on `/seim/dashboard` (or `?redirect=` target). App shell + user name (Sofia Martinez).
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 1.3 Auth pages load (`auth-api`)

- [ ] **Register / verify / password-reset**
  - **Role:** Anonymous (logout first)
  - **Path:** `/seim/register`, `/seim/verify-email`, `/seim/password-reset`, `/seim/password-reset/confirm`
  - **Steps:** Logout. Open each path. Do not need to complete email delivery.
  - **Expected:** Each page renders a form/heading (not 404, not build-required). Confirm page accepts token query if shown.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 1.4 Logout then other role (`auth-api`, `roles`)

- [ ] **Full logout before coordinator**
  - **Role:** Student → Coordinator
  - **Path:** `/seim/login`
  - **Steps:** While student: user menu → Logout. Confirm login page. Then `coordinator@test.com` / `coordinator123`.
  - **Expected:** Logout clears session. Coordinator login **200**, not **403**. Dashboard/staff chrome for Camila Coordinator. (Regression: **MQ-007** / **MQ-008**.)
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 1.5 Student blocked from staff routes (`roles`)

- [ ] **Student cannot use staff URLs**
  - **Role:** Student
  - **Path:** `/seim/review-queue`, `/seim/exchange-agreements`, `/seim/notification-routing`
  - **Steps:** Logout, login as student. Paste each URL (cold navigation).
  - **Expected:** Redirect to `/seim/applications` (or another student-safe route). No review-queue / agreements / routing matrix chrome.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 1.6 Partner-only portal (`roles`, `partner`)

- [ ] **Partner can open portal; staff/student cannot**
  - **Role:** Partner, then Student, then Coordinator (logout between each)
  - **Path:** `/seim/partner`
  - **Steps:** Login `partner@test.com` / `partner123` → open `/seim/partner` (sidebar “Partner portal”). Logout. Student: open `/seim/partner`. Logout. Coordinator: open `/seim/partner`.
  - **Expected:** Partner sees portal. Student/coordinator denied or redirected (not the partner agreements table). Admin is not a partner unless seeded that way — expect deny/redirect.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

---

## 2. Student core (`vue-portal`, `programs-applications`, `profile-catalogs`, `settings-ui`, `readiness-compare`)

Use **Student** `student@test.com` unless noted. Logout/login if you were another role.

### 2.1 Dashboard (`vue-portal`)

- [ ] **Next-steps and stats**
  - **Role:** Student
  - **Path:** `/seim/dashboard`
  - **Steps:** Open Dashboard from sidebar. Read stat cards and next-steps list. Follow one next-step or card link.
  - **Expected:** Stats (applications / documents / notifications / pending) and next-steps. Links go to the matching SPA page. Shell nav matches a student (no staff-only items).
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 2.2 Applications list (`programs-applications`)

- [ ] **List with program titles**
  - **Role:** Student
  - **Path:** `/seim/applications`
  - **Steps:** Open Applications. Scan rows, status filters, pagination if more than one page.
  - **Expected:** Program **names** (e.g. Erasmus+, Fulbright, DAAD), not “Unknown program” and not raw UUIDs. Seeded apps across statuses if seed ran.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 2.3 Application detail — timeline, comments, readiness (`programs-applications`, `readiness-compare`)

- [ ] **Detail panes**
  - **Role:** Student
  - **Path:** `/seim/applications/<id>` (open any seeded row)
  - **Steps:** Open detail. Check breadcrumb program title, status, timeline, comments thread, readiness/headline, document checklist chrome.
  - **Expected:** Timeline events with actor names where seeded. Comments visible. Readiness level/score or headline present. Program title, not UUID.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 2.4 New application — filters and presets (`programs-applications`, `readiness-compare`)

- [ ] **Program filters / presets**
  - **Role:** Student
  - **Path:** `/seim/applications/new`
  - **Steps:** Open New application. Use program search/filters (`accepting_applications` / location if present). Save or apply a filter preset if the UI offers one.
  - **Expected:** Program list is labeled with names. Filters change the list. Preset save/apply does not error.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 2.5 Eligibility preview (`programs-applications`)

- [ ] **Check-eligibility alert**
  - **Role:** Student
  - **Path:** `/seim/applications/new`
  - **Steps:** Select a program (try Fulbright and one other). Wait for eligibility preview.
  - **Expected:** Assertive preview (eligible / ineligible reasons). Draft save still allowed when ineligible (**MQ-010**). Do not require submit to pass this item.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 2.6 Host destination cascade (`programs-applications`, `mobility-documents`)

- [ ] **Institution → school → program → subjects**
  - **Role:** Student
  - **Path:** `/seim/applications/new`
  - **Steps:** Select a seeded program that has a host tree (Erasmus+ / DAAD / Fulbright). Walk host institution → school → academic program → subjects.
  - **Expected:** Each level enables the next. Empty host tree: note **Blocked** (seed), not Fail.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 2.7 Draft save (`programs-applications`)

- [ ] **Save as draft**
  - **Role:** Student
  - **Path:** `/seim/applications/new`
  - **Steps:** Fill the minimum fields. Save as draft (including when eligibility preview is ineligible). Return to `/seim/applications`.
  - **Expected:** Draft appears on the list. No hard eligibility block on draft create.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 2.8 Window-closed program (`programs-applications`)

- [ ] **Closed window disabled**
  - **Role:** Student
  - **Path:** `/seim/applications/new`
  - **Steps:** Look for a program whose apply window is closed (seed or filter). Try to select/submit it.
  - **Expected:** Closed program is disabled or submit/create is blocked with a clear message. If every demo program is open, mark **Blocked** (no closed fixture) and note names checked.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 2.9 Compare (`readiness-compare`)

- [ ] **Program compare**
  - **Role:** Student
  - **Path:** `/seim/programs/compare`
  - **Steps:** Open from sidebar. Toggle 2–4 program checkboxes. Use Clear selection. Follow **New application** (Apply deep-link).
  - **Expected:** Side-by-side compare. Selection can be cleared. Apply/new-application link reaches `/seim/applications/new` (optional `?ids=` / program preselect). `/seim/programs` redirects here.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 2.10 Profile catalogs (`profile-catalogs`)

- [ ] **School / program catalogs**
  - **Role:** Student
  - **Path:** `/seim/profile`
  - **Steps:** Open Profile. Change home school if listed; confirm academic program options reload. Save.
  - **Expected:** Catalog dropdowns (not free-text only for school/program). Save succeeds; values persist on refresh.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 2.11 Profile GPA, languages, banking, semester/credits (`profile-catalogs`)

- [ ] **Eligibility + banking fields**
  - **Role:** Student
  - **Path:** `/seim/profile`
  - **Steps:** Review GPA, primary + additional languages, semester, credits %, banking/CLABE. Change one field and save.
  - **Expected:** Fields visible and labeled. Save persists. Seeded student starts with GPA ~3.7 / English C1.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 2.12 Settings appearance and locale (`settings-ui`)

- [ ] **Theme, font, contrast, locale**
  - **Role:** Student
  - **Path:** `/seim/settings`
  - **Steps:** Toggle theme (or navbar sun/moon), font size, high contrast. Switch interface language **en** ↔ **es**. Save. Open one inner page (Applications). Switch back to en before later sections unless testing i18n.
  - **Expected:** Appearance applies (page + navbar). Locale changes chrome strings on Settings and the inner page. `/seim/preferences` redirects here.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 2.13 Settings notifications (`settings-ui`, `notifications`)

- [ ] **Matrix + digest; no staff routing link**
  - **Role:** Student
  - **Path:** `/seim/settings`
  - **Steps:** Open Notifications on Settings. Toggle an email/in-app row and digest cadence. Look for a link to notification routing.
  - **Expected:** Matrix + digest controls save. Email digest may stay disabled until system email is on. **No** staff routing-matrix link for student.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 2.14 Calendar (`calendar-ics`)

- [ ] **Events, toggles, saved views, ICS**
  - **Role:** Student
  - **Path:** `/seim/calendar`
  - **Steps:** Open Calendar / Deadlines. Use type toggles and date range. Save a view if offered. Copy HTTPS ICS and webcal subscribe URLs (do not complete Google OAuth — N/A).
  - **Expected:** Event list or empty state. Toggles filter types. Subscribe fields copyable. No Google OAuth UI required.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 2.15 Notifications inbox (`notifications`)

- [ ] **Notification center**
  - **Role:** Student
  - **Path:** `/seim/notifications`
  - **Steps:** Open from sidebar and from the navbar bell. Filter/clear if present. Open one item if seeded.
  - **Expected:** Inbox list (seed creates notifications). Bell dropdown + “view all” reach this page.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 2.16 SPA 404 (`vue-portal`)

- [ ] **Not found**
  - **Role:** Student
  - **Path:** `/seim/this-route-does-not-exist`
  - **Steps:** Open a nonsense `/seim/…` path while logged in.
  - **Expected:** Vue NotFound page (not Django 404 HTML, not a blank shell).
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

---

## 3. Documents (`documents-core`, `mobility-documents`)

Stay **Student** unless a step says staff.

### 3.1 Documents list filters (`documents-core`)

- [ ] **Readable program and type labels**
  - **Role:** Student
  - **Path:** `/seim/documents`
  - **Steps:** Open Documents. Use application and type filters. Read row labels.
  - **Expected:** Filter options and rows show **program names** and **document type names**, not raw application UUIDs or numeric type ids only (**MQ-011** / **MQ-012**).
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 3.2 Document detail (`documents-core`)

- [ ] **Preview, download, comments, replace**
  - **Role:** Student
  - **Path:** `/seim/documents/<id>`
  - **Steps:** Open a seeded PDF. Preview/download. Add a comment. Replace the file with a small PDF if the control is enabled.
  - **Expected:** Preview (iframe or download). Comments persist. Replace updates the file or shows a clear error. Breadcrumb uses type/filename, not stuck “Loading…”.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 3.3 Application checklist + upload (`documents-core`, `mobility-documents`)

- [ ] **Checklist upload**
  - **Role:** Student
  - **Path:** `/seim/applications/<id>` (draft or submitted with checklist)
  - **Steps:** On application detail, read `document_checklist` / required types (MX mobility types if shown). Upload a required type.
  - **Expected:** Type labels (not “2 Invalid”). Upload attaches to the application. Mobility/scheme required types appear when the program has them.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 3.4 Resubmit path (`documents-core`)

- [ ] **Resubmission if seeded**
  - **Role:** Student (staff may have requested resubmit on a demo doc)
  - **Path:** `/seim/documents` or application checklist
  - **Steps:** Look for a document / request that needs resubmit. Upload a replacement if present.
  - **Expected:** Resubmit control works **or** no such seed row — then **Blocked** (no fixture), not Fail.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 3.5 Submit gated on approved docs (`documents-core`, `programs-applications`)

- [ ] **Submit blocked until required docs approved**
  - **Role:** Student
  - **Path:** `/seim/applications/<id>`
  - **Steps:** On a draft that still has unapproved required types, try Submit. If seed already has an approved complete app, use a new draft + upload without staff approval.
  - **Expected:** Submit returns a clear 400/UI error until staff-validated required docs exist. If seed cannot produce this state, **Blocked**.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

---

## 4. Coordinator / staff (`coord-review`, `agreements`, `notifications`, `analytics`)

Logout from student. Login **Coordinator** `coordinator@test.com` / `coordinator123`. For 4.8 use **Admin** after a full logout.

### 4.1 Review queue filters (`coord-review`)

- [ ] **Search, status, pending / resubmit / assigned-to-me**
  - **Role:** Coordinator
  - **Path:** `/seim/review-queue`
  - **Steps:** Open Review queue from sidebar. Search. Filter by status. Toggle pending review, needs document resubmit, assigned-to-me.
  - **Expected:** Queue table/list with **Open** links. Filters change rows (empty state is OK if the flag has no matches).
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 4.2 Review queue presets (`coord-review`)

- [ ] **Saved presets**
  - **Role:** Coordinator
  - **Path:** `/seim/review-queue`
  - **Steps:** Set filters. Save a preset. Reload the page. Apply / set default / delete if safe.
  - **Expected:** Preset persists for this user (`search_type=application`). Default applies on open if set.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 4.3 Open application from queue (`coord-review`)

- [ ] **Open application**
  - **Role:** Coordinator
  - **Path:** `/seim/review-queue` → `/seim/applications/<id>`
  - **Steps:** Open a queued application (Diego Lopez / review seed if present).
  - **Expected:** Staff can view student application detail (status, docs, comments).
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 4.4 Status change (`coord-review`)

- [ ] **Change status**
  - **Role:** Coordinator
  - **Path:** `/seim/applications/<id>`
  - **Steps:** Move a **submitted** / **under_review** app one legal step (e.g. under review). Prefer a demo review student, not the main student’s only draft if you still need it for §8.
  - **Expected:** Status updates. Student-facing status changes. Illegal transitions are rejected clearly.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 4.5 Public vs internal comment (`coord-review`)

- [ ] **Comment visibility**
  - **Role:** Coordinator, then Student (logout between)
  - **Path:** `/seim/applications/<id>`
  - **Steps:** Coordinator posts one **public** and one **internal** comment. Logout. Login as the application’s student. Open the same detail.
  - **Expected:** Student sees public, not internal. Coordinator sees both.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 4.6 Document validate / request resubmission (`coord-review`, `documents-core`)

- [ ] **Staff document actions**
  - **Role:** Coordinator
  - **Path:** `/seim/documents/<id>` or application checklist
  - **Steps:** Validate/approve one document. Request resubmission on another (or the same after a second file) if the action exists.
  - **Expected:** Validate marks approved. Resubmit request appears for the student. Errors if over limit are explicit.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 4.7 Workload — coordinator (`coord-review`)

- [ ] **Workload (you only)**
  - **Role:** Coordinator
  - **Path:** `/seim/coordinator-workload`
  - **Steps:** Open Workload from sidebar.
  - **Expected:** “You” metrics (assigned + coordinated-program pending). **No** global totals / per-coordinator distribution (admin-only).
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 4.8 Workload — admin (`coord-review`)

- [ ] **Workload global / distribution**
  - **Role:** Admin
  - **Path:** `/seim/coordinator-workload`
  - **Steps:** Logout. Login `admin@test.com` / `admin123`. Open `/seim/coordinator-workload`.
  - **Expected:** Global metrics (including stale-under-review if shown) **and** per-coordinator distribution.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 4.9 Exchange agreements (`agreements`)

- [ ] **Filters, presets, renewal actions**
  - **Role:** Coordinator (logout from admin first)
  - **Path:** `/seim/exchange-agreements`
  - **Steps:** Open Exchange agreements. Filter All vs Active, type, program, partner, expiring. Save a preset. Find `DEMO-SEED-AGR-*`. Use renewal **Pending** and **Draft** (successor) on one row if enabled.
  - **Expected:** Table of demo agreements (Barcelona Erasmus, DAAD, Fulbright, …). Active subset smaller than All. Renewal actions succeed or explain why not. `/seim/exchange` redirects here.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 4.10 Agreement documents (`agreements`)

- [ ] **Per-agreement or staff documents list**
  - **Role:** Coordinator
  - **Path:** `/seim/exchange-agreements/<agreementId>/documents` (from a row). `/seim/agreement-documents` should redirect to the agreements list.
  - **Steps:** Open documents for one agreement. Confirm list/download. Note presets if the page has them.
  - **Expected:** Agreement documents list (or empty state). Redirect from `/agreement-documents` works.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 4.11 Notification routing (`notifications`)

- [ ] **Matrix + override CRUD**
  - **Role:** Coordinator
  - **Path:** `/seim/notification-routing`
  - **Steps:** Open Notification routing. Confirm schema version / category matrix. Create, edit, and delete one override if the UI allows (use a harmless test row).
  - **Expected:** Page loads (schema version ~12 historically). Override create/update/delete works or is clearly read-only. Student must not reach this page (already §1.5).
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 4.12 Nominations (`nominations`)

- [ ] **Nominations by program (live SPA)**
  - **Role:** Coordinator
  - **Path:** `/seim/nominations`
  - **Steps:** Open Nominations (sidebar). Select a seeded program. Read capacity / slots remaining. If rows exist, change a rank and save if a save control exists.
  - **Expected:** Program select, capacity/slots, table or empty state. **In scope** as a live route even if the tracker still lists nominations as P3. Do not Fail for missing matching-cycle product.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 4.13 Eligibility rulesets — load/read only (`eligibility-rulesets`)

- [ ] **Rulesets list (IN PROGRESS)**
  - **Role:** Coordinator or Admin
  - **Path:** `/seim/eligibility-rulesets`
  - **Steps:** Open Eligibility rulesets. Confirm the table loads (seed may include “Demo Fulbright GPA overlay”). Open a row **read** dialog if present. **Do not** treat create/save/editor as product-complete. Skip write actions unless they are obviously safe and already wired.
  - **Expected:** List loads without error (empty table is OK). This cluster is **IN PROGRESS** — Pass = page/API readable. Do not mark the feature implemented from this item.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 4.14 Analytics forecasts (`analytics`)

- [ ] **Forecasts SPA**
  - **Role:** Coordinator
  - **Path:** `/seim/analytics-forecasts`
  - **Steps:** Open Analytics forecasts. `/seim/analytics` should redirect here.
  - **Expected:** Forecasts page renders (charts/tables or empty). Not a Django API root. Predictive warehouse / BI is N/A.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 4.15 Staff documents presets (`documents-core`, `coord-review`)

- [ ] **Staff documents list presets**
  - **Role:** Coordinator
  - **Path:** `/seim/documents`
  - **Steps:** As coordinator, open Documents. Use filters and save a preset if the staff list supports it.
  - **Expected:** Staff sees a broader document set than the student. Preset save works **or** controls are absent (note Partial; do not Fail if presets are student-queue-only).
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

---

## 5. Partner (`partner` — live SPA; tracker may still say P3)

### 5.1 Partner portal (`partner`)

- [ ] **Agreements, documents, thread**
  - **Role:** Partner
  - **Path:** `/seim/partner`
  - **Steps:** Logout. Login `partner@test.com` / `partner123`. Open Partner portal. Confirm agreements table. **View documents** on a row. **Open thread**.
  - **Expected:** Agreements (seed ties partner to `DEMO-SEED-AGR-001` / Erasmus framework). Documents panel and thread UI open. Empty docs/thread is OK if chrome works.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 5.2 Partner denial already covered

Student/coordinator denial is **§1.6**. If you skipped it, run it here.

- [ ] **Non-partner denied** (if not done in §1.6)
  - **Role:** Student or Coordinator
  - **Path:** `/seim/partner`
  - **Steps:** Cold-open `/seim/partner` as student or coordinator.
  - **Expected:** Redirect or deny; no partner table.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

---

## 6. Admin SPA console (`dynamic-forms`, `data-management`, `admin-console`)

Logout. Login **Admin** `admin@test.com` / `admin123`. Confirm Admin console dropdown in the navbar.

### 6.1 Admin programs (`admin-console`)

- [ ] **Programs console**
  - **Role:** Admin
  - **Path:** `/seim/admin/programs`
  - **Steps:** Open from Admin console menu. Scan list. Open one program if the UI allows (read is enough).
  - **Expected:** Admin programs list. `/seim/admin` redirects here.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 6.2 Admin forms (`dynamic-forms`)

- [ ] **Forms catalog**
  - **Role:** Admin
  - **Path:** `/seim/admin/forms`
  - **Steps:** Open Admin → Forms.
  - **Expected:** Form types/catalog list (seeded forms if present).
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 6.3 Dynforms list + editor (`dynamic-forms`)

- [ ] **Dynforms and editor**
  - **Role:** Admin
  - **Path:** `/seim/admin/dynforms`, then `/seim/admin/dynforms/<id>`
  - **Steps:** Open Dynforms. Open one form in the editor (do not need to publish a new production form).
  - **Expected:** List + editor canvas/fields. Unsaved close is OK.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 6.4 Data management SPA (`data-management`)

- [ ] **SPA data-management**
  - **Role:** Admin
  - **Path:** `/seim/admin/data-management`
  - **Steps:** Open Data management. Read catalog / execute / import / cleanup / reset chrome. **Do not** run reset or destructive cleanup on this shared stack unless you can re-seed immediately.
  - **Expected:** Console loads. Destructive actions are gated/confirmed. See §7 for `/data-management/` redirect.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 6.5 Workflows + editor (`admin-console`, `dynamic-forms`)

- [ ] **Workflows**
  - **Role:** Admin
  - **Path:** `/seim/admin/workflows`, then `/seim/admin/workflows/<id>`
  - **Steps:** Open Workflows. Open one editor.
  - **Expected:** List + editor. Read-only pass is enough.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 6.6 Admin application edit (`admin-console`, `programs-applications`)

- [ ] **Optional application editor**
  - **Role:** Admin
  - **Path:** `/seim/admin/applications/<id>`
  - **Steps:** Copy a demo application UUID from `/seim/applications` or the review queue. Open `/seim/admin/applications/<id>`.
  - **Expected:** Admin application editor loads. If 404 for a valid id, Fail; if you have no id, **Blocked**.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 6.7 Non-admin redirected (`roles`, `admin-console`)

- [ ] **Student/coordinator cannot use admin console**
  - **Role:** Student, then Coordinator
  - **Path:** `/seim/admin/programs`
  - **Steps:** Logout. Login student; open `/seim/admin/programs`. Logout. Login coordinator; open the same URL.
  - **Expected:** Redirect away (typically `/seim/applications` or dashboard). No admin catalog.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

---

## 7. Django / Wagtail / SSR leftovers (`analytics`, `data-management`, `grades`)

Use **Admin** unless noted.

### 7.1 Django admin (`url-routing`)

- [ ] **Users, programs, agreements**
  - **Role:** Admin
  - **Path:** `/seim/django-admin/` (navbar “Django admin”; `/admin/` and `/django/admin/` should redirect here, not to Vue `/seim/admin/*`)
  - **Steps:** Open Django admin. Browse users/roles, exchange programs, exchange agreements.
  - **Expected:** Admin login may reuse the session or ask for `admin@test.com` / `admin123`. Change lists load.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 7.2 Wagtail (`cms-public`)

- [ ] **Wagtail admin**
  - **Role:** Admin / staff
  - **Path:** `/cms/`
  - **Steps:** Open `/cms/` (navbar CMS admin). Sign in if prompted. Open the page tree.
  - **Expected:** Wagtail explorer, not Vue. Staff can see pages used on `/` and `/programas/`.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 7.3 Data-management hub redirect (`data-management`)

- [ ] **Legacy hub**
  - **Role:** Anonymous, then Admin
  - **Path:** `/data-management/`
  - **Steps:** Logged out, open `/data-management/`. Then as admin, open it again.
  - **Expected:** Anonymous → login (`/seim/login/?next=…` or `/login/?next=…`). Authenticated admin → `/seim/admin/data-management` (or an equivalent hub that requires login). Not a 404.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 7.4 SSR analytics exports (`analytics`)

- [ ] **CSV / XLSX / PDF if still mounted**
  - **Role:** Admin
  - **Path:** `/dashboard/analytics/`
  - **Steps:** Open `/dashboard/analytics/`. If the page exists, trigger export CSV, XLSX/Excel, and PDF. If the URL 404s or redirects to Vue forecasts only, record that and skip file checks (**Blocked** or N/A — not Fail if the SPA forecasts page already passed).
  - **Expected:** Historical SSR exports still work **or** the route is clearly gone in favor of `/seim/analytics-forecasts`. Student hitting `/admin-dashboard/` should not 404 (redirect to dashboard).
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 7.5 Grades API only (`grades`)

- [ ] **OpenAPI grades — no SPA**
  - **Role:** Admin (or any authenticated user for browsable API)
  - **Path:** `/api/docs/` (grades group) and `/grades/api/scales/` (alias; canonical `/api/grades/`)
  - **Steps:** In Swagger, find grades scales/values/translations. Open `/grades/api/scales/` (login if 401). Confirm `/seim/grades` redirects to Profile, not a grades console.
  - **Expected:** Grades REST exists. **No** dedicated Vue grades UI. N/A for a grades SPA page.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

---

## 8. Cross-role lifecycle (one thin end-to-end)

Use a **new draft** from `student@test.com` so you do not depend on leftover §2/§4 edits. Logout between every role change.

### 8.1 Student draft (`programs-applications`)

- [ ] **Create draft**
  - **Role:** Student
  - **Path:** `/seim/applications/new`
  - **Steps:** Create a draft for an open program (host cascade if required). Save. Note the application id/URL.
  - **Expected:** Draft on `/seim/applications`.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 8.2 Upload (`documents-core`)

- [ ] **Upload required doc**
  - **Role:** Student
  - **Path:** `/seim/applications/<id>`
  - **Steps:** Upload at least one required checklist file.
  - **Expected:** Checklist shows uploaded / pending review.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 8.3 Submit or waitlist (`programs-applications`)

- [ ] **Submit**
  - **Role:** Student
  - **Path:** `/seim/applications/<id>`
  - **Steps:** Submit. If required docs are not staff-approved, either get a coordinator to approve first (§8.3b) or record the gate and use a seed app that can submit. If the program is at capacity, waitlist is a Pass.
  - **Expected:** Status **submitted** or **waitlist**, or a clear doc-gate error (then coordinate approve-docs and retry).
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 8.4 Coordinator review + comment (`coord-review`)

- [ ] **Staff review**
  - **Role:** Coordinator
  - **Path:** `/seim/review-queue` → application detail
  - **Steps:** Find the application. Add a **public** comment. Optionally validate the uploaded doc so submit can complete.
  - **Expected:** Comment saved. Queue still lists the app until approved.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 8.5 Student sees update (`notifications`, `vue-portal`)

- [ ] **Status / notification / `application.sync`**
  - **Role:** Student
  - **Path:** `/seim/applications/<id>`, `/seim/notifications`, dashboard
  - **Steps:** Logout/login student (or keep a second browser if you can). Watch detail status, inbox, toast. If WebSocket is up, a toast/list refresh from `application.sync` is a plus.
  - **Expected:** Student sees the new status and/or a notification. Toast is Pass if it appears; missing toast with updated detail/inbox is still Pass if sync is visible somehow. Total silence is Fail.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 8.6 Coordinator approve (`coord-review`)

- [ ] **Approve**
  - **Role:** Coordinator
  - **Path:** `/seim/applications/<id>`
  - **Steps:** Set status to **approved** (use this lifecycle app, not an unrelated completed seed unless submit failed).
  - **Expected:** Status approved.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 8.7 Student sees approved (`programs-applications`)

- [ ] **Approved on detail**
  - **Role:** Student
  - **Path:** `/seim/applications/<id>`
  - **Steps:** Open the same application.
  - **Expected:** Detail shows **approved**.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

---

## 9. Permission and a11y smoke (`roles`, `vue-portal`, `settings-ui`)

Short pass only. **Do not** treat a full WCAG audit as required (that remains P2 / N/A).

### 9.1 Wrong-role URLs (`roles`)

- [ ] **Cold URL matrix**
  - **Role:** Student, Coordinator, Partner (logout between)
  - **Path:** `/seim/review-queue`, `/seim/admin/programs`, `/seim/partner`, `/seim/nominations`, `/seim/eligibility-rulesets`
  - **Steps:** As **student**, open each path. As **coordinator**, open `/seim/admin/programs` and `/seim/partner`. As **partner**, open `/seim/review-queue` and `/seim/admin/programs`.
  - **Expected:** Each wrong-role hit redirects or denies. No staff/admin/partner chrome for the wrong role.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 9.2 Skip link and main landmark (`vue-portal`)

- [ ] **Skip to `#main-content`**
  - **Role:** Student (or anonymous on login)
  - **Path:** `/seim/login` then `/seim/dashboard`
  - **Steps:** Tab until “Skip to main” (or equivalent). Activate it. Confirm focus moves to `#main-content`.
  - **Expected:** Skip link in `App.vue` targets `#main-content`. Main landmark exists and can take focus.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 9.3 Focus ring (`vue-portal`)

- [ ] **`:focus-visible`**
  - **Role:** Student
  - **Path:** `/seim/dashboard`
  - **Steps:** Keyboard-tab through navbar, sidebar, and a primary button. Optionally enable high contrast in Settings and tab again.
  - **Expected:** Visible focus rings. Stronger in high contrast. Not a full audit.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

### 9.4 Locale on Login + inner page (`settings-ui`, `auth-api`)

- [ ] **en / es smoke**
  - **Role:** Anonymous, then Student
  - **Path:** `/seim/login`, then `/seim/applications`
  - **Steps:** On Login, switch locale if a control exists; otherwise login, set **es** in Settings, logout, confirm Login strings, login, open Applications in **es**, then restore **en**.
  - **Expected:** Login and one inner page show Spanish strings (or a documented fallback). No broken keys like `route.names.*` raw.
  - **Result:** `Pass` / `Fail` / `Blocked`
  - **Evidence notes:**

---

## Session sign-off (fill later)

| Field | Value |
|-------|-------|
| Date | |
| Base URL | `http://localhost:8020` |
| Compose project | `seim-localprod` |
| Seed | `create_initial_data` + `seed_demo_readiness` (yes/no) |
| Tester | |
| Clusters completed | |
| New `MQ-*` IDs | |
| Blockers | |

After execute: copy outcomes into [`feature-test-tracking.md`](feature-test-tracking.md) Notes; file defects in [`manual-qa-issues.md`](manual-qa-issues.md); optional narrative in [`manual-workflow-qa-session-log.md`](manual-workflow-qa-session-log.md). Follow [`prompts/manual-feature-workflow-test-loop-prompt.md`](prompts/manual-feature-workflow-test-loop-prompt.md).
