"""
End-to-end tests for authentication workflows.

Tests user registration, login, logout, password reset, and session management.
"""

import pytest
from tests.e2e_playwright.pages.auth_page import AuthPage
from tests.e2e_playwright.pages.dashboard_page import DashboardPage
from tests.e2e_playwright.utils.data_generators import generate_user_data


@pytest.mark.e2e_playwright
@pytest.mark.auth
class TestAuthenticationWorkflows:
    """Test suite for authentication workflows."""
    
    def test_user_registration_success(self, page, base_url):
        """Test successful user registration."""
        auth_page = AuthPage(page, base_url)
        user_data = generate_user_data()
        
        # Navigate to registration page
        auth_page.navigate_to_register()
        auth_page.assert_register_page_loaded()
        
        # Fill and submit registration form
        auth_page.register(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            confirm_password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        
        # Verify success (either redirected to dashboard or showing success message)
        # This may vary based on your implementation
        assert 'register' not in page.url or auth_page.is_visible(auth_page.REGISTER_SUCCESS_MESSAGE)
    
    def test_user_registration_password_mismatch(self, page, base_url):
        """Test registration with mismatched passwords."""
        auth_page = AuthPage(page, base_url)
        user_data = generate_user_data()
        
        auth_page.navigate_to_register()
        auth_page.register(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            confirm_password='DifferentPassword123!',
        )
        
        # Should show error message or stay on register page
        assert 'register' in page.url
    
    def test_user_login_valid_credentials(self, page, base_url, test_users):
        """Test login with valid credentials."""
        auth_page = AuthPage(page, base_url)
        dashboard_page = DashboardPage(page, base_url)
        
        # Navigate to login page
        auth_page.navigate_to_login()
        auth_page.assert_login_page_loaded()
        
        # Login with student credentials
        student_creds = test_users['student1']
        auth_page.login(student_creds['username'], student_creds['password'])
        
        # Verify redirect to dashboard
        assert 'dashboard' in page.url or 'login' not in page.url
        assert auth_page.is_logged_in()
    
    def test_user_login_invalid_credentials(self, page, base_url):
        """Test login with invalid credentials."""
        auth_page = AuthPage(page, base_url)
        
        auth_page.navigate_to_login()
        auth_page.login('nonexistent_user', 'wrong_password')
        
        # Should show error and stay on login page
        assert 'login' in page.url
    
    def test_user_logout(self, page, base_url, login_as_student):
        """Test user logout functionality."""
        auth_page = AuthPage(page, base_url)
        
        # Verify logged in
        assert auth_page.is_logged_in()
        
        # Logout
        auth_page.logout()
        
        # Verify logged out
        assert 'login' in page.url or not auth_page.is_logged_in()
    
    def test_session_persistence(self, page, base_url, test_users):
        """Test that session persists across page navigation."""
        auth_page = AuthPage(page, base_url)
        dashboard_page = DashboardPage(page, base_url)
        
        # Login
        auth_page.navigate_to_login()
        student_creds = test_users['student1']
        auth_page.login(student_creds['username'], student_creds['password'])
        
        # Navigate to different pages
        dashboard_page.navigate_to_dashboard()
        assert auth_page.is_logged_in()
        
        # Reload page
        page.reload()
        assert auth_page.is_logged_in()
    
    def test_protected_page_redirect(self, page, base_url):
        """Test that protected pages redirect to login."""
        dashboard_page = DashboardPage(page, base_url)
        
        # Try to access dashboard without login
        dashboard_page.navigate_to_dashboard()
        
        # Should redirect to login or show access denied
        assert 'login' in page.url or 'dashboard' not in page.url


@pytest.mark.e2e_playwright
@pytest.mark.auth
@pytest.mark.smoke
class TestAuthenticationSmoke:
    """Smoke tests for critical authentication paths."""
    
    def test_login_logout_smoke(self, page, base_url, test_users):
        """Smoke test for basic login/logout flow."""
        auth_page = AuthPage(page, base_url)
        
        # Login
        auth_page.navigate_to_login()
        student_creds = test_users['student1']
        auth_page.login(student_creds['username'], student_creds['password'])
        assert auth_page.is_logged_in()
        
        # Logout
        auth_page.logout()
        assert not auth_page.is_logged_in()

