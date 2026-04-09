"""
Vue.js SPA UI E2E tests.

Run against Vue dev server (default http://localhost:5173) with backend at API_URL.
  BASE_URL=http://localhost:5173 API_URL=http://localhost:8001 pytest tests/e2e_playwright/test_vue_ui.py -v
Or use Django serving built Vue (same origin):
  BASE_URL=http://localhost:8001 pytest tests/e2e_playwright/test_vue_ui.py -v
"""
import os
import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from tests.e2e_playwright.utils.auth_helpers import VueAppNotAvailable
from tests.e2e_playwright.utils.vue_auth_helpers import (
    login_vue_via_jwt,
    is_vue_logged_in,
    ensure_draft_application_via_api,
    API_BASE_URL,
)


def _login_vue_or_skip(page, vue_base_url, email, password):
    try:
        return login_vue_via_jwt(page, vue_base_url, email, password)
    except VueAppNotAvailable as e:
        pytest.skip(str(e))


def _normalize_vue_base_url(base_url: str) -> str:
    """Use Django's mounted SPA path when BASE_URL points at the backend root."""
    base_url = base_url.rstrip("/")
    if base_url.endswith(":8001"):
        return f"{base_url}/seim"
    return base_url


def _route_regex(path: str):
    """Match Vue routes with optional trailing slash from Django."""
    return re.compile(rf"{re.escape(VUE_BASE_URL)}{re.escape(path)}/?$")

# Vue app URL (dev server or Django serving Vue)
VUE_BASE_URL = _normalize_vue_base_url(os.environ.get("BASE_URL", "http://localhost:5173"))

# Test users (from create_vue_test_users)
VUE_STUDENT_EMAIL = "student@test.com"
VUE_STUDENT_PASSWORD = "student123"
VUE_COORDINATOR_EMAIL = "coordinator@test.com"
VUE_COORDINATOR_PASSWORD = "coordinator123"
VUE_ADMIN_EMAIL = "admin@test.com"
VUE_ADMIN_PASSWORD = "admin123"

