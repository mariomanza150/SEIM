"""
Dashboard Page Object for the main dashboard.
"""

from .base_page import BasePage


class DashboardPage(BasePage):
    """Page object for dashboard pages (all roles)."""
    
    # Common dashboard elements
    DASHBOARD_CONTAINER = '#dashboard-content, [data-testid="dashboard"]'
    WELCOME_MESSAGE = 'h1, .welcome-message'
    NAVIGATION_MENU = 'nav, .navbar'
    USER_MENU = '[data-testid="user-menu"]'
    NOTIFICATIONS_BADGE = '[data-testid="notifications-badge"]'
    
    # Quick actions
    QUICK_ACTIONS_CONTAINER = '.quick-actions, [data-testid="quick-actions"]'
    CREATE_APPLICATION_BUTTON = '[data-testid="create-application"], a:has-text("Create Application")'
    VIEW_PROGRAMS_BUTTON = '[data-testid="view-programs"], a:has-text("View Programs")'
    MY_APPLICATIONS_BUTTON = '[data-testid="my-applications"], a:has-text("My Applications")'
    
    # Statistics cards
    STATS_CONTAINER = '.stats-container, [data-testid="stats"]'
    APPLICATIONS_COUNT = '[data-testid="applications-count"]'
    PROGRAMS_COUNT = '[data-testid="programs-count"]'
    DOCUMENTS_COUNT = '[data-testid="documents-count"]'
    
    def navigate_to_dashboard(self) -> None:
        """Navigate to dashboard page."""
        self.navigate('dashboard/')
    
    def assert_dashboard_loaded(self) -> None:
        """Assert that dashboard is loaded."""
        self.assert_url_contains('dashboard')
        self.assert_element_visible(self.DASHBOARD_CONTAINER)
    
    def get_welcome_message(self) -> str:
        """
        Get welcome message text.
        
        Returns:
            Welcome message
        """
        return self.get_text(self.WELCOME_MESSAGE)
    
    def click_create_application(self) -> None:
        """Click create application button."""
        self.click(self.CREATE_APPLICATION_BUTTON)
    
    def click_view_programs(self) -> None:
        """Click view programs button."""
        self.click(self.VIEW_PROGRAMS_BUTTON)
    
    def click_my_applications(self) -> None:
        """Click my applications button."""
        self.click(self.MY_APPLICATIONS_BUTTON)
    
    def get_applications_count(self) -> str:
        """
        Get applications count.
        
        Returns:
            Applications count
        """
        return self.get_text(self.APPLICATIONS_COUNT)
    
    def get_notifications_count(self) -> str:
        """
        Get notifications count.
        
        Returns:
            Notifications count
        """
        return self.get_text(self.NOTIFICATIONS_BADGE)
    
    def has_notifications(self) -> bool:
        """
        Check if there are notifications.
        
        Returns:
            True if notifications exist
        """
        return self.is_visible(self.NOTIFICATIONS_BADGE, timeout=2000)

