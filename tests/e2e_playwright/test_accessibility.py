"""
Accessibility tests using axe-playwright.

Tests validate WCAG 2.1 Level AA compliance and accessibility best practices.
"""

import pytest


@pytest.mark.e2e_playwright
@pytest.mark.accessibility
class TestAccessibility:
    """Test suite for accessibility compliance."""
    
    def test_login_page_accessibility(self, page, base_url):
        """Test accessibility of login page."""
        from tests.e2e_playwright.pages.auth_page import AuthPage
        
        auth_page = AuthPage(page, base_url)
        auth_page.navigate_to_login()
        if page.title() and "not found" in page.title().lower():
            pytest.skip("Vue app not available at base_url. Run with BASE_URL=http://localhost:5173")
        # Run axe accessibility scan
        try:
            from axe_playwright_python.sync_playwright import Axe
            axe = Axe()
            results = axe.run(page)
            
            # Assert no violations
            assert len(results.violations) == 0, f"Found {len(results.violations)} accessibility violations"
        except ImportError:
            pytest.skip("axe-playwright-python not installed")
    
    def test_register_page_accessibility(self, page, base_url):
        """Test accessibility of register page."""
        from tests.e2e_playwright.pages.auth_page import AuthPage
        
        auth_page = AuthPage(page, base_url)
        auth_page.navigate_to_register()
        
        try:
            from axe_playwright_python.sync_playwright import Axe
            axe = Axe()
            results = axe.run(page)
            assert len(results.violations) == 0
        except ImportError:
            pytest.skip("axe-playwright-python not installed")
    
    def test_dashboard_accessibility(self, page, base_url, login_as_student):
        """Test accessibility of dashboard."""
        from tests.e2e_playwright.pages.dashboard_page import DashboardPage
        
        dashboard_page = DashboardPage(page, base_url)
        dashboard_page.navigate_to_dashboard()
        
        try:
            from axe_playwright_python.sync_playwright import Axe
            axe = Axe()
            results = axe.run(page)
            assert len(results.violations) == 0
        except ImportError:
            pytest.skip("axe-playwright-python not installed")
    
    def test_programs_page_accessibility(self, page, base_url, login_as_student):
        """Test accessibility of programs page."""
        from tests.e2e_playwright.pages.programs_page import ProgramsPage
        
        programs_page = ProgramsPage(page, base_url)
        programs_page.navigate_to_programs()
        
        try:
            from axe_playwright_python.sync_playwright import Axe
            axe = Axe()
            results = axe.run(page)
            assert len(results.violations) == 0
        except ImportError:
            pytest.skip("axe-playwright-python not installed")
    
    def test_keyboard_navigation_login(self, page, base_url):
        """Test keyboard navigation on login page."""
        from tests.e2e_playwright.pages.auth_page import AuthPage
        
        auth_page = AuthPage(page, base_url)
        auth_page.navigate_to_login()
        if page.title() and "not found" in page.title().lower():
            pytest.skip("Vue app not available at base_url. Run with BASE_URL=http://localhost:5173")
        # Test Tab navigation (Vue: email, password, submit)
        page.keyboard.press('Tab')
        page.keyboard.press('Tab')
        page.keyboard.press('Tab')
        focused = page.evaluate("() => document.activeElement?.type || document.activeElement?.getAttribute('type')")
        assert focused == 'submit', f"Expected focus on submit button, got type: {focused}"
    
    def test_screen_reader_labels(self, page, base_url):
        """Test that form inputs have proper labels for screen readers."""
        from tests.e2e_playwright.pages.auth_page import AuthPage
        
        auth_page = AuthPage(page, base_url)
        auth_page.navigate_to_login()
        if page.title() and "not found" in page.title().lower():
            pytest.skip("Vue app not available at base_url. Run with BASE_URL=http://localhost:5173")
        # Check email/username input has label or aria-label
        username_input = page.locator(auth_page.LOGIN_USERNAME_INPUT)
        has_label = (
            username_input.get_attribute('aria-label') or
            username_input.get_attribute('aria-labelledby') or
            page.locator(f'label[for="{username_input.get_attribute("id")}"]').count() > 0
        )
        assert has_label, "Username input must have accessible label"
    
    def test_color_contrast(self, page, base_url):
        """Test color contrast ratios meet WCAG standards."""
        from tests.e2e_playwright.pages.auth_page import AuthPage
        
        auth_page = AuthPage(page, base_url)
        auth_page.navigate_to_login()
        if page.title() and "not found" in page.title().lower():
            pytest.skip("Vue app not available at base_url. Run with BASE_URL=http://localhost:5173")
        try:
            from axe_playwright_python.sync_playwright import Axe
            axe = Axe()
            results = axe.run(page)
            
            # Check for color contrast violations
            contrast_violations = [v for v in results.violations if 'color-contrast' in v.id]
            assert len(contrast_violations) == 0, f"Found {len(contrast_violations)} color contrast violations"
        except ImportError:
            pytest.skip("axe-playwright-python not installed")


@pytest.mark.e2e_playwright
@pytest.mark.accessibility
@pytest.mark.smoke
class TestAccessibilitySmoke:
    """Smoke tests for critical accessibility requirements."""
    
    def test_main_pages_accessible(self, page, base_url):
        """Smoke test for main pages accessibility."""
        from tests.e2e_playwright.pages.auth_page import AuthPage
        
        auth_page = AuthPage(page, base_url)
        
        # Test login page
        auth_page.navigate_to_login()
        assert page.locator('h1, h2').count() > 0, "Page must have heading"
        
        # Test register page
        auth_page.navigate_to_register()
        assert page.locator('h1, h2').count() > 0, "Page must have heading"

