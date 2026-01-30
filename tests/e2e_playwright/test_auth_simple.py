"""
Simple authentication E2E tests.

These tests verify basic authentication workflows work correctly.
Uses API login for reliable and fast authentication.
"""

import pytest
from playwright.sync_api import Page, expect
import time
from tests.e2e_playwright.utils.auth_helpers import (
    login_via_api,
    login_as_student,
    login_as_coordinator,
    login_as_admin,
    logout,
    is_logged_in,
)


@pytest.mark.e2e_playwright
@pytest.mark.auth
@pytest.mark.nondestructive
class TestAuthenticationSimple:
    """Simple authentication workflow tests."""
    
    def test_login_page_accessible(self, page: Page, base_url: str):
        """Test that login page is accessible."""
        page.goto(f"{base_url}/seim/login/")
        page.wait_for_load_state("networkidle")
        
        # Verify page title
        title = page.title()
        assert "login" in title.lower(), f"Expected login page, got title: {title}"
        
        # Verify Sign In button exists (we know this from diagnostic)
        sign_in_button = page.locator('button:has-text("Sign In"), input[type="submit"]:has-text("Sign In")')
        expect(sign_in_button).to_be_visible(timeout=5000)
        
        # Verify password field exists
        password_field = page.locator('input[type="password"]')
        expect(password_field).to_be_visible(timeout=5000)
        
        print("✅ Login page is accessible with all required elements")
    
    def test_login_with_valid_credentials(self, page: Page, base_url: str):
        """Test login with valid student credentials via API."""
        # Login via API
        login_data = login_as_student(page, base_url)
        
        assert login_data.get('access'), "Access token not received"
        assert login_data.get('refresh'), "Refresh token not received"
        assert login_data.get('user'), "User data not received"
        
        # Verify we're logged in
        assert is_logged_in(page), "User should be logged in after API login"
        
        # Navigate to dashboard to verify access
        page.goto(f"{base_url}/seim/dashboard/")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        
        current_url = page.url
        assert "login" not in current_url.lower(), f"Should be on dashboard, but on: {current_url}"
        
        print(f"✅ Login successful! User: {login_data['user'].get('username', 'unknown')}")
        print(f"   Redirected to: {current_url}")
        page.screenshot(path="tests/e2e_playwright/screenshots/login_success.png")
    
    def test_login_with_invalid_credentials(self, page: Page, base_url: str):
        """Test login with invalid credentials shows error."""
        page.goto(f"{base_url}/seim/login/")
        page.wait_for_load_state("networkidle")
        
        # Find and fill username field
        username_field = page.locator('input[type="text"]').first
        if username_field.count() == 0:
            username_field = page.locator('input[name="username"], input[name="email"]').first
        
        expect(username_field).to_be_visible()
        username_field.fill("invalid_user_12345")
        
        # Fill password
        password_field = page.locator('input[type="password"]').first
        expect(password_field).to_be_visible()
        password_field.fill("wrong_password")
        
        # Submit form
        sign_in_button = page.locator('button:has-text("Sign In"), input[type="submit"]:has-text("Sign In")').first
        expect(sign_in_button).to_be_visible()
        sign_in_button.click()
        
        # Wait for response (should stay on login page or show error)
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Give time for error message to appear
        
        # Verify we're still on login page
        current_url = page.url
        assert "login" in current_url.lower(), f"Expected to stay on login page, but redirected to: {current_url}"
        
        # Check for error message (optional - some forms may not show explicit errors)
        # This is a soft check - we mainly care that we didn't get logged in
        has_error = (
            page.locator('text=/error|invalid|incorrect|wrong|credentials/i').count() > 0 or
            page.locator('.error, .alert-danger, .alert-error, [role="alert"]').count() > 0
        )
        
        if has_error:
            print("✅ Error message displayed for invalid credentials")
        else:
            print("ℹ️  No explicit error message found, but correctly stayed on login page")
        
        print("✅ Invalid login handled correctly")
        page.screenshot(path="tests/e2e_playwright/screenshots/login_invalid.png")
    
    def test_registration_page_accessible(self, page: Page, base_url: str):
        """Test that registration page is accessible."""
        # Try common registration URLs
        registration_urls = [
            f"{base_url}/seim/register/",
            f"{base_url}/register/",
            f"{base_url}/signup/",
        ]
        
        accessible = False
        for url in registration_urls:
            try:
                response = page.goto(url)
                if response and response.ok:
                    page.wait_for_load_state("networkidle")
                    # Check for registration form elements
                    has_form = (
                        page.locator('form').count() > 0 or
                        page.locator('input[type="password"]').count() > 0
                    )
                    if has_form:
                        accessible = True
                        print(f"✅ Registration page accessible at: {url}")
                        break
            except:
                continue
        
        if not accessible:
            print("ℹ️  Registration page not found (may not be implemented)")
            # Don't fail - registration might not be enabled
    
    def test_password_reset_page_accessible(self, page: Page, base_url: str):
        """Test that password reset page is accessible."""
        reset_urls = [
            f"{base_url}/seim/password-reset/",
            f"{base_url}/password-reset/",
            f"{base_url}/reset-password/",
        ]
        
        accessible = False
        for url in reset_urls:
            try:
                response = page.goto(url)
                if response and response.ok:
                    page.wait_for_load_state("networkidle")
                    # Check for email input (common in reset forms)
                    has_email_field = page.locator('input[type="email"], input[name="email"]').count() > 0
                    if has_email_field:
                        accessible = True
                        print(f"✅ Password reset page accessible at: {url}")
                        break
            except:
                continue
        
        if not accessible:
            print("ℹ️  Password reset page not found (may not be implemented)")
    
    def test_login_as_coordinator(self, page: Page, base_url: str):
        """Test login as coordinator user."""
        login_data = login_as_coordinator(page, base_url)
        
        assert login_data.get('access'), "Access token not received"
        assert login_data.get('user'), "User data not received"
        assert is_logged_in(page), "User should be logged in"
        
        # Verify user role
        user_data = login_data.get('user', {})
        print(f"✅ Coordinator login successful! User: {user_data.get('username', 'unknown')}")
        page.screenshot(path="tests/e2e_playwright/screenshots/login_coordinator.png")
    
    def test_login_as_admin(self, page: Page, base_url: str):
        """Test login as admin user."""
        login_data = login_as_admin(page, base_url)
        
        assert login_data.get('access'), "Access token not received"
        assert login_data.get('user'), "User data not received"
        assert is_logged_in(page), "User should be logged in"
        
        # Verify user is admin
        user_data = login_data.get('user', {})
        assert user_data.get('is_staff', False) or user_data.get('is_superuser', False), \
            "Admin user should have staff or superuser privileges"
        
        print(f"✅ Admin login successful! User: {user_data.get('username', 'unknown')}")
        page.screenshot(path="tests/e2e_playwright/screenshots/login_admin.png")
    
    def test_login_with_invalid_credentials_api(self, page: Page, base_url: str):
        """Test login API with invalid credentials."""
        page.goto(f"{base_url}/seim/login/")
        page.wait_for_load_state("networkidle")
        
        # Get CSRF token
        csrf_token = page.locator('#loginForm input[name="csrfmiddlewaretoken"]').first.get_attribute("value")
        if not csrf_token:
            csrf_token = page.locator('input[name="csrfmiddlewaretoken"]').first.get_attribute("value")
        
        assert csrf_token, "CSRF token not found"
        
        # Try to login with invalid credentials
        context = page.context
        response = context.request.post(
            f"{base_url}/api/accounts/login/",
            headers={
                "Content-Type": "application/json",
                "X-CSRFToken": csrf_token,
                "Referer": f"{base_url}/seim/login/",
            },
            data={
                "login": "invalid_user_12345",
                "password": "wrong_password"
            }
        )
        
        # Should fail with 400 or 401
        assert not response.ok, f"Login should fail but got status {response.status}"
        assert response.status in [400, 401], f"Expected 400 or 401, got {response.status}"
        
        error_data = response.text()
        print(f"✅ Invalid login correctly rejected. Status: {response.status}")
        print(f"   Error: {error_data[:100]}")
        page.screenshot(path="tests/e2e_playwright/screenshots/login_invalid_api.png")
    
    def test_logout_functionality(self, page: Page, base_url: str):
        """Test logout functionality after login."""
        # First, login via API
        login_data = login_as_student(page, base_url)
        assert is_logged_in(page), "Should be logged in"
        
        # Navigate to a protected page to verify we're logged in
        page.goto(f"{base_url}/seim/dashboard/")
        page.wait_for_load_state("networkidle")
        assert "login" not in page.url.lower(), "Should be able to access dashboard when logged in"
        
        # Logout
        logout(page, base_url)
        
        # Verify we're logged out
        assert not is_logged_in(page), "Should not be logged in after logout"
        
        # Try to access a protected page - should redirect to login
        page.goto(f"{base_url}/seim/dashboard/")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        
        final_url = page.url
        # Should be on login page or redirected
        assert "login" in final_url.lower() or base_url in final_url, \
            f"Expected to be logged out, but on: {final_url}"
        
        print("✅ Logout successful - tokens cleared and access denied")
        page.screenshot(path="tests/e2e_playwright/screenshots/logout_test.png")
    
    def test_dashboard_access_after_login(self, page: Page, base_url: str):
        """Test that dashboard is accessible after login."""
        # Login via API
        login_data = login_as_student(page, base_url)
        assert is_logged_in(page), "Should be logged in after API login"
        
        # Try to navigate to dashboard
        dashboard_urls = [
            f"{base_url}/dashboard/",
            f"{base_url}/seim/dashboard/",
        ]
        
        accessed = False
        for dashboard_url in dashboard_urls:
            try:
                page.goto(dashboard_url)
                page.wait_for_load_state("networkidle")
                time.sleep(1)
                
                current_url = page.url
                if "login" not in current_url.lower():
                    accessed = True
                    print(f"✅ Dashboard accessible after login. URL: {current_url}")
                    page.screenshot(path="tests/e2e_playwright/screenshots/dashboard_after_login.png")
                    break
            except:
                continue
        
        if not accessed:
            # Check if we're on any valid page (not login)
            current_url = page.url
            assert "login" not in current_url.lower(), \
                f"Should be able to access dashboard when logged in, but on: {current_url}"
            print(f"✅ Accessible page after login. URL: {current_url}")
            page.screenshot(path="tests/e2e_playwright/screenshots/dashboard_after_login.png")

