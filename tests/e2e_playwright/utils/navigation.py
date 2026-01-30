"""
Navigation helper utilities for E2E tests.

Provides functions for navigating to different pages and waiting for page loads.
"""

from playwright.sync_api import Page


def navigate_to_dashboard(page: Page, base_url: str) -> None:
    """Navigate to the dashboard page."""
    page.goto(f"{base_url}/dashboard/")
    page.wait_for_load_state('networkidle')


def navigate_to_programs(page: Page, base_url: str) -> None:
    """Navigate to the programs listing page."""
    page.goto(f"{base_url}/programs/")
    page.wait_for_load_state('networkidle')


def navigate_to_applications(page: Page, base_url: str) -> None:
    """Navigate to the applications listing page."""
    page.goto(f"{base_url}/applications/")
    page.wait_for_load_state('networkidle')


def navigate_to_application_create(page: Page, base_url: str) -> None:
    """Navigate to the application creation page."""
    page.goto(f"{base_url}/applications/create/")
    page.wait_for_load_state('networkidle')


def navigate_to_documents(page: Page, base_url: str) -> None:
    """Navigate to the documents page."""
    page.goto(f"{base_url}/documents/")
    page.wait_for_load_state('networkidle')


def navigate_to_profile(page: Page, base_url: str) -> None:
    """Navigate to the user profile page."""
    page.goto(f"{base_url}/profile/")
    page.wait_for_load_state('networkidle')


def navigate_to_settings(page: Page, base_url: str) -> None:
    """Navigate to the settings page."""
    page.goto(f"{base_url}/settings/")
    page.wait_for_load_state('networkidle')


def navigate_to_admin_dashboard(page: Page, base_url: str) -> None:
    """Navigate to the admin dashboard."""
    page.goto(f"{base_url}/admin-dashboard/")
    page.wait_for_load_state('networkidle')


def navigate_to_coordinator_dashboard(page: Page, base_url: str) -> None:
    """Navigate to the coordinator dashboard."""
    page.goto(f"{base_url}/coordinator-dashboard/")
    page.wait_for_load_state('networkidle')


def navigate_to_user_management(page: Page, base_url: str) -> None:
    """Navigate to the user management page."""
    page.goto(f"{base_url}/user-management/")
    page.wait_for_load_state('networkidle')


def navigate_to_analytics(page: Page, base_url: str) -> None:
    """Navigate to the analytics page."""
    page.goto(f"{base_url}/analytics/")
    page.wait_for_load_state('networkidle')


def wait_for_navigation(page: Page, timeout: int = 30000) -> None:
    """
    Wait for navigation to complete.
    
    Args:
        page: Playwright page object
        timeout: Timeout in milliseconds
    """
    page.wait_for_load_state('networkidle', timeout=timeout)


def wait_for_url(page: Page, pattern: str, timeout: int = 30000) -> None:
    """
    Wait for URL to match a pattern.
    
    Args:
        page: Playwright page object
        pattern: URL pattern to match
        timeout: Timeout in milliseconds
    """
    page.wait_for_url(pattern, timeout=timeout)


def scroll_to_bottom(page: Page) -> None:
    """Scroll to the bottom of the page."""
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")


def scroll_to_top(page: Page) -> None:
    """Scroll to the top of the page."""
    page.evaluate("window.scrollTo(0, 0)")


def scroll_to_element(page: Page, selector: str) -> None:
    """
    Scroll to a specific element.
    
    Args:
        page: Playwright page object
        selector: CSS selector for the element
    """
    element = page.locator(selector)
    element.scroll_into_view_if_needed()

