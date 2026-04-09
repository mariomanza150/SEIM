"""
Authentication helpers for E2E tests.

Uses Vue SPA: /login page, /api/token/ (email + password), access_token/refresh_token in localStorage.
"""

from playwright.sync_api import Page, Browser, BrowserContext
from typing import Optional
import time


class VueAppNotAvailable(Exception):
    """Raised when Vue app or API at base_url is not available (e.g. 404)."""
    pass

# Username -> email for /api/token/ (Vue backend accepts email)
_USER_EMAIL = {
    "student1": "student1@example.com",
    "coordinator": "coordinator@example.com",
    "admin": "admin@example.com",
}


def login_via_api(page: Page, base_url: str, email: str, password: str) -> dict:
    """
    Login via JWT API and store tokens in localStorage (Vue app keys).
    Uses POST /api/token/ with email + password; no CSRF.
    """
    max_retries = 3
    retry_delay = 2
    response = None
    for attempt in range(max_retries):
        response = page.context.request.post(
            f"{base_url}/api/token/",
            headers={"Content-Type": "application/json"},
            data={"email": email, "password": password},
        )
        if response.ok:
            break
        if response.status == 404:
            raise VueAppNotAvailable(
                f"API not available at {base_url}/api/token/ (404). "
                "Start Vue dev server and Django API; run with BASE_URL=http://localhost:5173"
            )
        if response.status == 429 and attempt < max_retries - 1:
            time.sleep(retry_delay)
            retry_delay *= 2
            continue
        assert response.ok, f"Login API failed: {response.status} {response.text()[:200]}"
    data = response.json()
    access = data.get("access", "")
    refresh = data.get("refresh", "")
    page.goto(base_url)
    page.wait_for_load_state("domcontentloaded")
    page.evaluate(
        """
        (args) => {
            localStorage.setItem('access_token', args.access);
            localStorage.setItem('refresh_token', args.refresh || '');
        }
        """,
        {"access": access, "refresh": refresh},
    )
    return data


def login(page: Page, base_url: str, username: str, password: str) -> dict:
    """Login with username (mapped to email) and password. Used by conftest fixtures."""
    email = _USER_EMAIL.get(username, f"{username}@example.com")
    return login_via_api(page, base_url, email, password)


def login_as_student(page: Page, base_url: str) -> dict:
    """Login as student1 user."""
    return login_via_api(page, base_url, "student1@example.com", "student123")


def login_as_coordinator(page: Page, base_url: str) -> dict:
    """Login as coordinator user."""
    return login_via_api(page, base_url, "coordinator@example.com", "coord123")


def login_as_admin(page: Page, base_url: str) -> dict:
    """Login as admin user."""
    return login_via_api(page, base_url, "admin@example.com", "admin123")


def create_authenticated_context(
    browser: Browser, base_url: str, username: str, password: str
) -> BrowserContext:
    """Create a browser context with tokens set so new pages are logged in."""
    context = browser.new_context()
    page = context.new_page()
    login(page, base_url, username, password)
    page.close()
    return context


def logout(page: Page, base_url: str) -> None:
    """Clear tokens and navigate to Vue login page."""
    page.evaluate("""
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    """)
    page.goto(f"{base_url}/login")
    page.wait_for_load_state("networkidle")


def is_logged_in(page: Page) -> bool:
    """True if access_token is present (Vue app)."""
    return page.evaluate("localStorage.getItem('access_token') !== null")


def ensure_logged_in(
    page: Page,
    base_url: str,
    username: str = "student1",
    password: str = "student123",
) -> dict:
    """Ensure user is logged in; login via API if not."""
    if not is_logged_in(page):
        email = _USER_EMAIL.get(username, f"{username}@example.com")
        return login_via_api(page, base_url, email, password)
    try:
        page.goto(f"{base_url}/dashboard")
        page.wait_for_load_state("networkidle", timeout=5000)
        if "login" not in page.url.lower():
            return {"status": "already_logged_in"}
    except Exception:
        pass
    email = _USER_EMAIL.get(username, f"{username}@example.com")
    return login_via_api(page, base_url, email, password)
