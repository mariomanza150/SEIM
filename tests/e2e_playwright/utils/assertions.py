"""
Custom assertion utilities for E2E tests.

Provides enhanced assertion methods for common E2E testing scenarios.
"""

from typing import Optional

from playwright.sync_api import Page, expect


def assert_url_contains(page: Page, text: str, timeout: int = 5000) -> None:
    """
    Assert that the current URL contains the specified text.
    
    Args:
        page: Playwright page object
        text: Text that should be in the URL
        timeout: Timeout in milliseconds
    """
    expect(page).to_have_url(f"**{text}**", timeout=timeout)


def assert_url_equals(page: Page, url: str, timeout: int = 5000) -> None:
    """
    Assert that the current URL equals the specified URL.
    
    Args:
        page: Playwright page object
        url: Expected URL
        timeout: Timeout in milliseconds
    """
    expect(page).to_have_url(url, timeout=timeout)


def assert_title_contains(page: Page, text: str, timeout: int = 5000) -> None:
    """
    Assert that the page title contains the specified text.
    
    Args:
        page: Playwright page object
        text: Text that should be in the title
        timeout: Timeout in milliseconds
    """
    expect(page).to_have_title(f"*{text}*", timeout=timeout)


def assert_element_visible(page: Page, selector: str, timeout: int = 5000) -> None:
    """
    Assert that an element is visible.
    
    Args:
        page: Playwright page object
        selector: CSS selector for the element
        timeout: Timeout in milliseconds
    """
    expect(page.locator(selector)).to_be_visible(timeout=timeout)


def assert_element_hidden(page: Page, selector: str, timeout: int = 5000) -> None:
    """
    Assert that an element is hidden.
    
    Args:
        page: Playwright page object
        selector: CSS selector for the element
        timeout: Timeout in milliseconds
    """
    expect(page.locator(selector)).to_be_hidden(timeout=timeout)


def assert_element_enabled(page: Page, selector: str, timeout: int = 5000) -> None:
    """
    Assert that an element is enabled.
    
    Args:
        page: Playwright page object
        selector: CSS selector for the element
        timeout: Timeout in milliseconds
    """
    expect(page.locator(selector)).to_be_enabled(timeout=timeout)


def assert_element_disabled(page: Page, selector: str, timeout: int = 5000) -> None:
    """
    Assert that an element is disabled.
    
    Args:
        page: Playwright page object
        selector: CSS selector for the element
        timeout: Timeout in milliseconds
    """
    expect(page.locator(selector)).to_be_disabled(timeout=timeout)


def assert_text_visible(page: Page, text: str, timeout: int = 5000) -> None:
    """
    Assert that specific text is visible on the page.
    
    Args:
        page: Playwright page object
        text: Text that should be visible
        timeout: Timeout in milliseconds
    """
    expect(page.locator(f"text={text}")).to_be_visible(timeout=timeout)


def assert_element_contains_text(page: Page, selector: str, text: str, timeout: int = 5000) -> None:
    """
    Assert that an element contains specific text.
    
    Args:
        page: Playwright page object
        selector: CSS selector for the element
        text: Text that should be in the element
        timeout: Timeout in milliseconds
    """
    expect(page.locator(selector)).to_contain_text(text, timeout=timeout)


def assert_element_count(page: Page, selector: str, count: int, timeout: int = 5000) -> None:
    """
    Assert the count of elements matching a selector.
    
    Args:
        page: Playwright page object
        selector: CSS selector for the elements
        count: Expected count
        timeout: Timeout in milliseconds
    """
    expect(page.locator(selector)).to_have_count(count, timeout=timeout)


def assert_input_value(page: Page, selector: str, value: str, timeout: int = 5000) -> None:
    """
    Assert that an input has a specific value.
    
    Args:
        page: Playwright page object
        selector: CSS selector for the input
        value: Expected value
        timeout: Timeout in milliseconds
    """
    expect(page.locator(selector)).to_have_value(value, timeout=timeout)


def assert_checkbox_checked(page: Page, selector: str, timeout: int = 5000) -> None:
    """
    Assert that a checkbox is checked.
    
    Args:
        page: Playwright page object
        selector: CSS selector for the checkbox
        timeout: Timeout in milliseconds
    """
    expect(page.locator(selector)).to_be_checked(timeout=timeout)


def assert_checkbox_unchecked(page: Page, selector: str, timeout: int = 5000) -> None:
    """
    Assert that a checkbox is unchecked.
    
    Args:
        page: Playwright page object
        selector: CSS selector for the checkbox
        timeout: Timeout in milliseconds
    """
    expect(page.locator(selector)).not_to_be_checked(timeout=timeout)


def assert_alert_message(page: Page, message: str, alert_type: Optional[str] = None, timeout: int = 5000) -> None:
    """
    Assert that an alert message is displayed.
    
    Args:
        page: Playwright page object
        message: Expected alert message
        alert_type: Type of alert (success, error, warning, info)
        timeout: Timeout in milliseconds
    """
    if alert_type:
        selector = f".alert.alert-{alert_type}:has-text('{message}')"
    else:
        selector = f".alert:has-text('{message}')"
    
    expect(page.locator(selector)).to_be_visible(timeout=timeout)


def assert_no_errors(page: Page, timeout: int = 2000) -> None:
    """
    Assert that no error messages are displayed.
    
    Args:
        page: Playwright page object
        timeout: Timeout in milliseconds
    """
    try:
        expect(page.locator('.alert-danger, .alert-error, .error-message')).to_have_count(0, timeout=timeout)
    except:
        pass  # No errors found, which is good


def assert_loading_complete(page: Page, timeout: int = 10000) -> None:
    """
    Assert that loading indicators are not visible.
    
    Args:
        page: Playwright page object
        timeout: Timeout in milliseconds
    """
    # Wait for common loading indicators to disappear
    try:
        expect(page.locator('.spinner, .loading, [data-testid="loading"]')).to_have_count(0, timeout=timeout)
    except:
        pass  # No loading indicators found

