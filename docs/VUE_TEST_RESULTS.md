# Vue UI Test Results

**Date:** 2026-01-31 (updated: expanded coverage with role-based and mobile tests)  
**Environment:** Vue dev server `http://localhost:5173`, Django API `http://localhost:8001`  
**Test user:** student@test.com / student123  

> This file is the canonical Vue testing summary and supersedes the earlier narrower snapshot previously kept in `docs/VUE_MANUAL_TEST_RESULTS.md`.

---

## 1. Playwright E2E (Automated)

**Suite:** `tests/e2e_playwright/test_vue_ui.py`  
**Command:** From repo root (API and Vue dev server running):

Option A — seed in container then run tests (recommended):
```powershell
make vue-e2e
```
Or manually: `docker compose exec web python manage.py seed_vue_e2e` then:
```powershell
$env:BASE_URL="http://localhost:5173"; $env:API_URL="http://localhost:8001"
python -m pytest tests/e2e_playwright/test_vue_ui.py -v -m "vue" --browser=chromium
```

Option B — host-run seed (when DB is reachable from host):
```powershell
$env:RUN_SEED_VUE_E2E="1"; $env:BASE_URL="http://localhost:5173"; $env:API_URL="http://localhost:8001"
python -m pytest tests/e2e_playwright/test_vue_ui.py -v -m "vue" --browser=chromium
```
**Seed:** Use `make vue-e2e-seed` (or `docker compose exec web python manage.py seed_vue_e2e`) to seed inside the web container so programs, draft application, document, and unread notifications exist. Draft-dependent tests call `ensure_draft_application_via_api` and wait for the applications list to show a draft (up to 10s) after filtering.  
**Throttle:** If you get `429 Request was throttled`, start the API with throttle disabled for E2E:  
`$env:DISABLE_THROTTLE_E2E="1"; python manage.py runserver 8001` (or set in docker-compose for the web service).

| Test | Result | Notes |
|------|--------|--------|
| test_login_page_loads | PASSED | Login page shows email, password, Sign In |
| test_login_with_credentials | PASSED | Email/password → redirect to dashboard |
| test_profile_page_after_login | PASSED | Profile page shows Language, Language level |
| test_profile_save_language_proficiency | PASSED | Set Language + A2, save, no error |
| test_applications_list_after_login | PASSED | My Applications list visible |
| test_new_application_page_loads | PASSED | New application form with program select |
| test_create_application_submit | PASSED | Select program, submit → redirect to detail or eligibility alert |
| test_documents_list_after_login | PASSED | Documents page and heading visible |
| test_notifications_list_after_login | PASSED | Notifications page and heading visible |
| test_application_detail_from_list | PASSED | From list, click View Details → application detail page |
| test_document_detail_from_list | SKIPPED | From list, click view → document detail (skips if no documents) |
| test_dashboard_content_after_login | PASSED | Dashboard shows Welcome and sidebar Applications link |
| test_logout_redirects_to_login | PASSED | Logout clears token and shows login page |
| test_edit_application_from_detail | SKIPPED | From detail, Edit → edit form with program disabled (skips if first app not draft) |
| test_notifications_page_has_content | PASSED | Notifications page has list, empty state, or Mark All as Read |
| test_not_found_shows_404 | PASSED | Unknown route shows 404 and Go to Dashboard link |
| test_go_to_dashboard_from_404 | PASSED | From 404, Go to Dashboard → dashboard |
| test_sidebar_applications_navigation | PASSED | Dashboard sidebar Applications → applications list |
| test_sidebar_documents_navigation | PASSED | Dashboard sidebar Documents → documents list |
| test_sidebar_notifications_navigation | PASSED | Dashboard sidebar Notifications → notifications list |
| test_applications_filters_visible | PASSED | Applications list shows search, status, ordering filters |
| test_applications_filter_by_status_draft | PASSED | Status filter Draft updates list without error |
| test_application_form_cancel_goes_to_applications | PASSED | Cancel from new application form → applications list |
| test_application_detail_draft_shows_edit_and_submit | PASSED / SKIPPED | Draft detail shows Edit Application and Submit (skips if first app not draft) |
| test_documents_filters_visible | PASSED | Documents page shows Application, Document Type, Status, Clear |
| test_notifications_filter_by_unread | PASSED | Notifications Status filter Unread updates list |
| test_notifications_mark_all_read_click_when_unread | PASSED / SKIPPED | Mark All as Read click when unread (skips if no unread) |
| test_capture_key_pages | PASSED | Captures vue-01-login … vue-08-404; vue-09/10 when apps exist |
| test_login_invalid_credentials_shows_error | PASSED | Wrong password → alert-danger, stay on login |
| test_save_draft_from_new_form | PASSED | Select program, Save as Draft → detail or list, no error |
| test_application_detail_back_to_list | PASSED | From detail, Back to List → applications list |
| test_application_detail_delete_draft_redirects | SKIPPED | Confirm Delete from draft detail → applications (skips if no draft) |
| test_applications_search_input_no_error | PASSED | Type in search (debounced), no alert |
| test_applications_clear_filters_click | PASSED | Set status filter, Clear → list still loads |
| test_dashboard_profile_link_goes_to_profile | PASSED | User dropdown → Profile → profile page |
| test_notifications_mark_one_read_click | SKIPPED | Click first Mark as Read (skips if none) |
| test_documents_clear_filters_click | PASSED | Clear filters on documents page |
| test_notifications_clear_filters_click | PASSED | Clear Filters on notifications page |
| test_coordinator_login_and_dashboard | PASSED | Coordinator can login and see dashboard |
| test_coordinator_can_view_applications | PASSED | Coordinator can view applications list |
| test_admin_login_and_dashboard | PASSED | Admin can login and see dashboard |
| test_admin_can_view_applications | PASSED | Admin can view applications list |
| test_submit_draft_application | SKIPPED | Submit from draft detail (skips if no draft) |
| test_document_upload_form_visible_on_draft | SKIPPED | Upload form visible on draft detail (skips if no draft) |
| test_mobile_login_page | PASSED | Login at mobile viewport (375×667) + screenshot |
| test_mobile_dashboard | PASSED | Dashboard at mobile viewport + screenshot |
| test_mobile_applications | PASSED | Applications at mobile viewport + screenshot |
| test_upload_document_from_draft_detail | PASSED / SKIP | Select type, attach sample.pdf, upload (skips if no types or no fixture) |
| test_mobile_profile | PASSED | Profile at mobile viewport + screenshot |
| test_mobile_documents | PASSED | Documents at mobile viewport + screenshot |

