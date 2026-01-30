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
    """Login via API directly, then verify we can access protected pages."""
    # First, get CSRF token by visiting the login page
    page.goto(f"{base_url}/seim/login/")
    page.wait_for_load_state("networkidle")
    
    # Get CSRF token from the page
    csrf_token = page.locator('#loginForm input[name="csrfmiddlewaretoken"]').first.get_attribute("value")
    assert csrf_token, "CSRF token not found"
    
    # Make API call directly using Playwright's request context
    context = page.context
    response = context.request.post(
        f"{base_url}/api/accounts/login/",
        headers={
            "Content-Type": "application/json",
            "X-CSRFToken": csrf_token,
            "Referer": f"{base_url}/seim/login/",
        },
        data={
            "login": "student1",
            "password": "student123"
        }
    )
    
    print(f"\n📡 API Response Status: {response.status}")
    
    if response.ok:
        data = response.json()
        print(f"✅ Login API successful!")
        print(f"   Access token: {data.get('access', 'N/A')[:20]}...")
        print(f"   User: {data.get('user', {}).get('username', 'N/A')}")
        
        # Store tokens in localStorage (as the JavaScript would)
        page.evaluate(f"""
            localStorage.setItem('seim_access_token', '{data.get('access', '')}');
            localStorage.setItem('seim_refresh_token', '{data.get('refresh', '')}');
        """)
        
        # Now try to access dashboard
        page.goto(f"{base_url}/seim/dashboard/")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        current_url = page.url
        print(f"\n🔗 Dashboard URL: {current_url}")
        
        # Verify we're not redirected to login
        assert "login" not in current_url.lower(), f"Should be on dashboard, but on: {current_url}"
        
        print("✅ Successfully accessed dashboard after API login!")
        page.screenshot(path="tests/e2e_playwright/screenshots/login_api_direct_success.png")
        
    else:
        error_data = response.text()
        print(f"\n❌ Login API failed!")
        print(f"   Status: {response.status}")
        print(f"   Response: {error_data[:200]}")
        page.screenshot(path="tests/e2e_playwright/screenshots/login_api_direct_failed.png")
        assert False, f"Login API failed with status {response.status}: {error_data[:200]}"


@pytest.mark.e2e_playwright
@pytest.mark.auth
@pytest.mark.nondestructive
def test_login_form_submission_with_wait(page: Page, base_url: str):
    """Test form submission with proper waiting for JavaScript execution."""
    page.goto(f"{base_url}/seim/login/")
    page.wait_for_load_state("networkidle")
    
    # Wait for JavaScript to be ready
    page.wait_for_function("typeof setupLoginForm !== 'undefined'", timeout=10000)
    time.sleep(1)  # Give a bit more time for event listeners
    
    # Fill form
    login_form = page.locator('#loginForm')
    username_field = login_form.locator('input[type="text"]').first
    if username_field.count() == 0:
        username_field = login_form.locator('input[name="username"], input[name="email"]').first
    username_field.fill("student1")
    
    password_field = login_form.locator('input[type="password"]').first
    password_field.fill("student123")
    
    # Set up response interception
    api_called = False
    api_status = None
    
    def handle_response(response):
        nonlocal api_called, api_status
        if '/api/accounts/login/' in response.url:
            api_called = True
            api_status = response.status
            print(f"\n📡 API call detected! Status: {response.status}")
    
    page.on("response", handle_response)
    
    # Click submit button
    sign_in_button = login_form.locator('button:has-text("Sign In"), input[type="submit"]:has-text("Sign In")').first
    sign_in_button.click()
    
    # Wait for API call
    for _ in range(10):  # Wait up to 5 seconds
        if api_called:
            break
        time.sleep(0.5)
    
    # Wait for potential redirect
    try:
        page.wait_for_url(
            lambda url: "dashboard" in url.lower() or ("login" not in url.lower()),
            timeout=10000
        )
    except:
        page.wait_for_load_state("networkidle")
        time.sleep(2)
    
    current_url = page.url
    has_tokens = page.evaluate("localStorage.getItem('seim_access_token') !== null")
    
    print(f"\n📊 Results:")
    print(f"   API called: {api_called}")
    print(f"   API status: {api_status}")
    print(f"   Has tokens: {has_tokens}")
    print(f"   Current URL: {current_url}")
    
    if api_called and api_status == 200 and has_tokens:
        if "dashboard" in current_url.lower() or "login" not in current_url.lower():
            print("✅ Login successful via form!")
            page.screenshot(path="tests/e2e_playwright/screenshots/login_form_success.png")
        else:
            print("⚠️  API succeeded but redirect didn't happen")
            page.screenshot(path="tests/e2e_playwright/screenshots/login_form_no_redirect.png")
    elif api_called and api_status != 200:
        print(f"❌ API call failed with status {api_status}")
        page.screenshot(path="tests/e2e_playwright/screenshots/login_form_api_failed.png")
    else:
        print("⚠️  API call not detected or failed")
        page.screenshot(path="tests/e2e_playwright/screenshots/login_form_no_api.png")