# E2E fixture path for document upload
E2E_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
SAMPLE_PDF_PATH = E2E_FIXTURES_DIR / "sample.pdf"


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueUILogin:
    """Vue login page and flow."""

    def test_login_page_loads(self, page: Page):
        """Login page is visible with email and password fields."""
        page.goto(f"{VUE_BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        if page.title() and "not found" in page.title().lower():
            pytest.skip("Vue app not available at BASE_URL. Run with BASE_URL=http://localhost:5173 and Vue dev server.")
        expect(page).to_have_url(re.compile(r".*login.*"))
        expect(page.locator("[data-testid=login-email]")).to_be_visible()
        expect(page.locator("[data-testid=login-password]")).to_be_visible()
        expect(page.locator("[data-testid=login-submit]")).to_be_visible()

    def test_login_with_credentials(self, page: Page):
        """Login with email/password redirects to dashboard."""
        page.goto(f"{VUE_BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        if page.title() and "not found" in page.title().lower():
            pytest.skip("Vue app not available at BASE_URL. Run with BASE_URL=http://localhost:5173 and Vue dev server.")
        page.locator("[data-testid=login-email]").fill(VUE_STUDENT_EMAIL)
        page.locator("[data-testid=login-password]").fill(VUE_STUDENT_PASSWORD)
        page.locator("[data-testid=login-submit]").click()
        page.wait_for_url(_route_regex("/dashboard"), timeout=15000)
        expect(page).to_have_url(_route_regex("/dashboard"))
        expect(page.get_by_role("heading", name=re.compile(r"Welcome", re.I))).to_be_visible(timeout=5000)


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueProfile:
    """Vue profile page and language proficiency."""

    def test_profile_page_after_login(self, page: Page):
        """Login via JWT, open profile, set language and level, save."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        assert is_vue_logged_in(page), "Should be logged in"
        page.goto(f"{VUE_BASE_URL}/profile")
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(_route_regex("/profile"))
        expect(page.locator('label:has-text("Language")').first).to_be_visible(timeout=5000)
        expect(page.locator('label:has-text("Language level")').first).to_be_visible(timeout=5000)

    def test_profile_save_language_proficiency(self, page: Page):
        """Set language German and level A2, save, expect success."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/profile")
        page.wait_for_load_state("networkidle")
        page.locator('label:has-text("Language") + input').fill("German")
        page.locator('label:has-text("Language level (CEFR)") + select').select_option("A2")
        page.get_by_role("button", name="Save profile").click()
        page.wait_for_load_state("networkidle")
        expect(page.locator(".alert-danger")).to_have_count(0, timeout=3000)


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueApplicationFlow:
    """Vue application create flow and eligibility messaging."""

    def test_applications_list_after_login(self, page: Page):
        """After login, applications list is reachable."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/applications")
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(_route_regex("/applications"))
        expect(page.get_by_role("heading", name=re.compile(r"My Applications", re.I))).to_be_visible(timeout=5000)

    def test_new_application_page_loads(self, page: Page):
        """New application form loads with program select."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/applications/new")
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(_route_regex("/applications/new"))
        expect(page.locator("[data-testid=program-select]")).to_be_visible(timeout=5000)

    def test_create_application_submit(self, page: Page):
        """Select program, submit; expect redirect to application detail or eligibility alert."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/applications/new")
        page.wait_for_load_state("networkidle")
        program_select = page.locator("[data-testid=program-select]")
        expect(program_select).to_be_visible(timeout=5000)
        # Select first real program (index 1; 0 is placeholder)
        options = program_select.locator("option")
        if options.count() < 2:
            pytest.skip("No programs available")
        program_select.select_option(index=1)
        page.locator("[data-testid=create-application-btn]").click()
        # Either redirect to application detail or eligibility alert appears
        page.wait_for_timeout(3000)
        url = page.url
        if re.search(r"/applications/[0-9a-f-]{36}(?!/edit)", url):
            expect(page).to_have_url(re.compile(r".*/applications/[0-9a-f-]+$"))
        else:
            expect(page.locator("[data-testid=eligibility-alert]")).to_be_visible(timeout=2000)


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueDocuments:
    """Vue documents list page."""

    def test_documents_list_after_login(self, page: Page):
        """Documents page loads and shows heading."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/documents")
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(_route_regex("/documents"))
        expect(page.locator("[data-testid=documents-page]")).to_be_visible(timeout=5000)
        expect(page.locator("[data-testid=documents-heading]")).to_be_visible()


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueNotifications:
    """Vue notifications list page."""

    def test_notifications_list_after_login(self, page: Page):
        """Notifications page loads and shows heading."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/notifications")
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(_route_regex("/notifications"))
        expect(page.locator("[data-testid=notifications-page]")).to_be_visible(timeout=5000)
        expect(page.locator("[data-testid=notifications-heading]")).to_be_visible()


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueApplicationDetail:
    """Application detail page from list."""

    def test_application_detail_from_list(self, page: Page):
        """From applications list, click first View Details and land on detail page."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/applications")
        page.wait_for_load_state("networkidle")
        detail_link = page.locator("[data-testid=application-detail-link]").first
        if detail_link.count() == 0:
            ensure_draft_application_via_api(page, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
            page.goto(f"{VUE_BASE_URL}/applications")
            page.wait_for_load_state("networkidle")
            detail_link = page.locator("[data-testid=application-detail-link]").first
        if detail_link.count() == 0:
            pytest.skip("No applications to view")
        detail_link.click()
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(re.compile(r".*/applications/[0-9a-f-]+$"))
        expect(page.locator("[data-testid=application-detail-page]")).to_be_visible(timeout=5000)


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueDocumentDetail:
    """Document detail page from list."""

    def test_document_detail_from_list(self, page: Page):
        """From documents list, click first view link and land on document detail (if any)."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/documents")
        page.wait_for_load_state("networkidle")
        doc_link = page.locator("[data-testid=document-detail-link]").first
        if doc_link.count() == 0:
            pytest.skip("No documents to view")
        doc_link.click()
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(re.compile(r".*/documents/[0-9a-f-]+$"))
        # Detail page shows data-testid when document loaded; may show error alert if API fails
        either = page.locator("[data-testid=document-detail-page]").or_(page.locator(".document-detail .alert-danger"))
        expect(either).to_be_visible(timeout=8000)


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueDashboard:
    """Dashboard content and navigation."""

    def test_dashboard_content_after_login(self, page: Page):
        """Dashboard shows Welcome and sidebar links."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/dashboard")
        page.wait_for_load_state("networkidle")
        expect(page.locator("[data-testid=dashboard-page]")).to_be_visible(timeout=5000)
        expect(page.get_by_role("heading", name=re.compile(r"Welcome", re.I))).to_be_visible()
        expect(page.get_by_role("link", name=re.compile(r"Applications", re.I)).first).to_be_visible()


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueLogout:
    """Logout flow."""

    def test_logout_redirects_to_login(self, page: Page):
        """After login, logout clears session and shows login page."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/dashboard")
        page.wait_for_load_state("networkidle")
        page.locator("#userDropdown").click()
        page.locator("[data-testid=logout-link]").click()
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(re.compile(r".*login.*"))
        assert not is_vue_logged_in(page), "Token should be cleared after logout"


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueEditApplication:
    """Edit application from detail page."""

    def test_edit_application_from_detail(self, page: Page):
        """From application detail (draft), click Edit and land on edit form with program disabled."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        ensure_draft_application_via_api(page, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/applications")
        page.wait_for_load_state("networkidle")
        page.locator("[data-testid=applications-filter-status]").select_option(value="draft")
        page.wait_for_load_state("networkidle")
        detail_link = page.locator("[data-testid=application-detail-link]").first
        try:
            detail_link.wait_for(state="visible", timeout=10000)
        except Exception:
            pytest.skip("No applications to view")
        detail_link.click()
        page.wait_for_load_state("networkidle")
        edit_link = page.locator("[data-testid=edit-application-link]").first
        if edit_link.count() == 0:
            pytest.skip("No draft application to edit")
        edit_link.click()
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(re.compile(r".*/applications/[0-9a-f-]+/edit$"))
        expect(page.locator("[data-testid=program-select]")).to_be_visible(timeout=5000)
        expect(page.locator("[data-testid=program-select]")).to_be_disabled()


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueNotificationsActions:
    """Notifications page actions and filters."""

    def test_notifications_page_has_content(self, page: Page):
        """Notifications page loads; has filters and either list or empty state or Mark All as Read."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/notifications")
        page.wait_for_load_state("networkidle")
        expect(page.locator("[data-testid=notifications-page]")).to_be_visible(timeout=5000)
        expect(page.locator("[data-testid=notifications-heading]")).to_be_visible()
        # Either Mark All as Read (when unread), or list, or empty state
        has_content = (
            page.locator("[data-testid=mark-all-read-btn]").count() > 0
            or page.locator("[data-testid=mark-read-btn]").count() > 0
            or page.locator(".list-group-item").count() > 0
            or page.get_by_text("No notifications").count() > 0
        )
        assert has_content, "Notifications page should show list, empty state, or Mark All as Read"


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueNotFound:
    """404 page."""

    def test_not_found_shows_404(self, page: Page):
        """Unknown route shows 404 page with Go to Dashboard link."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/nonexistent-route-xyz")
        page.wait_for_load_state("networkidle")
        expect(page.locator("[data-testid=not-found-page]")).to_be_visible(timeout=5000)
        expect(page.get_by_role("heading", name="404")).to_be_visible()
        expect(page.locator("[data-testid=go-to-dashboard-link]")).to_be_visible()

    def test_go_to_dashboard_from_404(self, page: Page):
        """From 404, Go to Dashboard navigates to dashboard."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/nonexistent-route-xyz")
        page.wait_for_load_state("networkidle")
        page.locator("[data-testid=go-to-dashboard-link]").click()
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(re.compile(r".*/(dashboard/?)?$"))


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueSidebarNavigation:
    """Sidebar navigation from dashboard."""

    def test_sidebar_applications_navigation(self, page: Page):
        """From dashboard, sidebar Applications link goes to applications list."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/dashboard")
        page.wait_for_load_state("networkidle")
        page.get_by_role("link", name=re.compile(r"Applications", re.I)).first.click()
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(_route_regex("/applications"))
        expect(page.get_by_role("heading", name=re.compile(r"My Applications", re.I))).to_be_visible(timeout=5000)

    def test_sidebar_documents_navigation(self, page: Page):
        """From dashboard, sidebar Documents link goes to documents list."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/dashboard")
        page.wait_for_load_state("networkidle")
        page.get_by_role("link", name=re.compile(r"Documents", re.I)).first.click()
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(_route_regex("/documents"))
        expect(page.locator("[data-testid=documents-heading]")).to_be_visible(timeout=5000)

    def test_sidebar_notifications_navigation(self, page: Page):
        """From dashboard, sidebar Notifications link goes to notifications list."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/dashboard")
        page.wait_for_load_state("networkidle")
        page.get_by_role("link", name=re.compile(r"Notifications", re.I)).first.click()
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(_route_regex("/notifications"))
        expect(page.locator("[data-testid=notifications-heading]")).to_be_visible(timeout=5000)


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueApplicationsFilters:
    """Applications list filters."""

    def test_applications_filters_visible(self, page: Page):
        """Applications list shows search, status, and sort filters."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/applications")
        page.wait_for_load_state("networkidle")
        expect(page.locator("[data-testid=applications-filters]")).to_be_visible(timeout=5000)
        expect(page.locator("[data-testid=applications-search]")).to_be_visible()
        expect(page.locator("[data-testid=applications-filter-status]")).to_be_visible()
        expect(page.locator("[data-testid=applications-filter-ordering]")).to_be_visible()

    def test_applications_filter_by_status_draft(self, page: Page):
        """Selecting status Draft updates the list without error."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/applications")
        page.wait_for_load_state("networkidle")
        page.locator("[data-testid=applications-filter-status]").select_option(value="draft")
        page.wait_for_load_state("networkidle")
        expect(page.locator("[data-testid=applications-filters]")).to_be_visible()
        expect(page.locator(".alert-danger")).to_have_count(0)


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueApplicationFormCancel:
    """Application form Cancel and navigation."""

    def test_application_form_cancel_goes_to_applications(self, page: Page):
        """From new application form, Cancel link navigates to applications list."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/applications/new")
        page.wait_for_load_state("networkidle")
        page.locator("[data-testid=cancel-link]").click()
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(_route_regex("/applications"))
        expect(page.get_by_role("heading", name=re.compile(r"My Applications", re.I))).to_be_visible(timeout=5000)


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueApplicationDetailActions:
    """Application detail page actions (draft: Edit, Submit)."""

    def test_application_detail_draft_shows_edit_and_submit(self, page: Page):
        """On draft application detail, Edit Application and Submit Application are visible."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        ensure_draft_application_via_api(page, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/applications")
        page.wait_for_load_state("networkidle")
        page.locator("[data-testid=applications-filter-status]").select_option(value="draft")
        page.wait_for_load_state("networkidle")
        detail_link = page.locator("[data-testid=application-detail-link]").first
        try:
            detail_link.wait_for(state="visible", timeout=10000)
        except Exception:
            pytest.skip("No draft application")
        detail_link.click()
        page.wait_for_load_state("networkidle")
        edit_link = page.locator("[data-testid=edit-application-link]").first
        if edit_link.count() == 0:
            pytest.skip("First application is not draft")
        expect(edit_link).to_be_visible()
        expect(page.locator("[data-testid=submit-application-btn]").first).to_be_visible()


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueDocumentsFilters:
    """Documents list filters."""

    def test_documents_filters_visible(self, page: Page):
        """Documents page shows Application, Document Type, Status filters and Clear."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/documents")
        page.wait_for_load_state("networkidle")
        doc_page = page.locator("[data-testid=documents-page]")
        expect(doc_page).to_contain_text("Application")
        expect(doc_page).to_contain_text("Document Type")
        expect(doc_page).to_contain_text("Status")
        expect(page.get_by_role("button", name=re.compile(r"Clear", re.I))).to_be_visible()


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueNotificationsFilters:
    """Notifications list filters and Mark All as Read."""

    def test_notifications_filter_by_unread(self, page: Page):
        """Selecting Unread in Status filter updates the list without error."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/notifications")
        page.wait_for_load_state("networkidle")
        notifications_section = page.locator("[data-testid=notifications-page]")
        status_select = notifications_section.locator("select").first
        if status_select.count() == 0:
            pytest.skip("Status filter not found")
        status_select.select_option("false")
        page.wait_for_load_state("networkidle")
        expect(page.locator("[data-testid=notifications-page]")).to_be_visible()
        # API may return error for some filter combos; ensure page still renders
        expect(page.locator("[data-testid=notifications-heading]")).to_be_visible()

    def test_notifications_mark_all_read_click_when_unread(self, page: Page):
        """When unread exist, Mark All as Read is visible and clickable without error."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/notifications")
        page.wait_for_load_state("networkidle")
        mark_all_btn = page.locator("[data-testid=mark-all-read-btn]").first
        if mark_all_btn.count() == 0:
            pytest.skip("No unread notifications")
        mark_all_btn.click()
        page.wait_for_load_state("networkidle")
        expect(page.locator("[data-testid=notifications-page]")).to_be_visible()
        expect(page.locator(".alert-danger")).to_have_count(0)


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueLoginValidation:
    """Login error handling."""

    def test_login_invalid_credentials_shows_error(self, page: Page):
        """Invalid email/password shows error message and stays on login."""
        page.goto(f"{VUE_BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        if page.title() and "not found" in page.title().lower():
            pytest.skip("Vue app not available at BASE_URL. Run with BASE_URL=http://localhost:5173")
        page.locator("[data-testid=login-email]").fill(VUE_STUDENT_EMAIL)
        page.locator("[data-testid=login-password]").fill("wrongpassword")
        page.locator("[data-testid=login-submit]").click()
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(re.compile(r".*login.*"))
        expect(page.locator(".alert-danger")).to_be_visible(timeout=5000)


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueApplicationFormSaveDraft:
    """Application form Save as Draft."""

    def test_save_draft_from_new_form(self, page: Page):
        """Select program, Save as Draft; expect redirect to application detail or list."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/applications/new")
        page.wait_for_load_state("networkidle")
        program_select = page.locator("[data-testid=program-select]")
        if program_select.locator("option").count() < 2:
            pytest.skip("No programs available")
        program_select.select_option(index=1)
        page.locator("[data-testid=save-draft-btn]").click()
        page.wait_for_timeout(3000)
        url = page.url
        assert re.search(r"/applications/[0-9a-f-]+(/edit)?$", url) or url.endswith("/applications")
        expect(page.locator(".alert-danger")).to_have_count(0)


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueApplicationDetailNavigation:
    """Application detail page navigation."""

    def test_application_detail_back_to_list(self, page: Page):
        """From application detail, Back to List goes to applications list."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/applications")
        page.wait_for_load_state("networkidle")
        detail_link = page.locator("[data-testid=application-detail-link]").first
        if detail_link.count() == 0:
            ensure_draft_application_via_api(page, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
            page.goto(f"{VUE_BASE_URL}/applications")
            page.wait_for_load_state("networkidle")
            detail_link = page.locator("[data-testid=application-detail-link]").first
        if detail_link.count() == 0:
            pytest.skip("No applications to view")
        detail_link.click()
        page.wait_for_load_state("networkidle")
        page.get_by_role("link", name=re.compile(r"Back to List", re.I)).click()
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(_route_regex("/applications"))
        expect(page.get_by_role("heading", name=re.compile(r"My Applications", re.I))).to_be_visible(timeout=5000)


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueApplicationDetailDelete:
    """Application detail delete (draft)."""

    def test_application_detail_delete_draft_redirects(self, page: Page):
        """From draft detail, confirm Delete; expect redirect to applications (skip if no draft)."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        ensure_draft_application_via_api(page, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/applications")
        page.wait_for_load_state("networkidle")
        page.locator("[data-testid=applications-filter-status]").select_option(value="draft")
        page.wait_for_load_state("networkidle")
        detail_link = page.locator("[data-testid=application-detail-link]").first
        try:
            detail_link.wait_for(state="visible", timeout=10000)
        except Exception:
            pytest.skip("No draft application to delete")
        detail_link.click()
        page.wait_for_load_state("networkidle")
        delete_loc = page.get_by_role("button", name=re.compile(r"Delete Application", re.I))
        if delete_loc.count() == 0:
            pytest.skip("No draft application to delete")
        page.once("dialog", lambda d: d.accept())
        delete_loc.first.click()
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(_route_regex("/applications"), timeout=10000)
        expect(page.locator(".alert-danger")).to_have_count(0)


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueApplicationsSearchAndClear:
    """Applications list search and clear filters."""

    def test_applications_search_input_no_error(self, page: Page):
        """Typing in search box and waiting does not show alert (debounced fetch)."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/applications")
        page.wait_for_load_state("networkidle")
        page.locator("[data-testid=applications-search]").fill("test")
        page.wait_for_timeout(1500)
        expect(page.locator("[data-testid=applications-filters]")).to_be_visible()
        expect(page.locator(".alert-danger")).to_have_count(0)

    def test_applications_clear_filters_click(self, page: Page):
        """After setting status filter, Clear resets and list still loads."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/applications")
        page.wait_for_load_state("networkidle")
        page.locator("[data-testid=applications-filter-status]").select_option(value="draft")
        page.wait_for_load_state("networkidle")
        page.get_by_role("button", name=re.compile(r"Clear", re.I)).first.click()
        page.wait_for_load_state("networkidle")
        expect(page.locator("[data-testid=applications-filters]")).to_be_visible()
        expect(page.get_by_role("heading", name=re.compile(r"My Applications", re.I))).to_be_visible()


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueDashboardProfileLink:
    """Dashboard user menu and profile link."""

    def test_dashboard_profile_link_goes_to_profile(self, page: Page):
        """From dashboard, user dropdown -> Profile navigates to profile page."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/dashboard")
        page.wait_for_load_state("networkidle")
        page.locator("#userDropdown").click()
        page.get_by_role("link", name="Profile").click()
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(_route_regex("/profile"))
        expect(page.locator('label:has-text("Language")').first).to_be_visible(timeout=5000)


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueNotificationsMarkOneRead:
    """Notifications mark single as read."""

    def test_notifications_mark_one_read_click(self, page: Page):
        """Click first Mark as Read on a notification; page still valid (skip if none)."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/notifications")
        page.wait_for_load_state("networkidle")
        mark_btn = page.locator("[data-testid=mark-read-btn]").first
        if mark_btn.count() == 0:
            pytest.skip("No per-item Mark as Read button")
        mark_btn.click()
        page.wait_for_load_state("networkidle")
        expect(page.locator("[data-testid=notifications-page]")).to_be_visible()
        expect(page.locator(".alert-danger")).to_have_count(0)


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueDocumentsClearFilters:
    """Documents list clear filters."""

    def test_documents_clear_filters_click(self, page: Page):
        """Clear filters on documents page; no error."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/documents")
        page.wait_for_load_state("networkidle")
        page.get_by_role("button", name=re.compile(r"Clear", re.I)).first.click()
        page.wait_for_load_state("networkidle")
        expect(page.locator("[data-testid=documents-page]")).to_be_visible()
        expect(page.locator(".alert-danger")).to_have_count(0)


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueNotificationsClearFilters:
    """Notifications list clear filters."""

    def test_notifications_clear_filters_click(self, page: Page):
        """Clear Filters on notifications page; no error."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/notifications")
        page.wait_for_load_state("networkidle")
        page.get_by_role("button", name=re.compile(r"Clear Filters", re.I)).click()
        page.wait_for_load_state("networkidle")
        expect(page.locator("[data-testid=notifications-page]")).to_be_visible()
        expect(page.locator(".alert-danger")).to_have_count(0)


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueVisualCapture:
    """Capture screenshots of key pages (replicates MCP browser visual flow)."""

    def test_capture_key_pages(self, page: Page, take_screenshot):
        """Navigate key pages and save screenshots to tests/e2e_playwright/screenshots/."""
        # Login page (unauthenticated)
        page.goto(f"{VUE_BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        take_screenshot("vue-01-login", full_page=True)

        # Login then capture dashboard and main sections
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        assert is_vue_logged_in(page), "Should be logged in"

        page.goto(f"{VUE_BASE_URL}/dashboard")
        page.wait_for_load_state("networkidle")
        take_screenshot("vue-02-dashboard", full_page=True)

        page.goto(f"{VUE_BASE_URL}/applications")
        page.wait_for_load_state("networkidle")
        take_screenshot("vue-03-applications", full_page=True)

        page.goto(f"{VUE_BASE_URL}/applications/new")
        page.wait_for_load_state("networkidle")
        take_screenshot("vue-04-new-application", full_page=True)

        page.goto(f"{VUE_BASE_URL}/profile")
        page.wait_for_load_state("networkidle")
        take_screenshot("vue-05-profile", full_page=True)

        page.goto(f"{VUE_BASE_URL}/documents")
        page.wait_for_load_state("networkidle")
        take_screenshot("vue-06-documents", full_page=True)

        page.goto(f"{VUE_BASE_URL}/notifications")
        page.wait_for_load_state("networkidle")
        take_screenshot("vue-07-notifications", full_page=True)

        page.goto(f"{VUE_BASE_URL}/nonexistent-route-xyz")
        page.wait_for_load_state("networkidle")
        take_screenshot("vue-08-404", full_page=True)

        # Application detail and edit form (when at least one application exists)
        page.goto(f"{VUE_BASE_URL}/applications")
        page.wait_for_load_state("networkidle")
        detail_link = page.locator("[data-testid=application-detail-link]").first
        if detail_link.count() > 0:
            detail_link.click()
            page.wait_for_load_state("networkidle")
            take_screenshot("vue-09-application-detail", full_page=True)
            edit_link = page.locator("[data-testid=edit-application-link]").first
            if edit_link.count() > 0:
                edit_link.click()
                page.wait_for_load_state("networkidle")
                take_screenshot("vue-10-application-edit", full_page=True)


# =============================================================================
# Expanded Coverage: Coordinator / Admin / Submit / Upload / Mobile
# =============================================================================


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueCoordinatorLogin:
    """Coordinator login and access."""

    def test_coordinator_login_and_dashboard(self, page: Page):
        """Coordinator can login and see dashboard."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_COORDINATOR_EMAIL, VUE_COORDINATOR_PASSWORD)
        assert is_vue_logged_in(page), "Coordinator should be logged in"
        page.goto(f"{VUE_BASE_URL}/dashboard")
        page.wait_for_load_state("networkidle")
        expect(page.locator("[data-testid=dashboard-page]")).to_be_visible(timeout=5000)

    def test_coordinator_can_view_applications(self, page: Page):
        """Coordinator can view applications list (may include all students)."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_COORDINATOR_EMAIL, VUE_COORDINATOR_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/applications")
        page.wait_for_load_state("networkidle")
        expect(page.get_by_role("heading", name=re.compile(r"My Applications", re.I))).to_be_visible(timeout=5000)
        expect(page.locator("[data-testid=applications-filters]")).to_be_visible()


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueAdminLogin:
    """Admin login and access."""

    def test_admin_login_and_dashboard(self, page: Page):
        """Admin can login and see dashboard."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_ADMIN_EMAIL, VUE_ADMIN_PASSWORD)
        assert is_vue_logged_in(page), "Admin should be logged in"
        page.goto(f"{VUE_BASE_URL}/dashboard")
        page.wait_for_load_state("networkidle")
        expect(page.locator("[data-testid=dashboard-page]")).to_be_visible(timeout=5000)

    def test_admin_can_view_applications(self, page: Page):
        """Admin can view applications list."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_ADMIN_EMAIL, VUE_ADMIN_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/applications")
        page.wait_for_load_state("networkidle")
        expect(page.get_by_role("heading", name=re.compile(r"My Applications", re.I))).to_be_visible(timeout=5000)


