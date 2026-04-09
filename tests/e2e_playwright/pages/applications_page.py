"""
Applications Page Object for application listing and details.
"""

from typing import List
from .base_page import BasePage


class ApplicationsPage(BasePage):
    """Page object for applications listing page."""
    
    # Page elements
    APPLICATIONS_CONTAINER = '[data-testid="applications-list"], .applications-container'
    APPLICATION_CARD = '.application-card, [data-testid^="application-"]'
    APPLICATION_TITLE = '.application-title, .card-title'
    APPLICATION_STATUS = '.application-status, .badge-status'
    
    # Actions
    CREATE_APPLICATION_BUTTON = '[data-testid="create-application"], a:has-text("Create Application")'
    VIEW_DETAILS_BUTTON = '[data-testid="view-details"], .btn-details'
    EDIT_BUTTON = '[data-testid="edit"], .btn-edit'
    DELETE_BUTTON = '[data-testid="delete"], .btn-delete'
    
    # Filters
    FILTER_STATUS = '[data-testid="filter-status"], select[name="status"]'
    FILTER_PROGRAM = '[data-testid="filter-program"], select[name="program"]'
    
    def navigate_to_applications(self) -> None:
        """Navigate to applications page."""
        self.navigate('seim/applications/')
    
    def navigate_to_application_create(self) -> None:
        """Navigate to application creation page."""
        self.navigate('seim/applications/new/')
    
    def assert_applications_page_loaded(self) -> None:
        """Assert that applications page is loaded."""
        self.assert_url_contains('applications')
        self.assert_element_visible(self.APPLICATIONS_CONTAINER)
    
    def click_create_application(self) -> None:
        """Click create application button."""
        self.click(self.CREATE_APPLICATION_BUTTON)
    
    def get_application_count(self) -> int:
        """
        Get count of visible applications.
        
        Returns:
            Number of applications
        """
        return self.page.locator(self.APPLICATION_CARD).count()
    
    def get_application_titles(self) -> List[str]:
        """
        Get all application titles.
        
        Returns:
            List of application titles
        """
        titles = []
        count = self.page.locator(self.APPLICATION_CARD).count()
        for i in range(count):
            title = self.page.locator(self.APPLICATION_CARD).nth(i).locator(self.APPLICATION_TITLE).text_content()
            if title:
                titles.append(title.strip())
        return titles
    
    def get_application_status(self, application_name: str) -> str:
        """
        Get status of an application.
        
        Args:
            application_name: Name of the application
        
        Returns:
            Application status
        """
        card = self.page.locator(f'.application-card:has-text("{application_name}")')
        status = card.locator(self.APPLICATION_STATUS).text_content()
        return status.strip() if status else ''
    
    def click_application_by_name(self, application_name: str) -> None:
        """
        Click on an application by name.
        
        Args:
            application_name: Name of the application
        """
        self.click(f'.application-card:has-text("{application_name}")')
    
    def edit_application(self, application_name: str) -> None:
        """
        Click edit button for an application.
        
        Args:
            application_name: Name of the application
        """
        card = self.page.locator(f'.application-card:has-text("{application_name}")')
        card.locator(self.EDIT_BUTTON).click()
    
    def filter_by_status(self, status: str) -> None:
        """
        Filter applications by status.
        
        Args:
            status: Status to filter by
        """
        self.select_option(self.FILTER_STATUS, status)
        self.wait_for_no_loading_indicators()

