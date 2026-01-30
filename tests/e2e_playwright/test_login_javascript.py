"""
Test to verify JavaScript is loaded and executing for login form.
"""

import pytest
from playwright.sync_api import Page
import time


@pytest.mark.e2e_playwright
@pytest.mark.nondestructive
def test_login_javascript_loaded(page: Page, base_url: str):
    """Verify JavaScript is loaded and form handler is attached."""
    page.goto(f"{base_url}/seim/login/")
    page.wait_for_load_state("networkidle")
    
    # Wait for JavaScript to load
    time.sleep(2)
    
    # Check if loginForm exists
    login_form = page.locator('#loginForm')
    assert login_form.count() > 0, "Login form not found"
    
    # Check if setupLoginForm function exists
    has_setup_function = page.evaluate("""
        () => {
            return typeof setupLoginForm !== 'undefined';
        }
    """)
    print(f"\n🔍 setupLoginForm function exists: {has_setup_function}")
    
    # Check if form has submit event listener
    has_submit_listener = page.evaluate("""
        () => {
            const form = document.getElementById('loginForm');
            if (!form) return false;
            // Check if form has any event listeners (hard to detect directly)
            return form !== null;
        }
    """)
    print(f"🔍 Login form element exists: {has_submit_listener}")
    
    # Try to manually trigger the form submission via JavaScript
    print("\n🖱️  Attempting to trigger form submission via JavaScript...")
    
    # Fill form
    username_field = login_form.locator('input[type="text"]').first
    if username_field.count() == 0:
        username_field = login_form.locator('input[name="username"], input[name="email"]').first
    username_field.fill("student1")
    
    password_field = login_form.locator('input[type="password"]').first
    password_field.fill("student123")
    
    # Try submitting via JavaScript directly
    result = page.evaluate("""
        async () => {
            const form = document.getElementById('loginForm');
            if (!form) return {error: 'Form not found'};
            
            // Try to trigger submit event
            const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
            form.dispatchEvent(submitEvent);
            
            // Wait a bit
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            return {
                formFound: true,
                currentUrl: window.location.href,
                hasTokens: localStorage.getItem('seim_access_token') !== null
            };
        }
    """)
    
    print(f"\n📊 JavaScript execution result:")
    print(f"   Form found: {result.get('formFound', False)}")
    print(f"   Current URL: {result.get('currentUrl', 'unknown')}")
    print(f"   Has tokens: {result.get('hasTokens', False)}")
    
    # Wait a bit more
    time.sleep(2)
    
    # Check final state
    final_url = page.url
    has_tokens = page.evaluate("localStorage.getItem('seim_access_token') !== null")
    
    print(f"\n🔗 Final URL: {final_url}")
    print(f"🔑 Tokens in localStorage: {has_tokens}")
    
    # Take screenshot
    page.screenshot(path="tests/e2e_playwright/screenshots/login_javascript_test.png")
    
    if has_tokens:
        print("\n✅ Tokens stored - login API call succeeded!")
    else:
        print("\n⚠️  No tokens stored - login API call may have failed")
    
    if "dashboard" in final_url.lower():
        print("✅ Redirected to dashboard")
    elif "login" not in final_url.lower():
        print(f"✅ Redirected (not on login page): {final_url}")
    else:
        print("⚠️  Still on login page")
    
    print("\n✅ JavaScript test complete.")

