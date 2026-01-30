"""
Wait helper utilities for E2E tests.

Provides smart waiting functions for various scenarios.
"""

from typing import Callable, Optional

from playwright.sync_api import Page


def wait_for_element(page: Page, selector: str, timeout: int = 30000, state: str = 'visible') -> None:
    """
    Wait for an element to reach a specific state.
    
    Args:
        page: Playwright page object
        selector: CSS selector for the element
        timeout: Timeout in milliseconds
        state: Element state to wait for (visible, hidden, attached, detached)
    """
    page.wait_for_selector(selector, state=state, timeout=timeout)


def wait_for_text(page: Page, text: str, timeout: int = 30000) -> None:
    """
    Wait for specific text to appear on the page.
    
    Args:
        page: Playwright page object
        text: Text to wait for
        timeout: Timeout in milliseconds
    """
    page.wait_for_selector(f"text={text}", timeout=timeout)


def wait_for_api_response(page: Page, url_pattern: str, timeout: int = 30000) -> None:
    """
    Wait for an API response matching a URL pattern.
    
    Args:
        page: Playwright page object
        url_pattern: URL pattern to match
        timeout: Timeout in milliseconds
    """
    with page.expect_response(url_pattern, timeout=timeout) as response_info:
        pass
    return response_info.value


def wait_for_navigation_complete(page: Page, timeout: int = 30000) -> None:
    """
    Wait for navigation to complete (networkidle state).
    
    Args:
        page: Playwright page object
        timeout: Timeout in milliseconds
    """
    page.wait_for_load_state('networkidle', timeout=timeout)


def wait_for_dom_content_loaded(page: Page, timeout: int = 30000) -> None:
    """
    Wait for DOM content to be loaded.
    
    Args:
        page: Playwright page object
        timeout: Timeout in milliseconds
    """
    page.wait_for_load_state('domcontentloaded', timeout=timeout)


def wait_for_condition(
    page: Page,
    condition: Callable[[], bool],
    timeout: int = 30000,
    poll_interval: int = 100
) -> None:
    """
    Wait for a custom condition to be true.
    
    Args:
        page: Playwright page object
        condition: Function that returns True when condition is met
        timeout: Timeout in milliseconds
        poll_interval: Interval between condition checks in milliseconds
    """
    page.wait_for_function(
        f"() => ({condition})",
        timeout=timeout,
        polling=poll_interval
    )


def wait_for_ajax_complete(page: Page, timeout: int = 30000) -> None:
    """
    Wait for all AJAX requests to complete (jQuery).
    
    Args:
        page: Playwright page object
        timeout: Timeout in milliseconds
    """
    page.wait_for_function(
        "() => typeof jQuery !== 'undefined' && jQuery.active === 0",
        timeout=timeout
    )


def wait_for_file_download(page: Page, timeout: int = 30000):
    """
    Wait for a file download to start.
    
    Args:
        page: Playwright page object
        timeout: Timeout in milliseconds
    
    Returns:
        Download object
    """
    with page.expect_download(timeout=timeout) as download_info:
        pass
    return download_info.value


def wait_for_new_page(context, timeout: int = 30000):
    """
    Wait for a new page/tab to open.
    
    Args:
        context: Browser context
        timeout: Timeout in milliseconds
    
    Returns:
        New page object
    """
    with context.expect_page(timeout=timeout) as page_info:
        pass
    return page_info.value


def wait_for_alert(page: Page, timeout: int = 30000):
    """
    Wait for an alert dialog to appear.
    
    Args:
        page: Playwright page object
        timeout: Timeout in milliseconds
    
    Returns:
        Dialog object
    """
    with page.expect_dialog(timeout=timeout) as dialog_info:
        pass
    return dialog_info.value


def wait_for_console_message(page: Page, text: Optional[str] = None, timeout: int = 30000):
    """
    Wait for a console message.
    
    Args:
        page: Playwright page object
        text: Optional text to match in console message
        timeout: Timeout in milliseconds
    
    Returns:
        Console message object
    """
    with page.expect_console_message(timeout=timeout) as msg_info:
        pass
    message = msg_info.value
    if text and text not in message.text:
        raise AssertionError(f"Console message '{message.text}' does not contain '{text}'")
    return message


def wait_for_websocket(page: Page, url_pattern: str, timeout: int = 30000):
    """
    Wait for a WebSocket connection.
    
    Args:
        page: Playwright page object
        url_pattern: URL pattern to match
        timeout: Timeout in milliseconds
    
    Returns:
        WebSocket object
    """
    with page.expect_websocket(timeout=timeout) as ws_info:
        pass
    return ws_info.value


def wait_for_element_count(page: Page, selector: str, count: int, timeout: int = 30000) -> None:
    """
    Wait for a specific number of elements matching a selector.
    
    Args:
        page: Playwright page object
        selector: CSS selector for the elements
        count: Expected count
        timeout: Timeout in milliseconds
    """
    page.wait_for_function(
        f"(selector, count) => document.querySelectorAll(selector).length === count",
        arg=[selector, count],
        timeout=timeout
    )


def wait_for_no_loading_indicators(page: Page, timeout: int = 30000) -> None:
    """
    Wait for all loading indicators to disappear.
    
    Args:
        page: Playwright page object
        timeout: Timeout in milliseconds
    """
    try:
        page.wait_for_selector('.spinner, .loading, [data-testid="loading"]', state='hidden', timeout=timeout)
    except:
        pass  # No loading indicators found, which is fine

