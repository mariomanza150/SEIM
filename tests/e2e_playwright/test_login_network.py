"""
Test to intercept and inspect login API calls.
"""

import pytest
from playwright.sync_api import Page
import time


@pytest.mark.e2e_playwright
@pytest.mark.nondestructive
def test_login_api_call(page: Page, base_url: str):
    """Test login by intercepting the API call."""
    # Set up request interception
    api_responses = []
    
    def handle_response(response):
        if '/api/accounts/login/' in response.url or '/api/token/' in response.url:
            api_responses.append({
                'url': response.url,
                'status': response.status,
                'headers': response.headers,
            })
            try:
                # Try to get response body
                api_responses[-1]['body'] = response.json()
            except:
                api_responses[-1]['body'] = None
    
    page.on("response", handle_response)
    
    # Navigate to login page
    page.goto(f"{base_url}/seim/login/")
    page.wait_for_load_state("networkidle")
    
    # Fill login form
    login_form = page.locator('#loginForm')
    username_field = login_form.locator('input[type="text"]').first
    if username_field.count() == 0:
        username_field = login_form.locator('input[name="username"], input[name="email"]').first
    username_field.fill("student1")
    
    password_field = login_form.locator('input[type="password"]').first
    password_field.fill("student123")
    
    # Click submit
    sign_in_button = login_form.locator('button:has-text("Sign In"), input[type="submit"]:has-text("Sign In")').first
    sign_in_button.click()
    
    # Wait for API call
    page.wait_for_load_state("networkidle")
    time.sleep(3)
    
    # Check API responses
    print(f"\n📡 API Calls captured: {len(api_responses)}")
    for i, resp in enumerate(api_responses):
        print(f"\n  Call {i+1}:")
        print(f"    URL: {resp['url']}")
        print(f"    Status: {resp['status']}")
        if resp.get('body'):
            print(f"    Response: {resp['body']}")
        else:
            print(f"    Response: (could not parse JSON)")
    
    # Check current URL
    current_url = page.url
    print(f"\n🔗 Current URL: {current_url}")
    
    # Check for errors in console
    console_messages = []
    def handle_console(msg):
        console_messages.append(msg.text)
    
    page.on("console", handle_console)
    
    # Take screenshot
    page.screenshot(path="tests/e2e_playwright/screenshots/login_network_test.png")
    
    # Analyze results
    if api_responses:
        last_response = api_responses[-1]
        if last_response['status'] == 200:
            print("\n✅ API call succeeded (200 OK)")
            if "dashboard" in current_url.lower() or "login" not in current_url.lower():
                print("✅ Login successful - redirected")
            else:
                print("⚠️  API succeeded but no redirect happened")
        elif last_response['status'] == 401:
            print("\n❌ API call failed - Unauthorized (401)")
            print("   Check: Username/password might be incorrect")
        elif last_response['status'] == 400:
            print("\n❌ API call failed - Bad Request (400)")
            print("   Check: Request format might be wrong")
        else:
            print(f"\n⚠️  API call returned status: {last_response['status']}")
    else:
        print("\n⚠️  No API call detected")
        print("   Check: JavaScript might not be executing")
    
    if console_messages:
        print(f"\n📝 Console messages: {len(console_messages)}")
        for msg in console_messages[:5]:
            print(f"   {msg}")
    
    print("\n✅ Network test complete. Check screenshot for details.")

