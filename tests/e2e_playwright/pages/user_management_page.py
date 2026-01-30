"""
User Management Page Object for admin user management.
"""

from typing import List
from .base_page import BasePage


class UserManagementPage(BasePage):
    """Page object for user management page."""
    
    # Page elements
    USERS_TABLE = '[data-testid="users-table"], .users-table'
    USER_ROW = 'tr[data-testid^="user-"]'
    
    # Search and filters
    SEARCH_INPUT = '[data-testid="search-users"], input[name="search"]'
    FILTER_ROLE = '[data-testid="filter-role"], select[name="role"]'
    FILTER_STATUS = '[data-testid="filter-status"], select[name="status"]'
    
    # Actions
    CREATE_USER_BUTTON = '[data-testid="create-user"], button:has-text("Create User")'
    EDIT_USER_BUTTON = '[data-testid="edit-user"], .btn-edit'
    DELETE_USER_BUTTON = '[data-testid="delete-user"], .btn-delete'
    ASSIGN_ROLE_BUTTON = '[data-testid="assign-role"], .btn-assign-role'
    DEACTIVATE_USER_BUTTON = '[data-testid="deactivate-user"], .btn-deactivate'
    ACTIVATE_USER_BUTTON = '[data-testid="activate-user"], .btn-activate'
    
    # User form modal
    USER_FORM_MODAL = '[data-testid="user-form-modal"], #userFormModal'
    USERNAME_INPUT = '[data-testid="username"], input[name="username"]'
    EMAIL_INPUT = '[data-testid="email"], input[name="email"]'
    ROLE_SELECT = '[data-testid="role"], select[name="role"]'
    SAVE_USER_BUTTON = '[data-testid="save-user"], button:has-text("Save")'
    
    # Messages
    SUCCESS_MESSAGE = '.alert-success'
    ERROR_MESSAGE = '.alert-danger'
    
    def navigate_to_user_management(self) -> None:
        """Navigate to user management page."""
        self.navigate('user-management/')
    
    def assert_user_management_page_loaded(self) -> None:
        """Assert that user management page is loaded."""
        self.assert_url_contains('user-management')
        self.assert_element_visible(self.USERS_TABLE)
    
    def search_users(self, query: str) -> None:
        """
        Search for users.
        
        Args:
            query: Search query
        """
        self.fill(self.SEARCH_INPUT, query)
        self.page.keyboard.press('Enter')
        self.wait_for_no_loading_indicators()
    
    def filter_by_role(self, role: str) -> None:
        """
        Filter users by role.
        
        Args:
            role: Role to filter by
        """
        self.select_option(self.FILTER_ROLE, role)
        self.wait_for_no_loading_indicators()
    
    def filter_by_status(self, status: str) -> None:
        """
        Filter users by status.
        
        Args:
            status: Status to filter by
        """
        self.select_option(self.FILTER_STATUS, status)
        self.wait_for_no_loading_indicators()
    
    def click_create_user(self) -> None:
        """Click create user button."""
        self.click(self.CREATE_USER_BUTTON)
        self.wait_for_selector(self.USER_FORM_MODAL)
    
    def create_user(self, username: str, email: str, role: str) -> None:
        """
        Create a new user.
        
        Args:
            username: Username
            email: Email address
            role: User role
        """
        self.click_create_user()
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.EMAIL_INPUT, email)
        self.select_option(self.ROLE_SELECT, role)
        self.click(self.SAVE_USER_BUTTON)
        self.wait_for_no_loading_indicators()
    
    def get_user_count(self) -> int:
        """
        Get count of visible users.
        
        Returns:
            Number of users
        """
        return self.page.locator(self.USER_ROW).count()
    
    def edit_user(self, username: str) -> None:
        """
        Click edit button for a user.
        
        Args:
            username: Username of the user to edit
        """
        row = self.page.locator(f'tr:has-text("{username}")')
        row.locator(self.EDIT_USER_BUTTON).click()
        self.wait_for_selector(self.USER_FORM_MODAL)
    
    def delete_user(self, username: str) -> None:
        """
        Delete a user.
        
        Args:
            username: Username of the user to delete
        """
        row = self.page.locator(f'tr:has-text("{username}")')
        row.locator(self.DELETE_USER_BUTTON).click()
        # Handle confirmation dialog if present
        self.page.once('dialog', lambda dialog: dialog.accept())
        self.wait_for_no_loading_indicators()
    
    def deactivate_user(self, username: str) -> None:
        """
        Deactivate a user.
        
        Args:
            username: Username of the user to deactivate
        """
        row = self.page.locator(f'tr:has-text("{username}")')
        row.locator(self.DEACTIVATE_USER_BUTTON).click()
        self.wait_for_no_loading_indicators()
    
    def has_user(self, username: str) -> bool:
        """
        Check if a user exists in the list.
        
        Args:
            username: Username to check
        
        Returns:
            True if user exists
        """
        return self.is_visible(f'tr:has-text("{username}")', timeout=2000)

