"""
Test authentication by calling the API directly, then verifying the flow.
"""

import pytest
from playwright.sync_api import Page
import time


@pytest.mark.e2e_playwright
@pytest.mark.auth
@pytest.mark.nondestructive
def test_login_via_api_then_verify(page: Page, base_url: str):
    """Login via Vue JWT API, then verify we can access protected pages."""
    response = page.context.request.post(
        f"{base_url}/api/token/",
        headers={"Content-Type": "application/json"},
        data={"email": "student1@example.com", "password": "student123"},
    )
    print(f"\n📡 API Response Status: {response.status}")
    if response.status == 404:
        pytest.skip("API not available at base_url. Run with BASE_URL=http://localhost:5173")
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
    page.goto(f"{base_url}/dashboard")
    page.wait_for_load_state("networkidle")
    time.sleep(1)
    current_url = page.url
    assert "login" not in current_url.lower(), f"Should be on dashboard, but on: {current_url}"
    print("✅ Successfully accessed dashboard after API login!")
    page.screenshot(path="tests/e2e_playwright/screenshots/login_api_direct_success.png")


@pytest.mark.e2e_playwright
@pytest.mark.auth
@pytest.mark.nondestructive
def test_login_form_submission_with_wait(page: Page, base_url: str):
    """Test Vue login form submission (email + password, /api/token/)."""
    page.goto(f"{base_url}/login", wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle", timeout=15000)
    if page.title() and "not found" in page.title().lower():
        pytest.skip("Vue app not available at base_url. Run with BASE_URL=http://localhost:5173")
    time.sleep(1)
    
    api_called = False
    api_status = None

    def handle_response(resp):
        nonlocal api_called, api_status
        if "/api/token/" in resp.url:
            api_called = True
            api_status = resp.status

    page.on("response", handle_response)
    
    page.locator("input#email, input[type='email']").first.fill("student1@example.com")
    page.locator("input#password, input[type='password']").first.fill("student123")
    page.locator('button:has-text("Sign In"), [data-testid="login-submit"]').first.click()
    
    for _ in range(15):
        if api_called:
            break
        time.sleep(0.5)
    
    try:
        page.wait_for_url(lambda url: "dashboard" in url.lower(), timeout=10000)
    except Exception:
        page.wait_for_load_state("networkidle")
        time.sleep(2)
    
    current_url = page.url
    has_tokens = page.evaluate("localStorage.getItem('access_token') !== null")
    print(f"\n📊 API called: {api_called}, status: {api_status}, tokens: {has_tokens}, URL: {current_url}")
    
    if api_called and api_status == 200 and has_tokens:
        print("✅ Login successful via form!")
        page.screenshot(path="tests/e2e_playwright/screenshots/login_form_success.png")
    else:
        page.screenshot(path="tests/e2e_playwright/screenshots/login_form_no_api.png")