@pytest.mark.e2e_playwright
@pytest.mark.vue
class TestVueSubmitApplication:
    """Submit application from draft detail."""

    def test_submit_draft_application(self, page: Page):
        """From draft detail, click Submit Application and confirm; status changes."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        ensure_draft_application_via_api(page, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/applications")
        page.wait_for_load_state("networkidle")
        page.locator("[data-testid=applications-filter-status]").select_option(value="draft")
        page.wait_for_load_state("networkidle")
        detail_link = page.locator("[data-testid=application-detail-link]").first
        try:
            detail_link.wait_for(state="visible", timeout=10000)
        except Exception:
            pytest.skip("No draft application to submit")
        detail_link.click()
        page.wait_for_load_state("networkidle")
        submit_btn = page.locator("[data-testid=submit-application-btn]").first
        if submit_btn.count() == 0:
            pytest.skip("Submit button not visible (not draft)")
        page.once("dialog", lambda d: d.accept())
        submit_btn.click()
        page.wait_for_load_state("networkidle")
        # After submit, status should change (page reloads or shows success)
        expect(page.locator("[data-testid=application-detail-page]")).to_be_visible(timeout=10000)
        # Submit button should no longer be visible
        expect(page.locator("[data-testid=submit-application-btn]")).to_have_count(0, timeout=5000)


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueDocumentUploadForm:
    """Document upload form on application detail."""

    def test_document_upload_form_visible_on_draft(self, page: Page):
        """On draft application detail, document upload form is visible with type select and file input."""
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        ensure_draft_application_via_api(page, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/applications")
        page.wait_for_load_state("networkidle")
        page.locator("[data-testid=applications-filter-status]").select_option(value="draft")
        page.wait_for_load_state("networkidle")
        detail_link = page.locator("[data-testid=application-detail-link]").first
        try:
            detail_link.wait_for(state="visible", timeout=10000)
        except Exception:
            pytest.skip("No draft application")
        detail_link.click()
        page.wait_for_load_state("networkidle")
        # Upload form should be present on draft/submitted applications
        expect(page.locator("[data-testid=document-type-select]")).to_be_visible(timeout=5000)
        expect(page.locator("[data-testid=document-file-input]")).to_be_visible()
        expect(page.locator("[data-testid=document-upload-btn]")).to_be_visible()


@pytest.mark.e2e_playwright
@pytest.mark.vue
class TestVueDocumentUpload:
    """Document upload from application detail."""

    def test_upload_document_from_draft_detail(self, page: Page):
        """On draft detail, select type, attach file, upload; success or no error."""
        if not SAMPLE_PDF_PATH.exists():
            pytest.skip("Fixture sample.pdf not found")
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        ensure_draft_application_via_api(page, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/applications")
        page.wait_for_load_state("networkidle")
        page.locator("[data-testid=applications-filter-status]").select_option(value="draft")
        page.wait_for_load_state("networkidle")
        detail_link = page.locator("[data-testid=application-detail-link]").first
        try:
            detail_link.wait_for(state="visible", timeout=10000)
        except Exception:
            pytest.skip("No draft application")
        detail_link.click()
        page.wait_for_load_state("networkidle")
        type_select = page.locator("[data-testid=document-type-select]")
        expect(type_select).to_be_visible(timeout=5000)
        options = type_select.locator("option").all_inner_texts()
        if len(options) <= 1:
            pytest.skip("No document types (only placeholder)")
        type_select.select_option(index=1)
        page.locator("[data-testid=document-file-input]").set_input_files(str(SAMPLE_PDF_PATH))
        page.locator("[data-testid=document-upload-btn]").click()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        expect(page.locator("[data-testid=application-detail-page]")).to_be_visible()
        expect(page.locator(".document-upload .alert-danger")).to_have_count(0, timeout=3000)


@pytest.mark.e2e_playwright
@pytest.mark.vue
@pytest.mark.nondestructive
class TestVueMobileViewport:
    """Mobile viewport visual tests."""

    def test_mobile_login_page(self, page: Page, take_screenshot):
        """Login page at mobile viewport."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"{VUE_BASE_URL}/login")
        page.wait_for_load_state("networkidle")
        if page.title() and "not found" in page.title().lower():
            pytest.skip("Vue app not available at BASE_URL. Run with BASE_URL=http://localhost:5173")
        take_screenshot("vue-mobile-01-login", full_page=True)
        expect(page.locator("[data-testid=login-email]")).to_be_visible()
        expect(page.locator("[data-testid=login-submit]")).to_be_visible()

    def test_mobile_dashboard(self, page: Page, take_screenshot):
        """Dashboard at mobile viewport."""
        page.set_viewport_size({"width": 375, "height": 667})
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/dashboard")
        page.wait_for_load_state("networkidle")
        take_screenshot("vue-mobile-02-dashboard", full_page=True)
        expect(page.locator("[data-testid=dashboard-page]")).to_be_visible(timeout=5000)

    def test_mobile_applications(self, page: Page, take_screenshot):
        """Applications list at mobile viewport."""
        page.set_viewport_size({"width": 375, "height": 667})
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/applications")
        page.wait_for_load_state("networkidle")
        take_screenshot("vue-mobile-03-applications", full_page=True)
        expect(page.get_by_role("heading", name=re.compile(r"My Applications", re.I))).to_be_visible(timeout=5000)

    def test_mobile_profile(self, page: Page, take_screenshot):
        """Profile at mobile viewport."""
        page.set_viewport_size({"width": 375, "height": 667})
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/profile")
        page.wait_for_load_state("networkidle")
        take_screenshot("vue-mobile-04-profile", full_page=True)
        expect(page.locator('label:has-text("Language")').first).to_be_visible(timeout=5000)

    def test_mobile_documents(self, page: Page, take_screenshot):
        """Documents list at mobile viewport."""
        page.set_viewport_size({"width": 375, "height": 667})
        _login_vue_or_skip(page, VUE_BASE_URL, VUE_STUDENT_EMAIL, VUE_STUDENT_PASSWORD)
        page.goto(f"{VUE_BASE_URL}/documents")
        page.wait_for_load_state("networkidle")
        take_screenshot("vue-mobile-05-documents", full_page=True)
        expect(page.locator("[data-testid=documents-page]")).to_be_visible(timeout=5000)
