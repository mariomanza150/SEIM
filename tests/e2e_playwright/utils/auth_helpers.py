"""
Authentication helpers for E2E tests.

These helpers use API login for reliable and fast authentication.
"""

from playwright.sync_api import Page
from typing import Optional
import time


def login_via_api(page: Page, base_url: str, username: str, password: str) -> dict:
    """
    Login via API and store tokens in localStorage.
    
    Args:
        page: Playwright page object
        base_url: Base URL of the application
        username: Username to login with
        password: Password for the user
        
    Returns:
        dict: Response data with access token, refresh token, and user info
        
    Raises:
        AssertionError: If login fails
    """
    # First, get CSRF token by visiting the login page
    page.goto(f"{base_url}/seim/login/")
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except:
        # If networkidle times out, try domcontentloaded
        try:
            page.wait_for_load_state("domcontentloaded", timeout=10000)
        except:
            pass  # Continue anyway
    
    # Wait for login form to be present
    try:
        page.wait_for_selector('#loginForm, form', timeout=10000)
    except:
        pass  # Continue anyway
    
    # Get CSRF token from the page
    csrf_token = None
    try:
        csrf_token = page.locator('#loginForm input[name="csrfmiddlewaretoken"]').first.get_attribute("value", timeout=10000)
    except:
        pass
    
    if not csrf_token:
        # Try alternative selector
        try:
            csrf_token = page.locator('input[name="csrfmiddlewaretoken"]').first.get_attribute("value", timeout=10000)
        except:
            pass
    
    assert csrf_token, "CSRF token not found on login page"
    
    # Make API call directly using Playwright's request context
    # Add retry logic for rate limiting (429 errors)
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        context = page.context
        response = context.request.post(
            f"{base_url}/api/accounts/login/",
            headers={
                "Content-Type": "application/json",
                "X-CSRFToken": csrf_token,
                "Referer": f"{base_url}/seim/login/",
            },
            data={
                "login": username,
                "password": password
            }
        )
        
        if response.ok:
            break
        elif response.status == 429 and attempt < max_retries - 1:
            # Rate limited - wait and retry
            error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            wait_time = error_data.get("detail", "").lower()
            if "seconds" in wait_time:
                # Extract wait time from error message if available
                try:
                    import re
                    seconds = int(re.search(r'(\d+)', wait_time).group(1))
                    retry_delay = max(seconds, retry_delay)
                except:
                    pass
            
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff
            continue
        else:
            # Other error or final attempt failed
            assert False, f"Login API failed with status {response.status}: {response.text()[:200]}"
    
    data = response.json()
    
    # Store tokens in localStorage (as the JavaScript would)
    page.evaluate(f"""
        localStorage.setItem('seim_access_token', '{data.get('access', '')}');
        localStorage.setItem('seim_refresh_token', '{data.get('refresh', '')}');
    """)
    
    return data


def login_as_student(page: Page, base_url: str) -> dict:
    """Login as student1 user."""
    return login_via_api(page, base_url, "student1", "student123")


def login_as_coordinator(page: Page, base_url: str) -> dict:
    """Login as coordinator user."""
    return login_via_api(page, base_url, "coordinator", "coord123")


def login_as_admin(page: Page, base_url: str) -> dict:
    """Login as admin user."""
    return login_via_api(page, base_url, "admin", "admin123")


def logout(page: Page, base_url: str) -> None:
    """
    Logout by clearing tokens and session.
    
    Args:
        page: Playwright page object
        base_url: Base URL of the application
    """
    # Clear localStorage tokens
    page.evaluate("""
        localStorage.removeItem('seim_access_token');
        localStorage.removeItem('seim_refresh_token');
    """)
    
    # Try to call logout API if we have a token
    try:
        access_token = page.evaluate("localStorage.getItem('seim_access_token')")
        if access_token:
            # Get refresh token
            refresh_token = page.evaluate("localStorage.getItem('seim_refresh_token')")
            
            context = page.context
            response = context.request.post(
                f"{base_url}/api/accounts/logout/",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}",
                },
                data={
                    "refresh": refresh_token
                } if refresh_token else {}
            )
    except:
        pass  # Ignore errors - tokens are cleared anyway
    
    # Navigate to login page to clear session
    page.goto(f"{base_url}/seim/login/")
    page.wait_for_load_state("networkidle")


def is_logged_in(page: Page) -> bool:
    """
    Check if user is logged in by checking for access token.
    
    Args:
        page: Playwright page object
        
    Returns:
        bool: True if logged in, False otherwise
    """
    return page.evaluate("localStorage.getItem('seim_access_token') !== null")


def ensure_logged_in(page: Page, base_url: str, username: str = "student1", password: str = "student123") -> dict:
    """
    Ensure user is logged in. If not, login via API.
    
    Args:
        page: Playwright page object
        base_url: Base URL of the application
        username: Username to login with (default: student1)
        password: Password for the user (default: student123)
        
    Returns:
        dict: Login response data
    """
    if not is_logged_in(page):
        return login_via_api(page, base_url, username, password)
    else:
        # Verify token is still valid by checking if we can access a protected page
        try:
            page.goto(f"{base_url}/seim/dashboard/")
            page.wait_for_load_state("networkidle", timeout=5000)
            if "login" not in page.url.lower():
                # Still logged in
                return {"status": "already_logged_in"}
        except:
            pass
        
        # Token might be invalid, login again
        return login_via_api(page, base_url, username, password)
