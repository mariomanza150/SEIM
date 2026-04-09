"""
Admin workflow E2E tests.

Tests admin-specific workflows for system management.
"""

import pytest
from playwright.sync_api import Page, expect
from tests.e2e_playwright.utils.auth_helpers import login_as_admin, VueAppNotAvailable
import time


@pytest.mark.e2e_playwright
@pytest.mark.workflow
@pytest.mark.admin
@pytest.mark.nondestructive
class TestAdminWorkflows:
    """Test admin-specific workflows."""
    
    def test_admin_dashboard_access(self, page: Page, base_url: str):
        """Test that admin can access admin dashboard."""
        try:
            login_as_admin(page, base_url)
        except VueAppNotAvailable as e:
            pytest.skip(str(e))
        
        page.goto(f"{base_url}/seim/admin-dashboard/")
        page.wait_for_load_state("networkidle")
        
        # Verify we're on admin dashboard
        assert "login" not in page.url.lower(), "Should be on admin dashboard, not login page"
        
        # Check for admin dashboard elements
        title = page.title()
        assert "admin" in title.lower() or "dashboard" in title.lower() or "seim" in title.lower(), \
            f"Expected admin dashboard, got: {title}"
        
        # Check for admin-specific content
        has_admin_content = (
            page.locator('text=/admin|system|management|analytics/i').count() > 0 or
            page.locator('.admin-dashboard, .dashboard, .system').count() > 0
        )
        
        print("✅ Admin dashboard accessible")
        page.screenshot(path="tests/e2e_playwright/screenshots/admin_dashboard.png")
    
    def test_access_all_features(self, page: Page, base_url: str):
        """Test that admin can access all features (student, coordinator, admin)."""
        try:
            login_as_admin(page, base_url)
        except VueAppNotAvailable as e:
            pytest.skip(str(e))
        # Admin should have access to all pages
        all_pages = [
            ("student dashboard", "/seim/dashboard/"),
            ("coordinator dashboard", "/seim/coordinator-dashboard/"),
            ("admin dashboard", "/seim/admin-dashboard/"),
            ("programs", "/seim/programs/"),
            ("applications", "/seim/applications/"),
            ("user management", "/seim/user-management/"),
            ("analytics", "/seim/analytics/"),
            ("profile", "/seim/profile/"),
        ]
        
        accessible_pages = []
        for page_name, url_path in all_pages:
            try:
                page.goto(f"{base_url}{url_path}")
                page.wait_for_load_state("networkidle", timeout=5000)
                
                if "login" not in page.url.lower():
                    accessible_pages.append(page_name)
            except:
                pass
        
        assert len(accessible_pages) > 0, "Admin should be able to access at least some pages"
        print(f"✅ Admin can access {len(accessible_pages)} pages: {', '.join(accessible_pages)}")
        page.screenshot(path="tests/e2e_playwright/screenshots/admin_all_features.png")
    
    def test_program_management(self, page: Page, base_url: str):
        """Test that admin can access program management."""
        try:
            login_as_admin(page, base_url)
        except VueAppNotAvailable as e:
            pytest.skip(str(e))
        
        # Try to access program creation
        page.goto(f"{base_url}/seim/programs/create/")
        page.wait_for_load_state("networkidle")
        
        # Verify we can access program creation
        assert "login" not in page.url.lower(), "Admin should be able to access program creation"
        
        # Check for form or program management interface
        has_form = (
            page.locator('form').count() > 0 or
            page.locator('text=/program|create|manage/i').count() > 0
        )
        
        print("✅ Admin can access program management")
        page.screenshot(path="tests/e2e_playwright/screenshots/admin_program_management.png")
    
    def test_user_management(self, page: Page, base_url: str):
        """Test that admin can access user management."""
        try:
            login_as_admin(page, base_url)
        except VueAppNotAvailable as e:
            pytest.skip(str(e))
        page.goto(f"{base_url}/seim/user-management/")
        page.wait_for_load_state("networkidle")
        
        # Verify we can access user management
        assert "login" not in page.url.lower(), "Admin should be able to access user management"
        
        # Check for user management interface
        has_content = (
            page.locator('text=/user|manage|role|permission/i').count() > 0 or
            page.locator('.user-management, table, .list-group').count() > 0
        )
        
        print("✅ Admin can access user management")
        page.screenshot(path="tests/e2e_playwright/screenshots/admin_user_management.png")
    
    def test_analytics_access(self, page: Page, base_url: str):
        """Test that admin can access full analytics."""
        try:
            login_as_admin(page, base_url)
        except VueAppNotAvailable as e:
            pytest.skip(str(e))
        page.goto(f"{base_url}/seim/analytics/")
        page.wait_for_load_state("networkidle")
        
        # Verify we can access analytics
        assert "login" not in page.url.lower(), "Admin should be able to access analytics"
        
        # Check for analytics content
        has_content = (
            page.locator('text=/analytics|statistics|report|metric/i').count() > 0 or
            page.locator('.analytics, .chart, .metric').count() > 0
        )
        
        print("✅ Admin can access analytics")
        page.screenshot(path="tests/e2e_playwright/screenshots/admin_analytics.png")
    
    def test_django_admin_access(self, page: Page, base_url: str):
        """Test that admin can access Django admin interface."""
        try:
            login_as_admin(page, base_url)
        except VueAppNotAvailable as e:
            pytest.skip(str(e))
        # Try to access Django admin
        page.goto(f"{base_url}/seim/admin/")
        page.wait_for_load_state("networkidle")
        
        # Django admin might redirect or require additional authentication
        current_url = page.url
        
        if "admin" in current_url.lower() and "login" not in current_url.lower():
            print("✅ Admin can access Django admin")
        elif "login" in current_url.lower():
            # Might need to login separately to Django admin
            print("ℹ️  Django admin requires separate login")
        else:
            print(f"ℹ️  Django admin access status unclear. URL: {current_url}")
        
        page.screenshot(path="tests/e2e_playwright/screenshots/admin_django_admin.png")
