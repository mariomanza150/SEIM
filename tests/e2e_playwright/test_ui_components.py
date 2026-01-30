"""
End-to-end tests for UI components and interactions.
"""

import pytest
from tests.e2e_playwright.pages.dashboard_page import DashboardPage


@pytest.mark.e2e_playwright
class TestUIComponents:
    """Test suite for UI components."""
    
    def test_navigation_menu_visible(self, page, base_url, login_as_student):
        """Test navigation menu is visible."""
        dashboard_page = DashboardPage(page, base_url)
        dashboard_page.navigate_to_dashboard()
        assert dashboard_page.is_visible(dashboard_page.NAVIGATION_MENU)
    
    def test_responsive_mobile_view(self, mobile_page, base_url, test_users):
        """Test mobile responsive design."""
        from tests.e2e_playwright.pages.auth_page import AuthPage
        
        auth_page = AuthPage(mobile_page, base_url)
        auth_page.navigate_to_login()
        assert auth_page.is_visible(auth_page.LOGIN_USERNAME_INPUT)
    
    def test_responsive_tablet_view(self, tablet_page, base_url, test_users):
        """Test tablet responsive design."""
        from tests.e2e_playwright.pages.auth_page import AuthPage
        
        auth_page = AuthPage(tablet_page, base_url)
        auth_page.navigate_to_login()
        assert auth_page.is_visible(auth_page.LOGIN_USERNAME_INPUT)

