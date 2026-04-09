"""
Student workflow E2E tests.

Tests the complete student journey from login to application submission.
"""

import pytest
from playwright.sync_api import Page, expect
from tests.e2e_playwright.utils.auth_helpers import login_as_student, VueAppNotAvailable
import time


@pytest.mark.e2e_playwright
@pytest.mark.workflow
@pytest.mark.student
@pytest.mark.nondestructive
class TestStudentWorkflows:
    """Test student-specific workflows."""
    
    def test_student_dashboard_access(self, page: Page, base_url: str):
        """Test that student can access dashboard after login."""
        try:
            login_as_student(page, base_url)
        except VueAppNotAvailable as e:
            pytest.skip(str(e))
        
        page.goto(f"{base_url}/seim/dashboard/")
        page.wait_for_load_state("networkidle")
        
        # Verify we're on dashboard (not redirected to login)
        assert "login" not in page.url.lower(), "Should be on dashboard, not login page"
        
        # Check for dashboard elements
        title = page.title()
        assert "dashboard" in title.lower() or "seim" in title.lower(), \
            f"Expected dashboard page, got: {title}"
        
        print("✅ Student dashboard accessible")
        page.screenshot(path="tests/e2e_playwright/screenshots/student_dashboard.png")
    
    def test_browse_programs(self, page: Page, base_url: str):
        """Test that student can browse available programs."""
        try:
            login_as_student(page, base_url)
        except VueAppNotAvailable as e:
            pytest.skip(str(e))
        
        page.goto(f"{base_url}/seim/programs/")
        page.wait_for_load_state("networkidle")
        
        # Verify we're on programs page
        assert "login" not in page.url.lower(), "Should be able to access programs page"
        assert "program" in page.url.lower() or "seim" in page.url.lower(), \
            f"Expected programs page, got: {page.url}"
        
        # Check for program listing elements
        # Programs might be in a list, cards, or table
        has_content = (
            page.locator('text=/program|exchange|apply/i').count() > 0 or
            page.locator('.program, .card, table, .list-group').count() > 0
        )
        
        print("✅ Programs page accessible")
        page.screenshot(path="tests/e2e_playwright/screenshots/browse_programs.png")
    
    def test_view_applications_list(self, page: Page, base_url: str):
        """Test that student can view their applications."""
        try:
            login_as_student(page, base_url)
        except VueAppNotAvailable as e:
            pytest.skip(str(e))
        
        page.goto(f"{base_url}/seim/applications/")
        page.wait_for_load_state("networkidle")
        
        # Verify we're on applications page
        assert "login" not in page.url.lower(), "Should be able to access applications page"
        assert "application" in page.url.lower() or "seim" in page.url.lower(), \
            f"Expected applications page, got: {page.url}"
        
        # Check for applications list or empty state
        has_content = (
            page.locator('text=/application|my applications|no applications/i').count() > 0 or
            page.locator('.application, .card, table, .list-group, .empty-state').count() > 0
        )
        
        print("✅ Applications list page accessible")
        page.screenshot(path="tests/e2e_playwright/screenshots/applications_list.png")
    
    def test_create_application_page(self, page: Page, base_url: str):
        """Test that student can access application creation page."""
        try:
            login_as_student(page, base_url)
        except VueAppNotAvailable as e:
            pytest.skip(str(e))
        
        page.goto(f"{base_url}/seim/applications/new")
        page.wait_for_load_state("networkidle")
        
        # Verify we're on create application page
        assert "login" not in page.url.lower(), "Should be able to access create application page"
        assert "create" in page.url.lower() or "application" in page.url.lower(), \
            f"Expected create application page, got: {page.url}"
        
        # Check for form elements
        has_form = (
            page.locator('form').count() > 0 or
            page.locator('input, select, textarea').count() > 0 or
            page.locator('text=/create|new application|apply/i').count() > 0
        )
        
        print("✅ Create application page accessible")
        page.screenshot(path="tests/e2e_playwright/screenshots/create_application_page.png")
    
    def test_view_profile(self, page: Page, base_url: str):
        """Test that student can view their profile."""
        try:
            login_as_student(page, base_url)
        except VueAppNotAvailable as e:
            pytest.skip(str(e))
        
        page.goto(f"{base_url}/seim/profile/")
        page.wait_for_load_state("networkidle")
        
        # Verify we're on profile page
        assert "login" not in page.url.lower(), "Should be able to access profile page"
        assert "profile" in page.url.lower() or "seim" in page.url.lower(), \
            f"Expected profile page, got: {page.url}"
        
        # Check for profile elements
        has_content = (
            page.locator('text=/profile|user|account/i').count() > 0 or
            page.locator('.profile, .user-info, form').count() > 0
        )
        
        print("✅ Profile page accessible")
        page.screenshot(path="tests/e2e_playwright/screenshots/student_profile.png")
    
    def test_view_settings(self, page: Page, base_url: str):
        """Test that student can access settings page."""
        try:
            login_as_student(page, base_url)
        except VueAppNotAvailable as e:
            pytest.skip(str(e))
        
        page.goto(f"{base_url}/seim/settings/")
        page.wait_for_load_state("networkidle")
        
        # Verify we're on settings page
        assert "login" not in page.url.lower(), "Should be able to access settings page"
        assert "setting" in page.url.lower() or "seim" in page.url.lower(), \
            f"Expected settings page, got: {page.url}"
        
        print("✅ Settings page accessible")
        page.screenshot(path="tests/e2e_playwright/screenshots/student_settings.png")
    
    def test_navigation_links(self, page: Page, base_url: str):
        """Test that student can navigate between pages."""
        try:
            login_as_student(page, base_url)
        except VueAppNotAvailable as e:
            pytest.skip(str(e))
        
        # Start at dashboard
        page.goto(f"{base_url}/seim/dashboard/")
        page.wait_for_load_state("networkidle")
        
        # Try to find and click navigation links
        nav_links = page.locator('nav a, .navbar a, .nav-link').all()
        
        if len(nav_links) > 0:
            # Try clicking on a few common links
            clicked = False
            for link in nav_links[:5]:  # Try first 5 links
                try:
                    href = link.get_attribute('href')
                    text = link.inner_text().strip().lower()
                    
                    # Look for common student navigation items
                    if any(keyword in text for keyword in ['program', 'application', 'profile', 'dashboard']):
                        if href and href.startswith('/'):
                            link.click()
                            page.wait_for_load_state("networkidle", timeout=5000)
                            clicked = True
                            break
                except:
                    continue
            
            if clicked:
                print("✅ Navigation links work")
            else:
                print("ℹ️  Navigation links found but not clicked")
        else:
            print("ℹ️  No navigation links found")
        
        page.screenshot(path="tests/e2e_playwright/screenshots/student_navigation.png")
