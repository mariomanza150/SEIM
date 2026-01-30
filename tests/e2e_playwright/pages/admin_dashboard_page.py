"""
Admin Dashboard Page Object for admin-specific features.
"""

from .dashboard_page import DashboardPage


class AdminDashboardPage(DashboardPage):
    """Page object for admin dashboard page."""
    
    # Admin-specific elements
    ADMIN_MENU = '[data-testid="admin-menu"]'
    USER_MANAGEMENT_LINK = '[data-testid="user-management"], a:has-text("User Management")'
    SYSTEM_SETTINGS_LINK = '[data-testid="system-settings"], a:has-text("System Settings")'
    ANALYTICS_LINK = '[data-testid="analytics"], a:has-text("Analytics")'
    REPORTS_LINK = '[data-testid="reports"], a:has-text("Reports")'
    
    # Statistics
    TOTAL_USERS_STAT = '[data-testid="total-users"]'
    TOTAL_APPLICATIONS_STAT = '[data-testid="total-applications"]'
    TOTAL_PROGRAMS_STAT = '[data-testid="total-programs"]'
    ACTIVE_USERS_STAT = '[data-testid="active-users"]'
    
    # Quick actions
    CREATE_USER_BUTTON = '[data-testid="create-user"], button:has-text("Create User")'
    CREATE_PROGRAM_BUTTON = '[data-testid="create-program"], button:has-text("Create Program")'
    VIEW_ALL_APPLICATIONS_BUTTON = '[data-testid="view-all-applications"], button:has-text("All Applications")'
    
    def navigate_to_admin_dashboard(self) -> None:
        """Navigate to admin dashboard."""
        self.navigate('admin-dashboard/')
    
    def assert_admin_dashboard_loaded(self) -> None:
        """Assert that admin dashboard is loaded."""
        self.assert_url_contains('admin-dashboard')
        self.assert_element_visible(self.DASHBOARD_CONTAINER)
        self.assert_element_visible(self.ADMIN_MENU)
    
    def click_user_management(self) -> None:
        """Navigate to user management."""
        self.click(self.USER_MANAGEMENT_LINK)
    
    def click_analytics(self) -> None:
        """Navigate to analytics."""
        self.click(self.ANALYTICS_LINK)
    
    def click_system_settings(self) -> None:
        """Navigate to system settings."""
        self.click(self.SYSTEM_SETTINGS_LINK)
    
    def get_total_users(self) -> str:
        """
        Get total users count.
        
        Returns:
            Total users count
        """
        return self.get_text(self.TOTAL_USERS_STAT)
    
    def get_total_applications(self) -> str:
        """
        Get total applications count.
        
        Returns:
            Total applications count
        """
        return self.get_text(self.TOTAL_APPLICATIONS_STAT)
    
    def click_create_user(self) -> None:
        """Click create user button."""
        self.click(self.CREATE_USER_BUTTON)
    
    def click_create_program(self) -> None:
        """Click create program button."""
        self.click(self.CREATE_PROGRAM_BUTTON)