**Summary:** With `RUN_SEED_VUE_E2E=1`, most tests pass and skips are minimized (draft-dependent tests use `ensure_draft_application_via_api` when no draft exists; seed provides programs, document, and unread notifications). (Vue dev server + Chromium). Run `seed_vue_e2e` first to reduce skips (draft app, document, unread notifications). Run `test_capture_key_pages` for visuals. With `DISABLE_THROTTLE_E2E=1` on the API, all non-skipped tests pass.

---

## 2. Visuals (Playwright or MCP Browser)

**Playwright (recommended):** Run the visual-capture test to save screenshots to `tests/e2e_playwright/screenshots/`:

```powershell
$env:BASE_URL="http://localhost:5173"; $env:API_URL="http://localhost:8001"
python -m pytest tests/e2e_playwright/test_vue_ui.py::TestVueVisualCapture::test_capture_key_pages -v --browser=chromium
```

| Screenshot | Page |
|------------|------|
| vue-01-login.png | Login (unauthenticated) |
| vue-02-dashboard.png | Dashboard after JWT login |
| vue-03-applications.png | My Applications list |
| vue-04-new-application.png | New application form |
| vue-05-profile.png | Profile (language / level) |
| vue-mobile-01-login.png | Login (mobile 375×667) |
| vue-mobile-02-dashboard.png | Dashboard (mobile viewport) |
| vue-mobile-03-applications.png | Applications (mobile viewport) |
| vue-mobile-04-profile.png | Profile (mobile viewport) |
| vue-mobile-05-documents.png | Documents (mobile viewport) |
| vue-06-documents.png | Documents list |
| vue-07-notifications.png | Notifications list |
| vue-08-404.png | 404 (unknown route) |
| vue-09-application-detail.png | Application detail (when at least one application exists) |
| vue-10-application-edit.png | Edit application form (when first application is draft) |

