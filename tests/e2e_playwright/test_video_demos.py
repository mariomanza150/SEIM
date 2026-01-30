"""
Video Demo E2E Tests - Complete User Story Walkthroughs

These tests record video demos of complete user journeys for review and issue spotting.
Each test follows a complete user story path and records the entire journey.
"""

import pytest
from playwright.sync_api import Page, expect
from tests.e2e_playwright.utils.auth_helpers import (
    login_as_student,
    login_as_coordinator,
    login_as_admin,
)
import time


@pytest.mark.e2e_playwright
@pytest.mark.video_demo
@pytest.mark.nondestructive
class TestStudentVideoDemos:
    """Student user story video demos."""
    
    def test_demo_1_new_student_registration_first_application(self, page: Page, base_url: str):
        """
        Story 1: New Student Registration & First Application
        
        Path: Registration → Email Verification → Login → Browse Programs → 
              Create Application → Upload Documents → Submit Application
        """
        # Step 1: Visit homepage
        page.goto(f"{base_url}/seim/")
        page.wait_for_load_state("networkidle")
        time.sleep(1)  # Pause for video clarity
        
        # Step 2: Navigate to registration
        registration_link = page.locator('a:has-text("Register"), a:has-text("Sign up"), a[href*="register"]').first
        if registration_link.count() > 0:
            registration_link.click()
            page.wait_for_load_state("networkidle")
            time.sleep(1)
        
        # Step 3: Complete registration form (if registration page exists)
        # Note: For demo, we'll skip to login since registration might require email verification
        page.goto(f"{base_url}/seim/login/")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        
        # Step 4-5: Login (simulating verified user)
        login_as_student(page, base_url)
        time.sleep(1)
        
        # Step 6: View dashboard
        page.goto(f"{base_url}/seim/dashboard/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Show dashboard
        
        # Step 7: Browse available programs
        page.goto(f"{base_url}/seim/programs/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Show programs
        
        # Step 8: Select a program (if programs exist)
        program_link = page.locator('.program, .card, a[href*="program"]').first
        if program_link.count() > 0:
            program_link.click()
            page.wait_for_load_state("networkidle")
            time.sleep(1)
        
        # Step 9: Start new application
        page.goto(f"{base_url}/seim/applications/create/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Show application form
        
        # Step 10: Fill application form (demonstrate form fields)
        form_inputs = page.locator('input, select, textarea').all()
        if len(form_inputs) > 0:
            # Fill first few fields to demonstrate
            for i, field in enumerate(form_inputs[:3]):
                try:
                    field_type = field.get_attribute('type') or 'text'
                    if field_type not in ['submit', 'button', 'hidden']:
                        field.click()
                        time.sleep(0.5)
                except:
                    pass
        
        # Step 11: Navigate to documents (if document upload page exists)
        page.goto(f"{base_url}/seim/documents/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Show document upload area
        
        # Step 12-13: Review and submit (navigate back to application)
        page.goto(f"{base_url}/seim/applications/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Show applications list
        
        # Step 14: View application status
        application_link = page.locator('.application, .card, a[href*="application"]').first
        if application_link.count() > 0:
            application_link.click()
            page.wait_for_load_state("networkidle")
            time.sleep(2)  # Show application details
        
        print("✅ Demo 1 Complete: New Student Registration & First Application")
    
    def test_demo_2_returning_student_check_status(self, page: Page, base_url: str):
        """
        Story 2: Returning Student - Check Status & Update
        
        Path: Login → Dashboard → View Applications → Check Status → Update Profile
        """
        # Step 1: Login as existing student
        login_as_student(page, base_url)
        time.sleep(1)
        
        # Step 2: View dashboard with applications
        page.goto(f"{base_url}/seim/dashboard/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Show dashboard
        
        # Step 3: Click on application to view details
        page.goto(f"{base_url}/seim/applications/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Show applications list
        
        # Step 4: Check current status
        application_link = page.locator('.application, .card, a[href*="application"]').first
        if application_link.count() > 0:
            application_link.click()
            page.wait_for_load_state("networkidle")
            time.sleep(2)  # Show application details with status
        
        # Step 5: View timeline/history
        timeline = page.locator('text=/timeline|history|status/i').first
        if timeline.count() == 0:
            timeline = page.locator('.timeline, .history').first
        if timeline.count() > 0:
            try:
                timeline.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
        
        # Step 6: Navigate to profile
        page.goto(f"{base_url}/seim/profile/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Show profile
        
        # Step 7: Update profile information
        edit_button = page.locator('button:has-text("Edit"), a:has-text("Edit")').first
        if edit_button.count() > 0:
            try:
                edit_button.click(timeout=5000)
                page.wait_for_load_state("networkidle", timeout=5000)
                time.sleep(1)
            except:
                pass  # Edit button might not be available, continue
        
        # Step 8: Save changes (if edit form exists)
        save_button = page.locator('button:has-text("Save"), button[type="submit"]').first
        if save_button.count() > 0:
            try:
                save_button.scroll_into_view_if_needed(timeout=5000)
                time.sleep(1)
            except:
                pass  # Save button might not be visible, continue
        
        # Step 9: Return to dashboard
        page.goto(f"{base_url}/seim/dashboard/")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        
        print("✅ Demo 2 Complete: Returning Student - Check Status & Update")
    
    def test_demo_3_student_withdraw_draft(self, page: Page, base_url: str):
        """
        Story 3: Student - Withdraw Draft Application
        
        Path: Login → Dashboard → View Draft Application → Withdraw Application
        """
        # Step 1: Login as student
        login_as_student(page, base_url)
        time.sleep(1)
        
        # Step 2: View dashboard
        page.goto(f"{base_url}/seim/dashboard/")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        
        # Step 3: Find draft application
        page.goto(f"{base_url}/seim/applications/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Show applications list
        
        # Step 4: Open application details
        application_link = page.locator('.application, .card, a[href*="application"]').first
        if application_link.count() > 0:
            application_link.click()
            page.wait_for_load_state("networkidle")
            time.sleep(2)  # Show application details
        
        # Step 5: Click withdraw button (if draft and withdraw available)
        withdraw_button = page.locator('button:has-text("Withdraw"), a:has-text("Withdraw")').first
        if withdraw_button.count() > 0:
            try:
                withdraw_button.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
            # Don't actually click to avoid modifying data
        
        # Step 6-7: Show withdrawal flow (simulated)
        print("✅ Demo 3 Complete: Student - Withdraw Draft Application")


@pytest.mark.e2e_playwright
@pytest.mark.video_demo
@pytest.mark.nondestructive
class TestCoordinatorVideoDemos:
    """Coordinator user story video demos."""
    
    def test_demo_4_coordinator_review_pending(self, page: Page, base_url: str):
        """
        Story 4: Coordinator - Review Pending Applications
        
        Path: Login → Coordinator Dashboard → View Pending Applications → 
              Review Application → Add Comment → Change Status
        """
        # Step 1: Login as coordinator
        login_as_coordinator(page, base_url)
        time.sleep(1)
        
        # Step 2: Access coordinator dashboard
        page.goto(f"{base_url}/seim/coordinator-dashboard/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Show coordinator dashboard
        
        # Step 3: View pending applications list
        page.goto(f"{base_url}/seim/applications/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Show all applications
        
        # Step 4: Filter by status (if filter exists)
        filter_dropdown = page.locator('select, .filter, [data-filter]').first
        if filter_dropdown.count() > 0:
            try:
                filter_dropdown.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
        
        # Step 5: Select an application
        application_link = page.locator('.application, .card, a[href*="application"]').first
        if application_link.count() > 0:
            application_link.click()
            page.wait_for_load_state("networkidle")
            time.sleep(2)  # Show application details
        
        # Step 6: Review application details
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        time.sleep(1)
        
        # Step 7: Review uploaded documents
        documents_section = page.locator('text=/document/i').first
        if documents_section.count() == 0:
            documents_section = page.locator('.documents, [data-documents]').first
        if documents_section.count() > 0:
            try:
                documents_section.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
        
        # Step 8: Add internal comment (if comment form exists)
        comment_section = page.locator('textarea, .comment-form, [data-comment]').first
        if comment_section.count() > 0:
            try:
                comment_section.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
        
        # Step 9: Show public comment option
        public_toggle = page.locator('input[type="checkbox"], .public-comment').first
        if public_toggle.count() > 0:
            try:
                public_toggle.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
        
        # Step 10: Show status change options
        status_dropdown = page.locator('select[name*="status"], .status-select').first
        if status_dropdown.count() > 0:
            try:
                status_dropdown.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
        
        # Step 11-12: Show workflow (without actually changing status)
        print("✅ Demo 4 Complete: Coordinator - Review Pending Applications")
    
    def test_demo_5_coordinator_request_resubmission(self, page: Page, base_url: str):
        """
        Story 5: Coordinator - Request Document Resubmission
        
        Path: Login → Coordinator Dashboard → Review Application → 
              View Documents → Request Resubmission → Add Comment
        """
        # Step 1: Login as coordinator
        login_as_coordinator(page, base_url)
        time.sleep(1)
        
        # Step 2: Access coordinator dashboard
        page.goto(f"{base_url}/seim/coordinator-dashboard/")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        
        # Step 3: Select application with documents
        page.goto(f"{base_url}/seim/applications/")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        
        application_link = page.locator('.application, .card, a[href*="application"]').first
        if application_link.count() > 0:
            application_link.click()
            page.wait_for_load_state("networkidle")
            time.sleep(2)
        
        # Step 4: View document list
        documents_section = page.locator('text=/document/i').first
        if documents_section.count() == 0:
            documents_section = page.locator('.documents').first
        if documents_section.count() > 0:
            documents_section.scroll_into_view_if_needed()
            time.sleep(2)
        
        # Step 5: Review specific document
        document_link = page.locator('a[href*="document"], .document-item').first
        if document_link.count() > 0:
            try:
                document_link.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
        
        # Step 6: Show resubmission request button
        resubmit_button = page.locator('button:has-text("Resubmit"), a:has-text("Request Resubmission")').first
        if resubmit_button.count() > 0:
            try:
                resubmit_button.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
        
        # Step 7-8: Show comment area for resubmission
        comment_area = page.locator('textarea, .comment-form').first
        if comment_area.count() > 0:
            try:
                comment_area.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
        
        print("✅ Demo 5 Complete: Coordinator - Request Document Resubmission")
    
    def test_demo_6_coordinator_approve_application(self, page: Page, base_url: str):
        """
        Story 6: Coordinator - Approve Application
        
        Path: Login → Coordinator Dashboard → Review Complete Application → 
              Validate Documents → Approve Application
        """
        # Step 1: Login as coordinator
        login_as_coordinator(page, base_url)
        time.sleep(1)
        
        # Step 2: Access coordinator dashboard
        page.goto(f"{base_url}/seim/coordinator-dashboard/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        # Step 3: Find application ready for review
        page.goto(f"{base_url}/seim/applications/")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        
        # Step 4: Review all application details
        application_link = page.locator('.application, .card, a[href*="application"]').first
        if application_link.count() > 0:
            application_link.click()
            page.wait_for_load_state("networkidle")
            time.sleep(2)
        
        # Step 5: Validate all required documents
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)
        
        # Step 6: Check eligibility criteria
        eligibility_section = page.locator('text=/eligibility|criteria|requirement/i').first
        if eligibility_section.count() > 0:
            try:
                eligibility_section.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
        
        # Step 7: Show approve button
        approve_button = page.locator('button:has-text("Approve"), a:has-text("Approve")').first
        if approve_button.count() > 0:
            try:
                approve_button.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
        
        print("✅ Demo 6 Complete: Coordinator - Approve Application")


@pytest.mark.e2e_playwright
@pytest.mark.video_demo
@pytest.mark.nondestructive
class TestAdminVideoDemos:
    """Admin user story video demos."""
    
    def test_demo_7_admin_create_program(self, page: Page, base_url: str):
        """
        Story 7: Admin - Create New Exchange Program
        
        Path: Login → Admin Dashboard → Program Management → Create Program → 
              Configure Settings → Publish Program
        """
        # Step 1: Login as admin
        login_as_admin(page, base_url)
        time.sleep(1)
        
        # Step 2: Access admin dashboard
        page.goto(f"{base_url}/seim/admin-dashboard/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        # Step 3: Navigate to program management
        page.goto(f"{base_url}/seim/programs/create/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Show program creation form
        
        # Step 4: Click create new program (if button exists)
        create_button = page.locator('button:has-text("Create"), a:has-text("New Program")').first
        if create_button.count() > 0:
            try:
                create_button.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
        
        # Step 5: Fill program details (demonstrate form)
        form_fields = page.locator('input, select, textarea').all()
        for i, field in enumerate(form_fields[:5]):  # Show first 5 fields
            try:
                field_type = field.get_attribute('type') or 'text'
                if field_type not in ['submit', 'button', 'hidden']:
                    try:
                        field.scroll_into_view_if_needed(timeout=2000)
                    except:
                        pass
                    time.sleep(0.5)
            except:
                pass
        
        # Step 6-8: Show configuration options
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
        
        # Step 9: Show save button
        save_button = page.locator('button:has-text("Save"), button[type="submit"]').first
        if save_button.count() > 0:
            try:
                save_button.scroll_into_view_if_needed(timeout=5000)
            except:
                pass  # Button might not be visible, continue anyway
            time.sleep(1)
        
        # Step 10: Navigate to programs list
        page.goto(f"{base_url}/seim/programs/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        print("✅ Demo 7 Complete: Admin - Create New Exchange Program")
    
    def test_demo_8_admin_manage_users(self, page: Page, base_url: str):
        """
        Story 8: Admin - Manage Users & Roles
        
        Path: Login → Admin Dashboard → User Management → View Users → 
              Assign Roles → Update Permissions
        """
        # Step 1: Login as admin
        login_as_admin(page, base_url)
        time.sleep(1)
        
        # Step 2: Access admin dashboard
        page.goto(f"{base_url}/seim/admin-dashboard/")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        
        # Step 3: Navigate to user management
        page.goto(f"{base_url}/seim/user-management/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Show user list
        
        # Step 4: View user list
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        time.sleep(1)
        
        # Step 5: Filter/search for specific user
        search_input = page.locator('input[type="search"], input[placeholder*="search"]').first
        if search_input.count() > 0:
            try:
                search_input.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
        
        # Step 6: View user details
        user_link = page.locator('.user, .card, a[href*="user"]').first
        if user_link.count() > 0:
            try:
                user_link.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
        
        # Step 7: Show role assignment options
        role_section = page.locator('text=/role/i').first
        if role_section.count() == 0:
            role_section = page.locator('.roles, select[name*="role"]').first
        if role_section.count() > 0:
            try:
                role_section.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
        
        print("✅ Demo 8 Complete: Admin - Manage Users & Roles")
    
    def test_demo_9_admin_view_analytics(self, page: Page, base_url: str):
        """
        Story 9: Admin - View Analytics & Reports
        
        Path: Login → Admin Dashboard → Analytics → View Metrics → Export Data → Generate Report
        """
        # Step 1: Login as admin
        login_as_admin(page, base_url)
        time.sleep(1)
        
        # Step 2: Access admin dashboard
        page.goto(f"{base_url}/seim/admin-dashboard/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Show admin dashboard with metrics
        
        # Step 3: Navigate to analytics
        page.goto(f"{base_url}/seim/analytics/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Show analytics page
        
        # Step 4: View overall statistics
        stats_section = page.locator('.statistics, .metrics, .stats').first
        if stats_section.count() > 0:
            try:
                stats_section.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
        
        # Step 5: View program-specific metrics
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        time.sleep(1)
        
        # Step 6: View application status breakdown
        status_section = page.locator('text=/status|breakdown/i').first
        if status_section.count() == 0:
            status_section = page.locator('.status-chart').first
        if status_section.count() > 0:
            try:
                status_section.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
        
        # Step 7: View user activity metrics
        activity_section = page.locator('text=/activity|user/i').first
        if activity_section.count() == 0:
            activity_section = page.locator('.activity-chart').first
        if activity_section.count() > 0:
            try:
                activity_section.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
        
        # Step 8: Show export options
        export_button = page.locator('button:has-text("Export"), a:has-text("Export")').first
        if export_button.count() > 0:
            try:
                export_button.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
        
        print("✅ Demo 9 Complete: Admin - View Analytics & Reports")
    
    def test_demo_10_admin_system_configuration(self, page: Page, base_url: str):
        """
        Story 10: Admin - System Configuration
        
        Path: Login → Admin Dashboard → Settings → Configure System → Update Settings → Verify Changes
        """
        # Step 1: Login as admin
        login_as_admin(page, base_url)
        time.sleep(1)
        
        # Step 2: Access admin dashboard
        page.goto(f"{base_url}/seim/admin-dashboard/")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        
        # Step 3: Navigate to system settings
        page.goto(f"{base_url}/seim/settings/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Show settings page
        
        # Step 4: View current configuration
        page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
        time.sleep(1)
        
        # Step 5: Show notification settings
        notification_section = page.locator('text=/notification/i').first
        if notification_section.count() == 0:
            notification_section = page.locator('.notification-settings').first
        if notification_section.count() > 0:
            try:
                notification_section.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
        
        # Step 6: Show email template configuration
        email_section = page.locator('text=/email|template/i').first
        if email_section.count() > 0:
            try:
                email_section.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
        
        # Step 7: Show system preferences
        preferences_section = page.locator('text=/preference|system/i').first
        if preferences_section.count() > 0:
            try:
                preferences_section.scroll_into_view_if_needed(timeout=5000)
            except:
                pass
            time.sleep(1)
        
        print("✅ Demo 10 Complete: Admin - System Configuration")


@pytest.mark.e2e_playwright
@pytest.mark.video_demo
@pytest.mark.nondestructive
class TestCrossRoleVideoDemos:
    """Cross-role user story video demos."""
    
    def test_demo_11_complete_application_lifecycle(self, page: Page, base_url: str):
        """
        Story 11: Complete Application Lifecycle
        
        Path: Student Creates → Coordinator Reviews → Coordinator Requests Changes → 
              Student Updates → Coordinator Approves
        """
        # Part 1: Student creates application
        login_as_student(page, base_url)
        time.sleep(1)
        
        page.goto(f"{base_url}/seim/applications/create/")
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except:
            pass
        time.sleep(2)
        
        # Part 2: Switch to coordinator view (logout first, then login as coordinator)
        # Clear tokens to simulate logout - login_via_api will navigate to login page itself
        page.evaluate("localStorage.removeItem('seim_access_token'); localStorage.removeItem('seim_refresh_token');")
        time.sleep(1)
        
        # login_as_coordinator will handle navigation to login page
        login_as_coordinator(page, base_url)
        time.sleep(1)
        
        page.goto(f"{base_url}/seim/applications/")
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except:
            pass
        time.sleep(2)
        
        application_link = page.locator('.application, .card, a[href*="application"]').first
        if application_link.count() > 0:
            try:
                application_link.click()
                page.wait_for_load_state("networkidle", timeout=5000)
                time.sleep(2)
            except:
                pass
        
        # Show review and approval workflow
        print("✅ Demo 11 Complete: Complete Application Lifecycle")
    
    def test_demo_12_multi_user_collaboration(self, page: Page, base_url: str):
        """
        Story 12: Multi-User Collaboration
        
        Path: Multiple Students Apply → Coordinator Reviews All → Admin Views Analytics
        """
        # Show student application view
        login_as_student(page, base_url)
        time.sleep(1)
        
        page.goto(f"{base_url}/seim/applications/")
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except:
            pass
        time.sleep(1)
        
        # Show coordinator review view (logout first)
        # Clear tokens to simulate logout - login functions will navigate to login page
        page.evaluate("localStorage.removeItem('seim_access_token'); localStorage.removeItem('seim_refresh_token');")
        time.sleep(1)
        
        # login_as_coordinator will handle navigation to login page
        login_as_coordinator(page, base_url)
        time.sleep(1)
        
        page.goto(f"{base_url}/seim/coordinator-dashboard/")
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except:
            pass
        time.sleep(2)
        
        # Show admin analytics view (logout first)
        # Clear tokens to simulate logout - login functions will navigate to login page
        page.evaluate("localStorage.removeItem('seim_access_token'); localStorage.removeItem('seim_refresh_token');")
        time.sleep(1)
        
        # login_as_admin will handle navigation to login page
        login_as_admin(page, base_url)
        time.sleep(1)
        
        page.goto(f"{base_url}/seim/analytics/")
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except:
            pass
        time.sleep(2)
        
        print("✅ Demo 12 Complete: Multi-User Collaboration")

