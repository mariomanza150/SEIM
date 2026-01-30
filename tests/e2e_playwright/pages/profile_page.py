"""
Profile Page Object for user profile viewing and editing.
"""

from .base_page import BasePage


class ProfilePage(BasePage):
    """Page object for user profile page."""
    
    # Page elements
    PROFILE_CONTAINER = '[data-testid="profile"], .profile-container'
    PROFILE_PHOTO = '[data-testid="profile-photo"], .profile-photo'
    USERNAME = '[data-testid="username"]'
    EMAIL = '[data-testid="email"]'
    FULL_NAME = '[data-testid="full-name"]'
    
    # Editable fields
    FIRST_NAME_INPUT = '[data-testid="first-name"], input[name="first_name"]'
    LAST_NAME_INPUT = '[data-testid="last-name"], input[name="last_name"]'
    EMAIL_INPUT = '[data-testid="email-input"], input[name="email"]'
    PHONE_INPUT = '[data-testid="phone"], input[name="phone"]'
    BIO_TEXTAREA = '[data-testid="bio"], textarea[name="bio"]'
    
    # Buttons
    EDIT_BUTTON = '[data-testid="edit-profile"], button:has-text("Edit")'
    SAVE_BUTTON = '[data-testid="save-profile"], button:has-text("Save")'
    CANCEL_BUTTON = '[data-testid="cancel"], button:has-text("Cancel")'
    CHANGE_PASSWORD_BUTTON = '[data-testid="change-password"], button:has-text("Change Password")'
    UPLOAD_PHOTO_BUTTON = '[data-testid="upload-photo"], button:has-text("Upload Photo")'
    
    # Messages
    SUCCESS_MESSAGE = '.alert-success'
    ERROR_MESSAGE = '.alert-danger'
    
    def navigate_to_profile(self) -> None:
        """Navigate to profile page."""
        self.navigate('profile/')
    
    def assert_profile_page_loaded(self) -> None:
        """Assert that profile page is loaded."""
        self.assert_url_contains('profile')
        self.assert_element_visible(self.PROFILE_CONTAINER)
    
    def get_username(self) -> str:
        """
        Get username.
        
        Returns:
            Username
        """
        return self.get_text(self.USERNAME)
    
    def get_email(self) -> str:
        """
        Get email.
        
        Returns:
            Email address
        """
        return self.get_text(self.EMAIL)
    
    def get_full_name(self) -> str:
        """
        Get full name.
        
        Returns:
            Full name
        """
        return self.get_text(self.FULL_NAME)
    
    def click_edit_profile(self) -> None:
        """Click edit profile button."""
        self.click(self.EDIT_BUTTON)
    
    def update_first_name(self, first_name: str) -> None:
        """
        Update first name.
        
        Args:
            first_name: New first name
        """
        self.fill(self.FIRST_NAME_INPUT, first_name)
    
    def update_last_name(self, last_name: str) -> None:
        """
        Update last name.
        
        Args:
            last_name: New last name
        """
        self.fill(self.LAST_NAME_INPUT, last_name)
    
    def update_email(self, email: str) -> None:
        """
        Update email.
        
        Args:
            email: New email address
        """
        self.fill(self.EMAIL_INPUT, email)
    
    def update_phone(self, phone: str) -> None:
        """
        Update phone number.
        
        Args:
            phone: New phone number
        """
        self.fill(self.PHONE_INPUT, phone)
    
    def update_bio(self, bio: str) -> None:
        """
        Update bio.
        
        Args:
            bio: New bio text
        """
        self.fill(self.BIO_TEXTAREA, bio)
    
    def save_profile(self) -> None:
        """Save profile changes."""
        self.click(self.SAVE_BUTTON)
        self.wait_for_no_loading_indicators()
    
    def cancel_edit(self) -> None:
        """Cancel profile editing."""
        self.click(self.CANCEL_BUTTON)
    
    def has_success_message(self) -> bool:
        """
        Check if success message is displayed.
        
        Returns:
            True if success message exists
        """
        return self.is_visible(self.SUCCESS_MESSAGE, timeout=2000)

