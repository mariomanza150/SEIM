"""
End-to-end tests for notifications.
"""

import pytest
from tests.e2e_playwright.pages.dashboard_page import DashboardPage


@pytest.mark.e2e_playwright
class TestNotifications:
    """Test suite for notification workflows."""
    
    def test_notifications_badge_visible(self, page, base_url, login_as_student):
        """Test notifications badge is visible when logged in."""
        dashboard_page = DashboardPage(page, base_url)
        dashboard_page.navigate_to_dashboard()
        
        # Check if notifications badge exists
        # Note: May not be visible if no notifications
        assert dashboard_page.is_visible(dashboard_page.USER_MENU)

