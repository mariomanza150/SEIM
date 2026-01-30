"""
Diagnostic test to understand login form submission.
"""

import pytest
from playwright.sync_api import Page
import time


@pytest.mark.e2e_playwright
@pytest.mark.nondestructive
def test_inspect_login_form_submission(page: Page, base_url: str):
    """Inspect what happens when we submit the login form."""
    page.goto(f"{base_url}/seim/login/")
    page.wait_for_load_state("networkidle")
    
    # Take screenshot before
    page.screenshot(path="tests/e2e_playwright/screenshots/login_before_submit.png")
    
    # Find all form elements
    forms = page.locator("form").all()
    print(f"\n📝 Found {len(forms)} forms:")
    for i, form in enumerate(forms):
        form_action = form.get_attribute("action") or "no-action"
        form_method = form.get_attribute("method") or "GET"
        form_id = form.get_attribute("id") or "no-id"
        print(f"  Form {i+1}: action={form_action}, method={form_method}, id={form_id}")
    
    # Find username field
    username_field = page.locator('input[type="text"]').first
    if username_field.count() == 0:
        username_field = page.locator('input[name="username"], input[name="email"]').first
    
    print(f"\n👤 Username field found: {username_field.count() > 0}")
    if username_field.count() > 0:
        username_field.fill("student1")
        print("  ✅ Filled username: student1")
    
    # Find password field
    password_field = page.locator('input[type="password"]').first
    print(f"\n🔒 Password field found: {password_field.count() > 0}")
    if password_field.count() > 0:
        password_field.fill("student123")
        print("  ✅ Filled password")
    
    # Check for CSRF token in login form
    login_form = page.locator('#loginForm')
    if login_form.count() > 0:
        csrf_token = login_form.locator('input[name="csrfmiddlewaretoken"]').first
        if csrf_token.count() > 0:
            token_value = csrf_token.get_attribute("value")
            print(f"\n🔐 CSRF token in login form found: {token_value[:20] if token_value else 'None'}...")
        else:
            print("\n⚠️  No CSRF token in login form")
    else:
        print("\n⚠️  Login form not found")
    
    # Take screenshot after filling
    page.screenshot(path="tests/e2e_playwright/screenshots/login_after_fill.png")
    
    # Find submit button
    sign_in_button = page.locator('button:has-text("Sign In"), input[type="submit"]:has-text("Sign In")').first
    print(f"\n🔘 Sign In button found: {sign_in_button.count() > 0}")
    
    if sign_in_button.count() > 0:
        # Click and wait
        print("\n🖱️  Clicking Sign In button...")
        sign_in_button.click()
        
        # Wait a bit
        time.sleep(3)
        page.wait_for_load_state("networkidle")
        
        # Take screenshot after
        page.screenshot(path="tests/e2e_playwright/screenshots/login_after_submit.png")
        
        # Check current URL
        current_url = page.url
        print(f"\n🔗 Current URL after submit: {current_url}")
        
        # Check for error messages
        error_messages = page.locator('.error, .alert-danger, .alert-error, [role="alert"], .message-error')
        error_count = error_messages.count()
        print(f"\n❌ Error messages found: {error_count}")
        if error_count > 0:
            for i in range(min(error_count, 3)):
                error_text = error_messages.nth(i).inner_text()
                print(f"  Error {i+1}: {error_text[:100]}")
        
        # Check for success messages
        success_messages = page.locator('.success, .alert-success, .message-success')
        success_count = success_messages.count()
        print(f"\n✅ Success messages found: {success_count}")
        
        # Check page content
        page_text = page.locator("body").inner_text()
        if "error" in page_text.lower() or "invalid" in page_text.lower():
            print("\n⚠️  Page contains error-related text")
        if "welcome" in page_text.lower() or "dashboard" in page_text.lower():
            print("\n✅ Page contains welcome/dashboard text")
        
        # Get page title
        title = page.title()
        print(f"\n📄 Page title: {title}")
    
    print("\n✅ Diagnostic complete. Check screenshots in tests/e2e_playwright/screenshots/")

