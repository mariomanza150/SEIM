"""
Accessibility tests using axe-playwright.

Tests validate WCAG 2.1 Level AA compliance and accessibility best practices.
"""

import pytest


@pytest.mark.e2e_playwright
@pytest.mark.accessibility
@pytest.mark.nondestructive
class TestAccessibility:
    """Test suite for accessibility compliance."""

    def test_login_page_accessibility(self, page, base_url):
        """Test accessibility of login page."""
        from tests.e2e_playwright.pages.auth_page import AuthPage

        auth_page = AuthPage(page, base_url)
        auth_page.navigate_to_login()
        from tests.e2e_playwright.utils.axe_helpers import (
            format_violations,
            run_axe,
            serious_violations,
        )

        violations = serious_violations(run_axe(page))
        assert not violations, format_violations(violations)

    def test_register_page_accessibility(self, page, base_url):
        """Test accessibility of register page."""
        from tests.e2e_playwright.pages.auth_page import AuthPage

        auth_page = AuthPage(page, base_url)
        auth_page.navigate_to_register()
        from tests.e2e_playwright.utils.axe_helpers import (
            format_violations,
            run_axe,
            serious_violations,
        )

        violations = serious_violations(run_axe(page))
        assert not violations, format_violations(violations)

    def test_dashboard_accessibility(self, page, base_url, login_as_student):
        """Test accessibility of dashboard."""
        from tests.e2e_playwright.pages.dashboard_page import DashboardPage

        dashboard_page = DashboardPage(page, base_url)
        dashboard_page.navigate_to_dashboard()
        from tests.e2e_playwright.utils.axe_helpers import (
            format_violations,
            run_axe,
            serious_violations,
        )

        violations = serious_violations(run_axe(page))
        assert not violations, format_violations(violations)

    def test_programs_page_accessibility(self, page, base_url, login_as_student):
        """Test accessibility of programs page."""
        from tests.e2e_playwright.pages.programs_page import ProgramsPage

        programs_page = ProgramsPage(page, base_url)
        programs_page.navigate_to_programs()
        from tests.e2e_playwright.utils.axe_helpers import (
            format_violations,
            run_axe,
            serious_violations,
        )

        violations = serious_violations(run_axe(page))
        assert not violations, format_violations(violations)

    def test_keyboard_navigation_login(self, page, base_url):
        """Test keyboard navigation on login page."""
        from tests.e2e_playwright.pages.auth_page import AuthPage

        auth_page = AuthPage(page, base_url)
        auth_page.navigate_to_login()
        if page.title() and "not found" in page.title().lower():
            pytest.skip(
                "Vue app not available at base_url. Run with BASE_URL=http://localhost:5173"
            )
        focused = None
        for _ in range(12):
            page.keyboard.press("Tab")
            focused = page.evaluate(
                "() => document.activeElement?.type || document.activeElement?.getAttribute('type')"
            )
            if focused == "submit":
                break
        assert focused == "submit", (
            f"Expected focus on submit button, got type: {focused}"
        )

    def test_screen_reader_labels(self, page, base_url):
        """Test that form inputs have proper labels for screen readers."""
        from tests.e2e_playwright.pages.auth_page import AuthPage

        auth_page = AuthPage(page, base_url)
        auth_page.navigate_to_login()
        if page.title() and "not found" in page.title().lower():
            pytest.skip(
                "Vue app not available at base_url. Run with BASE_URL=http://localhost:5173"
            )
        # Check email/username input has label or aria-label
        username_input = page.locator(auth_page.LOGIN_USERNAME_INPUT)
        has_label = (
            username_input.get_attribute("aria-label")
            or username_input.get_attribute("aria-labelledby")
            or page.locator(
                f'label[for="{username_input.get_attribute("id")}"]'
            ).count()
            > 0
        )
        assert has_label, "Username input must have accessible label"

    def test_color_contrast(self, page, base_url):
        """Test color contrast ratios meet WCAG standards."""
        from tests.e2e_playwright.pages.auth_page import AuthPage

        auth_page = AuthPage(page, base_url)
        auth_page.navigate_to_login()
        from tests.e2e_playwright.utils.axe_helpers import format_violations, run_axe

        results = run_axe(page)
        raw = getattr(results, "violations", None) or []
        contrast_violations = []
        for item in raw:
            vid = getattr(item, "id", None) or (
                item.get("id") if isinstance(item, dict) else ""
            )
            if "color-contrast" in str(vid):
                contrast_violations.append(item)
        assert not contrast_violations, format_violations(contrast_violations)


@pytest.mark.e2e_playwright
@pytest.mark.accessibility
@pytest.mark.smoke
@pytest.mark.nondestructive
class TestAccessibilitySmoke:
    """Smoke tests for critical accessibility requirements."""

    def test_main_pages_accessible(self, page, base_url):
        """Smoke test for main pages accessibility."""
        from tests.e2e_playwright.pages.auth_page import AuthPage

        auth_page = AuthPage(page, base_url)

        # Test login page
        auth_page.navigate_to_login()
        assert page.locator("h1, h2").count() > 0, "Page must have heading"

        # Test register page
        auth_page.navigate_to_register()
        assert page.locator("h1, h2").count() > 0, "Page must have heading"
