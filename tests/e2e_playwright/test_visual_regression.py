"""
Visual regression tests using Playwright screenshots.

Tests compare current page screenshots with baseline images to detect unintended UI changes.
Requires: pixelmatch, PIL
"""

import pytest

from tests.e2e_playwright.pages.auth_page import AuthPage
from tests.e2e_playwright.pages.dashboard_page import DashboardPage
from tests.e2e_playwright.pages.programs_page import ProgramsPage
from tests.e2e_playwright.pages.applications_page import ApplicationsPage
from tests.e2e_playwright.pages.profile_page import ProfilePage


@pytest.mark.e2e_playwright
@pytest.mark.visual
class TestVisualRegression:
    """Test suite for visual regression testing."""
    
    def test_login_page_visual(self, page, base_url, assert_visual_match):
        """Test visual appearance of login page."""
        auth_page = AuthPage(page, base_url)
        auth_page.navigate_to_login()
        
        # Hide dynamic elements (timestamps, etc.)
        from tests.e2e_playwright.utils.visual_regression import hide_dynamic_elements
        hide_dynamic_elements(page, ['.timestamp', '[data-time]'])
        
        # Compare with baseline
        assert assert_visual_match('login_page')
    
    def test_register_page_visual(self, page, base_url, assert_visual_match):
        """Test visual appearance of register page."""
        auth_page = AuthPage(page, base_url)
        auth_page.navigate_to_register()
        
        from tests.e2e_playwright.utils.visual_regression import hide_dynamic_elements
        hide_dynamic_elements(page, ['.timestamp', '[data-time]'])
        
        assert assert_visual_match('register_page')
    
    def test_dashboard_visual_student(self, page, base_url, login_as_student, assert_visual_match):
        """Test visual appearance of student dashboard."""
        dashboard_page = DashboardPage(page, base_url)
        dashboard_page.navigate_to_dashboard()
        
        # Hide dynamic content
        from tests.e2e_playwright.utils.visual_regression import hide_dynamic_elements, mask_elements
        hide_dynamic_elements(page, ['.timestamp', '[data-time]', '.notification-badge'])
        mask_elements(page, ['.user-specific-data'])
        
        assert assert_visual_match('dashboard_student')
    
    def test_programs_list_visual(self, page, base_url, login_as_student, assert_visual_match):
        """Test visual appearance of programs listing."""
        programs_page = ProgramsPage(page, base_url)
        programs_page.navigate_to_programs()
        
        from tests.e2e_playwright.utils.visual_regression import hide_dynamic_elements
        hide_dynamic_elements(page, ['.timestamp', '[data-time]'])
        
        assert assert_visual_match('programs_list')
    
    def test_applications_list_visual(self, page, base_url, login_as_student, assert_visual_match):
        """Test visual appearance of applications listing."""
        applications_page = ApplicationsPage(page, base_url)
        applications_page.navigate_to_applications()
        
        from tests.e2e_playwright.utils.visual_regression import hide_dynamic_elements
        hide_dynamic_elements(page, ['.timestamp', '[data-time]', '.status-badge'])
        
        assert assert_visual_match('applications_list')
    
    def test_profile_page_visual(self, page, base_url, login_as_student, assert_visual_match):
        """Test visual appearance of profile page."""
        profile_page = ProfilePage(page, base_url)
        profile_page.navigate_to_profile()
        
        from tests.e2e_playwright.utils.visual_regression import mask_elements
        mask_elements(page, ['.profile-photo', '.email', '.phone'])
        
        assert assert_visual_match('profile_page')


@pytest.mark.e2e_playwright
@pytest.mark.visual
class TestVisualRegressionDarkMode:
    """Test visual appearance in dark mode."""
    
    def test_login_page_dark_mode_visual(self, page, base_url, assert_visual_match):
        """Test login page in dark mode."""
        auth_page = AuthPage(page, base_url)
        auth_page.navigate_to_login()
        
        # Enable dark mode if supported
        try:
            page.evaluate("document.body.classList.add('dark-mode')")
        except:
            pytest.skip("Dark mode not supported")
        
        from tests.e2e_playwright.utils.visual_regression import hide_dynamic_elements
        hide_dynamic_elements(page, ['.timestamp'])
        
        assert assert_visual_match('login_page_dark')

