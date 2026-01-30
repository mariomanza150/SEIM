"""
Authentication Page Object for login, register, and logout.
"""

from .base_page import BasePage


class AuthPage(BasePage):
    """Page object for authentication pages."""
    
    # Login page locators
    LOGIN_USERNAME_INPUT = '[name="username"]'
    LOGIN_PASSWORD_INPUT = '[name="password"]'
    LOGIN_SUBMIT_BUTTON = 'button[type="submit"]'
    LOGIN_ERROR_MESSAGE = '.alert-danger, .error-message'
    
    # Register page locators
    REGISTER_USERNAME_INPUT = '[name="username"]'
    REGISTER_EMAIL_INPUT = '[name="email"]'
    REGISTER_PASSWORD_INPUT = '[name="password"]'
    REGISTER_CONFIRM_PASSWORD_INPUT = '[name="confirm_password"]'
    REGISTER_FIRST_NAME_INPUT = '[name="first_name"]'
    REGISTER_LAST_NAME_INPUT = '[name="last_name"]'
    REGISTER_AGREE_TERMS_CHECKBOX = '[name="agree_terms"]'
    REGISTER_SUBMIT_BUTTON = 'button[type="submit"]'
    REGISTER_SUCCESS_MESSAGE = '.alert-success'
    REGISTER_ERROR_MESSAGE = '.alert-danger, .error-message'
    
    # Common elements
    LOGOUT_BUTTON = '[data-testid="logout-button"], a:has-text("Logout")'
    USER_MENU = '[data-testid="user-menu"]'
    
    def navigate_to_login(self) -> None:
        """Navigate to login page."""
        self.navigate('login/')
    
    def navigate_to_register(self) -> None:
        """Navigate to register page."""
        self.navigate('register/')
    
    def login(self, username: str, password: str) -> None:
        """
        Login with credentials.
        
        Args:
            username: Username
            password: Password
        """
        self.fill(self.LOGIN_USERNAME_INPUT, username)
        self.fill(self.LOGIN_PASSWORD_INPUT, password)
        self.click(self.LOGIN_SUBMIT_BUTTON)
        self.wait_for_no_loading_indicators()
    
    def register(
        self,
        username: str,
        email: str,
        password: str,
        confirm_password: str,
        first_name: str = '',
        last_name: str = '',
        agree_terms: bool = True
    ) -> None:
        """
        Register a new user.
        
        Args:
            username: Username
            email: Email address
            password: Password
            confirm_password: Password confirmation
            first_name: First name (optional)
            last_name: Last name (optional)
            agree_terms: Whether to agree to terms
        """
        self.fill(self.REGISTER_USERNAME_INPUT, username)
        self.fill(self.REGISTER_EMAIL_INPUT, email)
        self.fill(self.REGISTER_PASSWORD_INPUT, password)
        self.fill(self.REGISTER_CONFIRM_PASSWORD_INPUT, confirm_password)
        
        if first_name:
            self.fill(self.REGISTER_FIRST_NAME_INPUT, first_name)
        if last_name:
            self.fill(self.REGISTER_LAST_NAME_INPUT, last_name)
        
        if agree_terms:
            self.check(self.REGISTER_AGREE_TERMS_CHECKBOX)
        
        self.click(self.REGISTER_SUBMIT_BUTTON)
        self.wait_for_no_loading_indicators()
    
    def logout(self) -> None:
        """Logout from the application."""
        try:
            self.click(self.LOGOUT_BUTTON, timeout=5000)
            self.wait_for_load()
        except:
            # If button not found, navigate to logout URL
            self.navigate('logout/')
    
    def is_logged_in(self) -> bool:
        """
        Check if user is logged in.
        
        Returns:
            True if logged in, False otherwise
        """
        return self.is_visible(self.USER_MENU, timeout=2000)
    
    def get_login_error(self) -> str:
        """
        Get login error message.
        
        Returns:
            Error message text
        """
        return self.get_text(self.LOGIN_ERROR_MESSAGE)
    
    def get_register_success_message(self) -> str:
        """
        Get registration success message.
        
        Returns:
            Success message text
        """
        return self.get_text(self.REGISTER_SUCCESS_MESSAGE)
    
    def get_register_error(self) -> str:
        """
        Get registration error message.
        
        Returns:
            Error message text
        """
        return self.get_text(self.REGISTER_ERROR_MESSAGE)
    
    def assert_login_page_loaded(self) -> None:
        """Assert that login page is loaded."""
        self.assert_url_contains('login')
        self.assert_element_visible(self.LOGIN_USERNAME_INPUT)
        self.assert_element_visible(self.LOGIN_PASSWORD_INPUT)
    
    def assert_register_page_loaded(self) -> None:
        """Assert that register page is loaded."""
        self.assert_url_contains('register')
        self.assert_element_visible(self.REGISTER_USERNAME_INPUT)
        self.assert_element_visible(self.REGISTER_EMAIL_INPUT)
    
    def assert_logged_in(self) -> None:
        """Assert that user is logged in."""
        self.assert_element_visible(self.USER_MENU)
    
    def assert_logged_out(self) -> None:
        """Assert that user is logged out."""
        self.assert_element_hidden(self.USER_MENU)

