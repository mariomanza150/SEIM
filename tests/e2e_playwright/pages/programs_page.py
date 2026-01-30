"""
Programs Page Object for program listing and details.
"""

from typing import List
from .base_page import BasePage


class ProgramsPage(BasePage):
    """Page object for programs listing page."""
    
    # Page elements
    PROGRAMS_CONTAINER = '[data-testid="programs-list"], .programs-container'
    PROGRAM_CARD = '.program-card, [data-testid^="program-"]'
    PROGRAM_TITLE = '.program-title, .card-title'
    PROGRAM_DESCRIPTION = '.program-description, .card-text'
    
    # Filters and search
    SEARCH_INPUT = '[data-testid="search"], input[name="search"]'
    FILTER_LANGUAGE = '[data-testid="filter-language"], select[name="language"]'
    FILTER_GPA = '[data-testid="filter-gpa"], input[name="min_gpa"]'
    FILTER_BUTTON = '[data-testid="filter-button"], button:has-text("Filter")'
    CLEAR_FILTERS_BUTTON = '[data-testid="clear-filters"], button:has-text("Clear")'
    
    # Actions
    VIEW_DETAILS_BUTTON = '[data-testid="view-details"], .btn-details'
    APPLY_BUTTON = '[data-testid="apply"], .btn-apply'
    
    def navigate_to_programs(self) -> None:
        """Navigate to programs page."""
        self.navigate('programs/')
    
    def assert_programs_page_loaded(self) -> None:
        """Assert that programs page is loaded."""
        self.assert_url_contains('programs')
        self.assert_element_visible(self.PROGRAMS_CONTAINER)
    
    def search_programs(self, query: str) -> None:
        """
        Search for programs.
        
        Args:
            query: Search query
        """
        self.fill(self.SEARCH_INPUT, query)
        self.page.keyboard.press('Enter')
        self.wait_for_no_loading_indicators()
    
    def filter_by_language(self, language: str) -> None:
        """
        Filter programs by language.
        
        Args:
            language: Language to filter by
        """
        self.select_option(self.FILTER_LANGUAGE, language)
        self.wait_for_no_loading_indicators()
    
    def filter_by_gpa(self, min_gpa: str) -> None:
        """
        Filter programs by minimum GPA.
        
        Args:
            min_gpa: Minimum GPA value
        """
        self.fill(self.FILTER_GPA, min_gpa)
        self.wait_for_no_loading_indicators()
    
    def get_program_count(self) -> int:
        """
        Get count of visible programs.
        
        Returns:
            Number of programs
        """
        return self.page.locator(self.PROGRAM_CARD).count()
    
    def get_program_titles(self) -> List[str]:
        """
        Get all program titles.
        
        Returns:
            List of program titles
        """
        titles = []
        count = self.page.locator(self.PROGRAM_CARD).count()
        for i in range(count):
            title = self.page.locator(self.PROGRAM_CARD).nth(i).locator(self.PROGRAM_TITLE).text_content()
            if title:
                titles.append(title.strip())
        return titles
    
    def click_program_by_name(self, program_name: str) -> None:
        """
        Click on a program by name.
        
        Args:
            program_name: Name of the program
        """
        self.click(f'.program-card:has-text("{program_name}")')
    
    def click_apply_for_program(self, program_name: str) -> None:
        """
        Click apply button for a specific program.
        
        Args:
            program_name: Name of the program
        """
        program_card = self.page.locator(f'.program-card:has-text("{program_name}")')
        program_card.locator(self.APPLY_BUTTON).click()

