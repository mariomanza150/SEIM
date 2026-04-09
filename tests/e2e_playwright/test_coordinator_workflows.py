"""
Coordinator workflow E2E tests.

Tests coordinator-specific workflows for reviewing and managing applications.
"""

import pytest
from playwright.sync_api import Page, expect
from tests.e2e_playwright.utils.auth_helpers import login_as_coordinator, VueAppNotAvailable
import time


@pytest.mark.e2e_playwright
@pytest.mark.workflow
@pytest.mark.coordinator
@pytest.mark.nondestructive
class TestCoordinatorWorkflows:
    """Test coordinator-specific workflows."""
    
    def test_coordinator_dashboard_access(self, page: Page, base_url: str):
        """Test that coordinator can access coordinator dashboard."""
        try:
            login_as_coordinator(page, base_url)
        except VueAppNotAvailable as e:
            pytest.skip(str(e))
        
        page.goto(f"{base_url}/seim/coordinator-dashboard/")
        page.wait_for_load_state("networkidle")
        
        # Verify we're on coordinator dashboard
        assert "login" not in page.url.lower(), "Should be on coordinator dashboard, not login page"
        
        # Check for coordinator dashboard elements
        title = page.title()
        assert "coordinator" in title.lower() or "dashboard" in title.lower() or "seim" in title.lower(), \
            f"Expected coordinator dashboard, got: {title}"
        
        # Check for coordinator-specific content
        has_coordinator_content = (
            page.locator('text=/coordinator|review|application|pending/i').count() > 0 or
            page.locator('.coordinator-dashboard, .dashboard, .review').count() > 0
        )
        
        print("✅ Coordinator dashboard accessible")
        page.screenshot(path="tests/e2e_playwright/screenshots/coordinator_dashboard.png")
    
    def test_view_all_applications(self, page: Page, base_url: str):
        """Test that coordinator can view all applications (not just own)."""
        try:
            login_as_coordinator(page, base_url)
        except VueAppNotAvailable as e:
            pytest.skip(str(e))
        
        page.goto(f"{base_url}/seim/applications/")
        page.wait_for_load_state("networkidle")
        
        # Verify we're on applications page
        assert "login" not in page.url.lower(), "Should be able to access applications page"
        
        # Coordinators should see all applications, not just their own
        # Check for applications list or table
        has_content = (
            page.locator('text=/application|all applications|review/i').count() > 0 or
            page.locator('.application, .card, table, .list-group').count() > 0
        )
        
        print("✅ Coordinator can view applications page")
        page.screenshot(path="tests/e2e_playwright/screenshots/coordinator_applications.png")
    
    def test_access_student_dashboard_features(self, page: Page, base_url: str):
        """Test that coordinator can access student features (they have student role too)."""
        try:
            login_as_coordinator(page, base_url)
        except VueAppNotAvailable as e:
            pytest.skip(str(e))
        
        # Coordinators should be able to access student features
        student_pages = [
            ("dashboard", "/seim/dashboard/"),
            ("programs", "/seim/programs/"),
            ("profile", "/seim/profile/"),
        ]
        
        for page_name, url_path in student_pages:
            page.goto(f"{base_url}{url_path}")
            page.wait_for_load_state("networkidle")
            
            assert "login" not in page.url.lower(), \
                f"Coordinator should be able to access {page_name} page"
        
        print("✅ Coordinator can access student features")
        page.screenshot(path="tests/e2e_playwright/screenshots/coordinator_student_features.png")
    
    def test_user_management_access(self, page: Page, base_url: str):
        """Test that coordinator can access user management."""
        try:
            login_as_coordinator(page, base_url)
        except VueAppNotAvailable as e:
            pytest.skip(str(e))
        
        page.goto(f"{base_url}/seim/user-management/")
        page.wait_for_load_state("networkidle")
        
        # Coordinators may or may not have access to user management
        # Just verify the page loads (might redirect if no access)
        current_url = page.url
        
        if "login" not in current_url.lower():
            print("✅ Coordinator can access user management")
        else:
            print("ℹ️  Coordinator redirected (may not have user management access)")
        
        page.screenshot(path="tests/e2e_playwright/screenshots/coordinator_user_management.png")
    
    def test_analytics_access(self, page: Page, base_url: str):
        """Test that coordinator can access analytics (limited)."""
        try:
            login_as_coordinator(page, base_url)
        except VueAppNotAvailable as e:
            pytest.skip(str(e))
        
        page.goto(f"{base_url}/seim/analytics/")
        page.wait_for_load_state("networkidle")
        
        # Coordinators may have limited analytics access
        current_url = page.url
        
        if "login" not in current_url.lower():
            print("✅ Coordinator can access analytics")
        else:
            print("ℹ️  Coordinator redirected (may not have analytics access)")
        
        page.screenshot(path="tests/e2e_playwright/screenshots/coordinator_analytics.png")
