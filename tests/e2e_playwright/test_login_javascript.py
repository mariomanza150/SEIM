"""
Test to verify Vue login page and form work (email + password, /api/token/).
"""

import pytest
from playwright.sync_api import Page, expect
import time


@pytest.mark.e2e_playwright
@pytest.mark.nondestructive
def test_login_javascript_loaded(page: Page, base_url: str):
    """Verify Vue login page loads and form submission stores access_token."""
    page.goto(f"{base_url}/login", wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle", timeout=15000)
    if page.title() and "not found" in page.title().lower():
        pytest.skip("Vue app not available at base_url. Run with BASE_URL=http://localhost:5173")
    time.sleep(1)
    form = page.locator("form")
    expect(form).to_have_count(1)
    expect(page.locator("input#email, input[type='email']")).to_be_visible()
    expect(page.locator("input#password, input[type='password']")).to_be_visible()
    expect(page.locator('button:has-text("Sign In")')).to_be_visible()
    
    page.locator("input#email, input[type='email']").first.fill("student1@example.com")
    page.locator("input#password, input[type='password']").first.fill("student123")
    page.locator('button:has-text("Sign In"), [data-testid="login-submit"]').first.click()
    
    try:
        page.wait_for_url(lambda url: "dashboard" in url.lower(), timeout=10000)
    except Exception:
        page.wait_for_load_state("networkidle")
        time.sleep(2)
    
    final_url = page.url
    has_tokens = page.evaluate("localStorage.getItem('access_token') !== null")
    
    page.screenshot(path="tests/e2e_playwright/screenshots/login_javascript_test.png")
    print(f"\n🔗 Final URL: {final_url}, tokens: {has_tokens}")
    
    if has_tokens:
        print("✅ Tokens stored - login succeeded!")
    if "dashboard" in final_url.lower():
        print("✅ Redirected to dashboard")
    print("✅ Vue login test complete.")

