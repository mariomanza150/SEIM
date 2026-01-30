"""
Settings Page Object for user settings.
"""

from .base_page import BasePage


class SettingsPage(BasePage):
    """Page object for settings page."""
    
    # Page elements
    SETTINGS_CONTAINER = '[data-testid="settings"], .settings-container'
    
    # Notification settings
    EMAIL_NOTIFICATIONS_CHECKBOX = '[data-testid="email-notifications"], input[name="email_notifications"]'
    IN_APP_NOTIFICATIONS_CHECKBOX = '[data-testid="in-app-notifications"], input[name="in_app_notifications"]'
    
    # Privacy settings
    PROFILE_VISIBILITY_SELECT = '[data-testid="profile-visibility"], select[name="profile_visibility"]'
    
    # Theme settings
    DARK_MODE_TOGGLE = '[data-testid="dark-mode"], input[name="dark_mode"]'
    LANGUAGE_SELECT = '[data-testid="language"], select[name="language"]'
    
    # Account settings
    CHANGE_PASSWORD_BUTTON = '[data-testid="change-password"], button:has-text("Change Password")'
    DELETE_ACCOUNT_BUTTON = '[data-testid="delete-account"], button:has-text("Delete Account")'
    
    # Buttons
    SAVE_BUTTON = '[data-testid="save-settings"], button:has-text("Save")'
    CANCEL_BUTTON = '[data-testid="cancel"], button:has-text("Cancel")'
    
    # Messages
    SUCCESS_MESSAGE = '.alert-success'
    ERROR_MESSAGE = '.alert-danger'
    
    def navigate_to_settings(self) -> None:
        """Navigate to settings page."""
        self.navigate('settings/')
    
    def assert_settings_page_loaded(self) -> None:
        """Assert that settings page is loaded."""
        self.assert_url_contains('settings')
        self.assert_element_visible(self.SETTINGS_CONTAINER)
    
    def enable_email_notifications(self) -> None:
        """Enable email notifications."""
        self.check(self.EMAIL_NOTIFICATIONS_CHECKBOX)
    
    def disable_email_notifications(self) -> None:
        """Disable email notifications."""
        self.uncheck(self.EMAIL_NOTIFICATIONS_CHECKBOX)
    
    def enable_in_app_notifications(self) -> None:
        """Enable in-app notifications."""
        self.check(self.IN_APP_NOTIFICATIONS_CHECKBOX)
    
    def disable_in_app_notifications(self) -> None:
        """Disable in-app notifications."""
        self.uncheck(self.IN_APP_NOTIFICATIONS_CHECKBOX)
    
    def set_profile_visibility(self, visibility: str) -> None:
        """
        Set profile visibility.
        
        Args:
            visibility: Visibility level (public, private, etc.)
        """
        self.select_option(self.PROFILE_VISIBILITY_SELECT, visibility)
    
    def enable_dark_mode(self) -> None:
        """Enable dark mode."""
        self.check(self.DARK_MODE_TOGGLE)
    
    def disable_dark_mode(self) -> None:
        """Disable dark mode."""
        self.uncheck(self.DARK_MODE_TOGGLE)
    
    def set_language(self, language: str) -> None:
        """
        Set language preference.
        
        Args:
            language: Language code
        """
        self.select_option(self.LANGUAGE_SELECT, language)
    
    def save_settings(self) -> None:
        """Save settings."""
        self.click(self.SAVE_BUTTON)
        self.wait_for_no_loading_indicators()
    
    def click_change_password(self) -> None:
        """Click change password button."""
        self.click(self.CHANGE_PASSWORD_BUTTON)
    
    def has_success_message(self) -> bool:
        """
        Check if success message is displayed.
        
        Returns:
            True if success message exists
        """
        return self.is_visible(self.SUCCESS_MESSAGE, timeout=2000)

