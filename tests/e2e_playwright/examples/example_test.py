"""
Example E2E test demonstrating best practices.

This test shows:
- Page Object Model usage
- Screenshot capture
- Assertion patterns
- Test organization
"""

import pytest
from tests.e2e_playwright.pages.auth_page import AuthPage
from tests.e2e_playwright.pages.dashboard_page import DashboardPage


@pytest.mark.e2e_playwright
@pytest.mark.smoke
class TestExample:
    """Example test class showing best practices."""
    
    def test_complete_login_flow_example(self, page, base_url, test_users, take_screenshot):
        """
        Example test showing complete login flow.
        
        This test demonstrates:
        - Using page objects
        - Taking screenshots
        - Making assertions
        - Using fixtures
        """
        # Initialize page objects
        auth_page = AuthPage(page, base_url)
        dashboard_page = DashboardPage(page, base_url)
        
        # Step 1: Navigate to login page
        auth_page.navigate_to_login()
        auth_page.assert_login_page_loaded()
        
        # Take screenshot of login page
        take_screenshot('example_01_login_page')
        
        # Step 2: Fill in credentials
        student_creds = test_users['student1']
        auth_page.fill(auth_page.LOGIN_USERNAME_INPUT, student_creds['username'])
        auth_page.fill(auth_page.LOGIN_PASSWORD_INPUT, student_creds['password'])
        
        # Take screenshot of filled form
        take_screenshot('example_02_credentials_filled')
        
        # Step 3: Submit login
        auth_page.click(auth_page.LOGIN_SUBMIT_BUTTON)
        auth_page.wait_for_no_loading_indicators()
        
        # Step 4: Verify successful login
        auth_page.assert_logged_in()
        dashboard_page.assert_dashboard_loaded()
        
        # Take screenshot of dashboard
        take_screenshot('example_03_dashboard')
        
        # Step 5: Verify welcome message
        welcome_msg = dashboard_page.get_welcome_message()
        assert welcome_msg  # Welcome message should exist
        
        # Test completed successfully
        print("✓ Example test completed successfully!")

