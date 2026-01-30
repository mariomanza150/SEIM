"""
Base Page Object for all page objects in E2E tests.

Provides common functionality and patterns for all page objects.
"""

from typing import Optional

from playwright.sync_api import Page, expect


class BasePage:
    """Base class for all page objects."""
    
    def __init__(self, page: Page, base_url: str):
        """
        Initialize base page.
        
        Args:
            page: Playwright page object
            base_url: Base URL of the application
        """
        self.page = page
        self.base_url = base_url
    
    def navigate(self, path: str = '') -> None:
        """
        Navigate to a specific path.
        
        Args:
            path: Path to navigate to (relative to base_url)
        """
        url = f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url
        self.page.goto(url)
        self.wait_for_load()
    
    def wait_for_load(self, timeout: int = 30000) -> None:
        """
        Wait for page to be fully loaded.
        
        Args:
            timeout: Timeout in milliseconds
        """
        self.page.wait_for_load_state('networkidle', timeout=timeout)
    
    def wait_for_selector(self, selector: str, timeout: int = 30000, state: str = 'visible') -> None:
        """
        Wait for a selector to reach a specific state.
        
        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
            state: Element state to wait for
        """
        self.page.wait_for_selector(selector, state=state, timeout=timeout)
    
    def click(self, selector: str, timeout: int = 30000) -> None:
        """
        Click an element.
        
        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
        """
        self.page.locator(selector).click(timeout=timeout)
    
    def fill(self, selector: str, value: str, timeout: int = 30000) -> None:
        """
        Fill an input field.
        
        Args:
            selector: CSS selector
            value: Value to fill
            timeout: Timeout in milliseconds
        """
        self.page.locator(selector).fill(value, timeout=timeout)
    
    def select_option(self, selector: str, value: str, timeout: int = 30000) -> None:
        """
        Select an option from a dropdown.
        
        Args:
            selector: CSS selector
            value: Value to select
            timeout: Timeout in milliseconds
        """
        self.page.locator(selector).select_option(value, timeout=timeout)
    
    def check(self, selector: str, timeout: int = 30000) -> None:
        """
        Check a checkbox.
        
        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
        """
        self.page.locator(selector).check(timeout=timeout)
    
    def uncheck(self, selector: str, timeout: int = 30000) -> None:
        """
        Uncheck a checkbox.
        
        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
        """
        self.page.locator(selector).uncheck(timeout=timeout)
    
    def get_text(self, selector: str, timeout: int = 30000) -> str:
        """
        Get text content of an element.
        
        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
        
        Returns:
            Text content of the element
        """
        return self.page.locator(selector).text_content(timeout=timeout) or ''
    
    def get_value(self, selector: str, timeout: int = 30000) -> str:
        """
        Get input value.
        
        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
        
        Returns:
            Input value
        """
        return self.page.locator(selector).input_value(timeout=timeout)
    
    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """
        Check if element is visible.
        
        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
        
        Returns:
            True if visible, False otherwise
        """
        try:
            self.page.locator(selector).wait_for(state='visible', timeout=timeout)
            return True
        except:
            return False
    
    def is_hidden(self, selector: str, timeout: int = 5000) -> bool:
        """
        Check if element is hidden.
        
        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
        
        Returns:
            True if hidden, False otherwise
        """
        try:
            self.page.locator(selector).wait_for(state='hidden', timeout=timeout)
            return True
        except:
            return False
    
    def screenshot(self, path: str, full_page: bool = True) -> None:
        """
        Take a screenshot.
        
        Args:
            path: Path to save screenshot
            full_page: Whether to capture full page
        """
        self.page.screenshot(path=path, full_page=full_page)
    
    def assert_url_contains(self, text: str, timeout: int = 5000) -> None:
        """
        Assert that URL contains text.
        
        Args:
            text: Text to check for in URL
            timeout: Timeout in milliseconds
        """
        expect(self.page).to_have_url(f"**{text}**", timeout=timeout)
    
    def assert_title_contains(self, text: str, timeout: int = 5000) -> None:
        """
        Assert that title contains text.
        
        Args:
            text: Text to check for in title
            timeout: Timeout in milliseconds
        """
        expect(self.page).to_have_title(f"*{text}*", timeout=timeout)
    
    def assert_element_visible(self, selector: str, timeout: int = 5000) -> None:
        """
        Assert that element is visible.
        
        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
        """
        expect(self.page.locator(selector)).to_be_visible(timeout=timeout)
    
    def assert_element_hidden(self, selector: str, timeout: int = 5000) -> None:
        """
        Assert that element is hidden.
        
        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
        """
        expect(self.page.locator(selector)).to_be_hidden(timeout=timeout)
    
    def assert_text(self, selector: str, text: str, timeout: int = 5000) -> None:
        """
        Assert that element contains text.
        
        Args:
            selector: CSS selector
            text: Expected text
            timeout: Timeout in milliseconds
        """
        expect(self.page.locator(selector)).to_contain_text(text, timeout=timeout)
    
    def wait_for_no_loading_indicators(self, timeout: int = 30000) -> None:
        """
        Wait for all loading indicators to disappear.
        
        Args:
            timeout: Timeout in milliseconds
        """
        try:
            self.page.wait_for_selector(
                '.spinner, .loading, [data-testid="loading"]',
                state='hidden',
                timeout=timeout
            )
        except:
            pass  # No loading indicators found
    
    def scroll_to_element(self, selector: str) -> None:
        """
        Scroll to an element.
        
        Args:
            selector: CSS selector
        """
        self.page.locator(selector).scroll_into_view_if_needed()
    
    def hover(self, selector: str, timeout: int = 30000) -> None:
        """
        Hover over an element.
        
        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds
        """
        self.page.locator(selector).hover(timeout=timeout)

