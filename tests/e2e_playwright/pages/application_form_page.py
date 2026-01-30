"""
Application Form Page Object for creating and editing applications.
"""

from .base_page import BasePage


class ApplicationFormPage(BasePage):
    """Page object for application form page."""
    
    # Form elements
    FORM_CONTAINER = '[data-testid="application-form"], form'
    PROGRAM_SELECT = '[data-testid="program-select"], select[name="program"]'
    PERSONAL_STATEMENT = '[data-testid="personal-statement"], textarea[name="personal_statement"]'
    ACADEMIC_BACKGROUND = '[data-testid="academic-background"], textarea[name="academic_background"]'
    LANGUAGE_PROFICIENCY = '[data-testid="language-proficiency"], textarea[name="language_proficiency"]'
    FINANCIAL_PLAN = '[data-testid="financial-plan"], textarea[name="financial_plan"]'
    MOTIVATION = '[data-testid="motivation"], textarea[name="motivation"]'
    
    # Buttons
    SAVE_DRAFT_BUTTON = '[data-testid="save-draft"], button:has-text("Save Draft")'
    SUBMIT_BUTTON = '[data-testid="submit-application"], button:has-text("Submit")'
    CANCEL_BUTTON = '[data-testid="cancel"], button:has-text("Cancel")'
    
    # Validation messages
    ERROR_MESSAGE = '.error-message, .invalid-feedback'
    SUCCESS_MESSAGE = '.success-message, .alert-success'
    
    def navigate_to_application_form(self, application_id: str = None) -> None:
        """
        Navigate to application form.
        
        Args:
            application_id: Optional application ID for editing
        """
        if application_id:
            self.navigate(f'applications/{application_id}/edit/')
        else:
            self.navigate('applications/create/')
    
    def assert_form_loaded(self) -> None:
        """Assert that application form is loaded."""
        self.assert_element_visible(self.FORM_CONTAINER)
    
    def select_program(self, program_name: str) -> None:
        """
        Select a program from dropdown.
        
        Args:
            program_name: Name of the program
        """
        self.page.locator(self.PROGRAM_SELECT).select_option(label=program_name)
    
    def fill_personal_statement(self, text: str) -> None:
        """
        Fill personal statement field.
        
        Args:
            text: Personal statement text
        """
        self.fill(self.PERSONAL_STATEMENT, text)
    
    def fill_academic_background(self, text: str) -> None:
        """
        Fill academic background field.
        
        Args:
            text: Academic background text
        """
        self.fill(self.ACADEMIC_BACKGROUND, text)
    
    def fill_language_proficiency(self, text: str) -> None:
        """
        Fill language proficiency field.
        
        Args:
            text: Language proficiency text
        """
        self.fill(self.LANGUAGE_PROFICIENCY, text)
    
    def fill_financial_plan(self, text: str) -> None:
        """
        Fill financial plan field.
        
        Args:
            text: Financial plan text
        """
        self.fill(self.FINANCIAL_PLAN, text)
    
    def fill_motivation(self, text: str) -> None:
        """
        Fill motivation field.
        
        Args:
            text: Motivation text
        """
        self.fill(self.MOTIVATION, text)
    
    def fill_complete_application(
        self,
        program_name: str,
        personal_statement: str,
        academic_background: str,
        language_proficiency: str,
        financial_plan: str,
        motivation: str = ''
    ) -> None:
        """
        Fill complete application form.
        
        Args:
            program_name: Program to select
            personal_statement: Personal statement text
            academic_background: Academic background text
            language_proficiency: Language proficiency text
            financial_plan: Financial plan text
            motivation: Motivation text (optional)
        """
        self.select_program(program_name)
        self.fill_personal_statement(personal_statement)
        self.fill_academic_background(academic_background)
        self.fill_language_proficiency(language_proficiency)
        self.fill_financial_plan(financial_plan)
        if motivation:
            self.fill_motivation(motivation)
    
    def save_as_draft(self) -> None:
        """Save application as draft."""
        self.click(self.SAVE_DRAFT_BUTTON)
        self.wait_for_no_loading_indicators()
    
    def submit_application(self) -> None:
        """Submit application."""
        self.click(self.SUBMIT_BUTTON)
        self.wait_for_no_loading_indicators()
    
    def cancel(self) -> None:
        """Cancel application form."""
        self.click(self.CANCEL_BUTTON)
    
    def get_error_message(self) -> str:
        """
        Get error message.
        
        Returns:
            Error message text
        """
        return self.get_text(self.ERROR_MESSAGE)
    
    def get_success_message(self) -> str:
        """
        Get success message.
        
        Returns:
            Success message text
        """
        return self.get_text(self.SUCCESS_MESSAGE)
    
    def has_validation_errors(self) -> bool:
        """
        Check if form has validation errors.
        
        Returns:
            True if errors exist
        """
        return self.is_visible(self.ERROR_MESSAGE, timeout=2000)

