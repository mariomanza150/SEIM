"""
Authentication Page Object for login, register, and logout.
"""

from .base_page import BasePage


class AuthPage(BasePage):
    """Page object for authentication pages."""

    # Login page locators (Vue: email + password, id="email" / id="password")
    LOGIN_USERNAME_INPUT = '#email, [data-testid="login-email"], input[type="email"]'
    LOGIN_PASSWORD_INPUT = (
        '#password, [data-testid="login-password"], input[type="password"]'
    )
    LOGIN_SUBMIT_BUTTON = 'button[type="submit"], [data-testid="login-submit"]'
    LOGIN_ERROR_MESSAGE = ".alert-danger, .error-message"

    # Register page locators
    REGISTER_USERNAME_INPUT = '[data-testid="register-username"], [name="username"]'
    REGISTER_EMAIL_INPUT = '[data-testid="register-email"], [name="email"]'
    REGISTER_PASSWORD_INPUT = '[data-testid="register-password"], [name="password"]'
    REGISTER_CONFIRM_PASSWORD_INPUT = (
        '[data-testid="register-password2"], [name="password2"]'
    )
    REGISTER_FIRST_NAME_INPUT = '[data-testid="register-first-name"], [name="first_name"]'
    REGISTER_LAST_NAME_INPUT = '[data-testid="register-last-name"], [name="last_name"]'
    REGISTER_MIDDLE_NAME_INPUT = (
        '[data-testid="register-middle-name"], [name="middle_name"]'
    )
    REGISTER_MOTHERS_LAST_NAME_INPUT = (
        '[data-testid="register-mothers-last-name"], [name="mothers_last_name"]'
    )
    REGISTER_AGREE_TERMS_CHECKBOX = '[name="agree_terms"]'
    REGISTER_SUBMIT_BUTTON = '[data-testid="register-submit"], button[type="submit"]'
    REGISTER_SUCCESS_MESSAGE = (
        '[data-testid="register-success"], .alert-success'
    )
    REGISTER_ERROR_MESSAGE = ".alert-danger, .error-message"

    # Common elements
    LOGOUT_BUTTON = (
        '[data-testid="logout-button"], [data-testid="logout-link"], a:has-text("Logout")'
    )
    USER_MENU = (
        '[data-testid="user-menu"], #userDropdown, a[aria-label*="User menu" i]'
    )

    def navigate_to_login(self) -> None:
        """Navigate to Vue login page."""
        self.navigate("login")

    def navigate_to_register(self) -> None:
        """Navigate to register page."""
        self.navigate("register/")

    def login(
        self, username_or_email: str, password: str, *, expect_success: bool = True
    ) -> None:
        """
        Login with credentials (Vue: email in first field).
        Args:
            username_or_email: Email or username
            password: Password
            expect_success: Wait for the authenticated shell when True
        """
        self.fill(self.LOGIN_USERNAME_INPUT, username_or_email)
        self.fill(self.LOGIN_PASSWORD_INPUT, password)
        self.click(self.LOGIN_SUBMIT_BUTTON)
        if expect_success:
            self.page.locator(self.USER_MENU).wait_for(state="visible", timeout=15000)
        else:
            self.wait_for_no_loading_indicators()

    def register(
        self,
        username: str,
        email: str,
        password: str,
        confirm_password: str,
        first_name: str = "",
        last_name: str = "",
        agree_terms: bool = True,
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
        self.fill(self.REGISTER_FIRST_NAME_INPUT, first_name or "Test")
        self.fill(self.REGISTER_MIDDLE_NAME_INPUT, "Q")
        self.fill(self.REGISTER_LAST_NAME_INPUT, last_name or "User")
        self.fill(self.REGISTER_MOTHERS_LAST_NAME_INPUT, "Garcia")

        if agree_terms and self.is_visible(self.REGISTER_AGREE_TERMS_CHECKBOX, timeout=1000):
            self.check(self.REGISTER_AGREE_TERMS_CHECKBOX)

        self.click(self.REGISTER_SUBMIT_BUTTON)
        self.wait_for_no_loading_indicators()

    def logout(self) -> None:
        """Logout from the application."""
        try:
            menu = self.page.locator(self.USER_MENU).first
            if menu.count() and menu.is_visible():
                menu.click(timeout=5000)
            logout_btn = self.page.locator('[data-testid="logout-link"]').first
            if logout_btn.count():
                # Bootstrap dropdown items stay display:none until shown.
                logout_btn.evaluate("el => el.click()")
            else:
                self.click(self.LOGOUT_BUTTON, timeout=5000)
            self.page.wait_for_url("**/login**", timeout=15000)
            self.wait_for_load()
        except Exception:
            self.page.evaluate(
                "() => { localStorage.removeItem('access_token'); localStorage.removeItem('refresh_token'); }"
            )
            self.navigate("login/")

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
        """Assert that Vue login page is loaded."""
        self.assert_url_contains("login")
        self.assert_element_visible(self.LOGIN_PASSWORD_INPUT)
        self.assert_element_visible(self.LOGIN_USERNAME_INPUT)

    def assert_register_page_loaded(self) -> None:
        """Assert that register page is loaded."""
        self.assert_url_contains("register")
        self.assert_element_visible(self.REGISTER_USERNAME_INPUT)
        self.assert_element_visible(self.REGISTER_EMAIL_INPUT)

    def assert_logged_in(self) -> None:
        """Assert that user is logged in."""
        self.assert_element_visible(self.USER_MENU)

    def assert_logged_out(self) -> None:
        """Assert that user is logged out."""
        self.assert_element_hidden(self.USER_MENU)
