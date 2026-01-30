"""
Example Page Object demonstrating best practices.

This shows how to structure a page object with:
- Clear locator definitions
- High-level action methods
- Verification methods
- Proper error handling
"""

from tests.e2e_playwright.pages.base_page import BasePage


class ExamplePage(BasePage):
    """
    Example page object for demonstration.
    
    This is a template showing best practices for creating page objects.
    """
    
    # Locators - defined as class constants
    # Use data-testid attributes when available
    TITLE = '[data-testid="page-title"], h1'
    SEARCH_INPUT = '[data-testid="search"], input[name="search"]'
    SEARCH_BUTTON = '[data-testid="search-button"], button:has-text("Search")'
    RESULTS_CONTAINER = '[data-testid="results"], .results-container'
    RESULT_ITEM = '[data-testid^="result-"], .result-item'
    
    # Actions - high-level methods for user actions
    
    def navigate_to_page(self) -> None:
        """Navigate to this page."""
        self.navigate('example/')
    
    def search_for(self, query: str) -> None:
        """
        Perform a search.
        
        Args:
            query: Search query text
        """
        self.fill(self.SEARCH_INPUT, query)
        self.click(self.SEARCH_BUTTON)
        self.wait_for_no_loading_indicators()
    
    def get_result_count(self) -> int:
        """
        Get number of search results.
        
        Returns:
            Number of results displayed
        """
        return self.page.locator(self.RESULT_ITEM).count()
    
    def click_first_result(self) -> None:
        """Click the first search result."""
        self.page.locator(self.RESULT_ITEM).first.click()
    
    # Verifications - methods to check page state
    
    def assert_page_loaded(self) -> None:
        """Assert that page is loaded and visible."""
        self.assert_url_contains('example')
        self.assert_element_visible(self.TITLE)
    
    def assert_has_results(self) -> None:
        """Assert that search results are displayed."""
        self.assert_element_visible(self.RESULTS_CONTAINER)
        assert self.get_result_count() > 0, "Expected at least one result"
    
    def assert_no_results(self) -> None:
        """Assert that no search results are displayed."""
        assert self.get_result_count() == 0, "Expected no results"

