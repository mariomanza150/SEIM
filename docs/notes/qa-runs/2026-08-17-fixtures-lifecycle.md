# Manual QA — fixtures + Section 8 lifecycle — 2026-08-17

**Date:** 2026-08-17  
**App:** `http://localhost:8020`  
**Stack:** Compose project `seim-localprod` (`docker-compose.local-prod.yml`)  
**Did not:** commit  

Student and coordinator used **isolated Playwright browser contexts** (separate storage). IDE-browser MCP had no tab; Puppeteer MCP Chrome 131 was missing (Chrome 152 installed later, unused).

## Seed artifacts

`seed_demo_readiness` inside `seim-web-local-prod` after copying updated `exchange/demo_seed.py` + `seed_demo_readiness.py`. Coordinator remains `is_email_verified=True`, `is_admin=False`, `is_staff=True`.

| Fixture | Name / id | Status |
|---------|-----------|--------|
| Closed window | **DEMO-SEED Closed Window - University of Oslo** `82d98b92-6e4e-4d70-9468-626e9cc8c1ee` | Active, window closed (`open` 2026-05-19, `deadline` 2026-08-03). No student application. |
| Submit gate | **DEMO-SEED Submit Gate - University of Lisbon** app `dd987b81-8740-4c84-b25b-d527a9212c36` | Student draft. transcript + passport uploaded, `is_valid=False`. |
| Resubmit | **DEMO-SEED Resubmit - University of Vienna** app `0e4c6efc-206a-4bb6-a203-c569a542a0de` | Student submitted. Open `DocumentResubmissionRequest` on passport. |
| §8 reserved | **DEMO-SEED Lifecycle - University of Porto** `7b86298b-9b47-44f7-b165-c2acd9e56bd6` | Open window. Seed creates **no** student application. |

Existing Fulbright / DAAD / Erasmus rows were not used for §8.

## Product changes (this session)

- Catalog filter `eligible_for_me` no longer hides closed-window programs (window is `accepting_applications`). Needed so 2.8 is selectable.
- Seed recreates the four DEMO-SEED fixtures above (idempotent).
- `DocumentUpload` loads all document-type pages (`page_size=100` + `next`). Default PAGE_SIZE 20 dropped `transcript` / `passport` off page 1.
- `POST /api/documents/{id}/validate_document/` (and other staff application mutations) call `invalidate_application_api_responses()` so student detail is not left on a cached pre-mutation payload.

Vue dist was rebuilt on the host and copied into `seim-web-local-prod` (then container restart / collectstatic).

## Fixture retest

| ID | Result | Evidence |
|----|--------|----------|
| **2.8** Closed window | **Pass** | `/seim/applications/new` → select Oslo. Alert “Applications closed on August 03, 2026.” Create + Save draft **disabled**. Screenshot `2.8-closed-window.png`. API: `eligible_for_me=true` includes the program, `application_window_open=false`. |
| **3.4** Resubmit | **Pass** | Vienna app checklist: passport `resubmit_requested`. Document detail replace-file uploaded. Screenshots `3.4-resubmit-checklist.png`, `3.4-document-detail.png`, `3.4-after-replace.png`. |
| **3.5** Submit gate | **Pass** | Lisbon draft: Submit disabled, title “Required documents must be approved first”, 0/2 approved, both pending review. Screenshot `3.5-submit-gate.png`. `POST .../submit/` **400** `Required documents are not all approved yet: transcript (pending_review); passport (pending_review)`. Gate not weakened. |

## Section 8 — Lifecycle Porto

New draft **`bb40c56f-3cc2-447d-b87b-68dc4de6da64`** for `student@test.com` (not Fulbright/DAAD).

| ID | Result | Evidence |
|----|--------|----------|
| **8.1** Draft | **Pass** | Save draft → `/seim/applications/bb40c56f-3cc2-447d-b87b-68dc4de6da64`. Screenshot `8.1-lifecycle-draft.png`. |
| **8.2** Upload | **Pass** | Checklist pending review for transcript + passport (`8.2-uploaded.png`). First UI upload attempt timed out: type dropdown used first 20 types only (**MQ-2026-08-17-001**, fixed). Files attached with the student JWT (`POST /api/documents/` 201) then verified in the SPA. |
| **8.3** Submit | **Pass** | UI Submit stayed disabled until staff `is_valid=True` (`8.3-gate`). Coordinator mark-valid controls clicked (`8.3b-coordinator-validate.png`). `POST .../submit/` **200** `Application submitted successfully` after docs valid. UI button lagged on a cached checklist until cache clear — gate itself still 400 on the Lisbon fixture. |
| **8.4** Coord comment | **Pass** | Public comment posted on the lifecycle app. `8.4-public-comment.png`. |
| **8.5** Student update | **Pass** | Student detail/inbox showed the coordinator activity. `8.5-student-notifications.png`. |
| **8.6** Approve | **Pass** | Coordinator `PATCH` status **approved** 200. Isolated coordinator browser: detail shows approved (`8.6-coordinator-approved.png`). |
| **8.7** Student approved | **Pass** | After `CacheManager.clear_pattern('api_resp:*')`, student GET `status=approved`, headline “Application approved.” Playwright body contains approved (`8.7-student-approved.png`). **Retest (MQ-002):** targeted invalidate — coordinator comment `1dbaf5d1-…` visible on student `GET /api/comments/` immediately (2→3); Porto status `approved`→`under_review`→`approved` student GET/headline matched without TTL or pattern clear. |

## Tests

- `tests/unit/exchange/test_exchange_management_commands_seed_demo_readiness.py` + catalog filter test: **4 passed** (`seime2e-web-1`).
- Vitest `DocumentUpload.spec.js`: **2 passed** (`--pool=threads`).
- Cache regression (`seime2e-web-1`): `test_student_get_sees_staff_status_and_comment_after_cache` + `test_invalidate_application_api_responses_increments_generation` + `test_application_viewset_cache_keys.py` — **8 passed**.

## New issues

See [`manual-qa-issues.md`](../manual-qa-issues.md): **MQ-2026-08-17-001** (fixed), **MQ-2026-08-17-002** (fixed — student GET after staff comment/status no longer needs `api_resp:*` clear).
