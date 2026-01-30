"""
Coordinator Dashboard Page Object for coordinator-specific features.
"""

from .dashboard_page import DashboardPage


class CoordinatorDashboardPage(DashboardPage):
    """Page object for coordinator dashboard page."""
    
    # Coordinator-specific elements
    COORDINATOR_MENU = '[data-testid="coordinator-menu"]'
    PENDING_APPLICATIONS_LINK = '[data-testid="pending-applications"], a:has-text("Pending Applications")'
    REVIEW_DOCUMENTS_LINK = '[data-testid="review-documents"], a:has-text("Review Documents")'
    MANAGE_PROGRAMS_LINK = '[data-testid="manage-programs"], a:has-text("Manage Programs")'
    
    # Statistics
    PENDING_REVIEWS_STAT = '[data-testid="pending-reviews"]'
    APPROVED_COUNT_STAT = '[data-testid="approved-count"]'
    REJECTED_COUNT_STAT = '[data-testid="rejected-count"]'
    DOCUMENTS_TO_REVIEW_STAT = '[data-testid="documents-to-review"]'
    
    # Quick actions
    REVIEW_APPLICATION_BUTTON = '[data-testid="review-application"], button:has-text("Review")'
    BULK_APPROVE_BUTTON = '[data-testid="bulk-approve"], button:has-text("Bulk Approve")'
    BULK_REJECT_BUTTON = '[data-testid="bulk-reject"], button:has-text("Bulk Reject")'
    
    # Applications list
    APPLICATIONS_TABLE = '[data-testid="applications-table"], .applications-table'
    APPLICATION_ROW = 'tr[data-testid^="application-"]'
    
    def navigate_to_coordinator_dashboard(self) -> None:
        """Navigate to coordinator dashboard."""
        self.navigate('coordinator-dashboard/')
    
    def assert_coordinator_dashboard_loaded(self) -> None:
        """Assert that coordinator dashboard is loaded."""
        self.assert_url_contains('coordinator-dashboard')
        self.assert_element_visible(self.DASHBOARD_CONTAINER)
        self.assert_element_visible(self.COORDINATOR_MENU)
    
    def click_pending_applications(self) -> None:
        """Navigate to pending applications."""
        self.click(self.PENDING_APPLICATIONS_LINK)
    
    def click_review_documents(self) -> None:
        """Navigate to document review."""
        self.click(self.REVIEW_DOCUMENTS_LINK)
    
    def get_pending_reviews_count(self) -> str:
        """
        Get pending reviews count.
        
        Returns:
            Pending reviews count
        """
        return self.get_text(self.PENDING_REVIEWS_STAT)
    
    def get_approved_count(self) -> str:
        """
        Get approved applications count.
        
        Returns:
            Approved count
        """
        return self.get_text(self.APPROVED_COUNT_STAT)
    
    def review_application(self, application_id: str) -> None:
        """
        Click review button for an application.
        
        Args:
            application_id: Application ID
        """
        row = self.page.locator(f'[data-testid="application-{application_id}"]')
        row.locator(self.REVIEW_APPLICATION_BUTTON).click()