**MCP Browser (cursor-ide-browser):** Same flows; screenshots saved under `%TEMP%\cursor\screenshots\` (e.g. `vue-applications.png`).

---

## 3. API Checks (Prior Session)

| Check | Result |
|-------|--------|
| GET /api/accounts/profile/ | 200, includes language_level |
| PATCH /api/accounts/profile/ (language, language_level) | 200, profile updated |
| POST /api/applications/ (program ID, student from JWT) | 201, application created (with profile German A2) |
| Eligibility 400 | Application create returns 400 with program eligibility messages when profile does not meet program requirements |

---

## 4. Coverage Summary

- **Auth:** Login (email/password), JWT, redirect to dashboard.
- **Profile:** Load, edit Language + Language level (CEFR), save.
- **Applications:** List, filters, new application form (program select, optional statement, actions), **create application submit** (select program → redirect to detail or eligibility alert).
- **Documents:** List page loads with heading and filters.
- **Notifications:** List page loads with heading and filters.
- **Application detail:** From applications list, View Details → application detail page (program info, status, actions).
- **Document detail:** From documents list, view link → document detail page (skips if no documents).
- **Dashboard:** Welcome heading and sidebar links (Applications, Documents, Notifications).
- **Logout:** User dropdown → Logout → login page and token cleared.
- **Edit application:** From application detail (draft), Edit → edit form with program disabled (skips if first app not draft).
- **Notifications actions:** Page has Mark All as Read when unread, or list, or empty state; per-item Mark as Read.
- **404:** Unknown route shows 404 page and Go to Dashboard link; link navigates to dashboard.
- **Sidebar navigation:** Dashboard sidebar links → Applications, Documents, Notifications lists.
- **Applications filters:** Search, status (e.g. Draft), and ordering visible and applied without error.
- **Application form Cancel:** From new application form, Cancel link → applications list.
- **Application detail (draft):** Edit Application and Submit Application buttons visible on draft detail (skips if first app not draft).
- **Documents filters:** Application, Document Type, Status, and Clear visible on documents page.
- **Notifications filters:** Status filter (e.g. Unread) and Mark All as Read (when unread) tested; Mark All as Read click (skips if no unread).
- **Visual capture:** One test (`test_capture_key_pages`) navigates login → dashboard → applications → new application → profile → documents → notifications → 404 and optionally application detail + edit form; saves full-page screenshots (vue-01 … vue-10 when data exists).
- **Login validation:** Invalid credentials show `.alert-danger` and stay on login.
- **Save as Draft:** New application form → select program → Save as Draft → redirect to detail or list, no error.
- **Application detail:** Back to List → applications list; Delete (draft) with confirm dialog → applications (skips if no draft).
- **Applications:** Search input (debounced), Clear filters after setting status.
- **Dashboard:** User dropdown → Profile link → profile page.
- **Notifications / Documents:** Clear filters click; Mark one as read (skips if no per-item button).
- **Eligibility:** Backend returns 400 with structured program errors; Vue shows alert with bullet list (`data-testid=eligibility-alert`).

**Stable selectors (data-testid):** `program-select`, `create-application-btn`, `save-draft-btn`, `cancel-link`, `eligibility-alert` (ApplicationForm); `documents-page`, `documents-heading`, `document-detail-link` (Documents); `notifications-page`, `notifications-heading`, `mark-all-read-btn`, `mark-read-btn` (Notifications); `application-detail-page`, `application-detail-link`, `edit-application-link`, `submit-application-btn` (ApplicationDetail, Applications); `document-detail-page` (DocumentDetail); `dashboard-page`, `logout-link` (Dashboard); `not-found-page`, `go-to-dashboard-link` (NotFound).

---

## 5. How to Re-run

1. **Backend:** `docker compose up -d` (API on 8001). To avoid 429 throttle during E2E, run API with `DISABLE_THROTTLE_E2E=1` (in docker-compose).
2. **Seed (for previously skipped tests):** Run `docker compose exec web python manage.py seed_vue_e2e` to create a draft application, one document, and unread notifications for student@test.com. Then document-detail, edit-from-detail, draft-actions, delete-draft, mark-all-read, and mark-one-read tests can run.
3. **Vue:** `cd frontend-vue && npm run dev` (dev server on 5173).
4. **Playwright:** From repo root, set `BASE_URL=http://localhost:5173`, `API_URL=http://localhost:8001`, run pytest as above. JWT tokens are cached per run to reduce API calls.
5. **Visuals:** Run `TestVueVisualCapture::test_capture_key_pages` to save vue-01 … vue-10 to `tests/e2e_playwright/screenshots/` (replicates MCP browser flow).
6. **MCP browser:** In Cursor Composer, use cursor-ide-browser: navigate, lock, fill/click/snapshot/screenshot, unlock.
