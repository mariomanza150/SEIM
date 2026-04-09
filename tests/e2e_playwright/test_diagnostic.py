"""
Diagnostic tests to inspect page structure.

These tests help understand the actual page structure for writing proper E2E tests.
"""

import pytest
from playwright.sync_api import Page


@pytest.mark.e2e_playwright
@pytest.mark.nondestructive
def test_inspect_login_page(page: Page, base_url: str):
    """Inspect the login page structure."""
    page.goto(f"{base_url}/login", wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle", timeout=15000)
    if page.title() and "not found" in page.title().lower():
        pytest.skip("Vue app not available at base_url. Run with BASE_URL=http://localhost:5173")
    
    # Take screenshot
    page.screenshot(path="tests/e2e_playwright/screenshots/login_page_inspect.png", full_page=True)
    
    # Get page HTML structure
    html = page.content()
    
    # Find all input fields
    inputs = page.locator("input").all()
    print(f"\n📋 Found {len(inputs)} input fields:")
    for i, inp in enumerate(inputs):
        input_type = inp.get_attribute("type") or "text"
        input_name = inp.get_attribute("name") or "no-name"
        input_id = inp.get_attribute("id") or "no-id"
        input_class = inp.get_attribute("class") or "no-class"
        print(f"  {i+1}. type={input_type}, name={input_name}, id={input_id}, class={input_class[:50]}")
    
    # Find all buttons
    buttons = page.locator("button, input[type='submit']").all()
    print(f"\n🔘 Found {len(buttons)} buttons:")
    for i, btn in enumerate(buttons):
        btn_type = btn.get_attribute("type") or "button"
        btn_text = btn.inner_text()[:50] if btn.inner_text() else "no-text"
        btn_id = btn.get_attribute("id") or "no-id"
        print(f"  {i+1}. type={btn_type}, text={btn_text}, id={btn_id}")
    
    # Get page title
    title = page.title()
    print(f"\n📄 Page title: {title}")
    
    # Get current URL
    print(f"🔗 Current URL: {page.url}")
    
    # Check for forms
    forms = page.locator("form").all()
    print(f"\n📝 Found {len(forms)} forms:")
    for i, form in enumerate(forms):
        form_action = form.get_attribute("action") or "no-action"
        form_method = form.get_attribute("method") or "GET"
        print(f"  {i+1}. action={form_action}, method={form_method}")
    
    print("\n✅ Diagnostic complete. Check screenshot: tests/e2e_playwright/screenshots/login_page_inspect.png")
    
    # Don't fail - this is just for inspection
    assert True


@pytest.mark.e2e_playwright
@pytest.mark.nondestructive
def test_inspect_homepage(page: Page, base_url: str):
    """Inspect the homepage structure."""
    page.goto(base_url)
    page.wait_for_load_state("networkidle")
    
    # Take screenshot
    page.screenshot(path="tests/e2e_playwright/screenshots/homepage_inspect.png", full_page=True)
    
    # Get page title
    title = page.title()
    print(f"\n📄 Homepage title: {title}")
    
    # Get current URL
    print(f"🔗 Current URL: {page.url}")
    
    # Find navigation links
    nav_links = page.locator("nav a, header a, .navbar a").all()
    print(f"\n🔗 Found {len(nav_links)} navigation links:")
    for i, link in enumerate(nav_links[:10]):  # Limit to first 10
        link_text = link.inner_text()[:30] if link.inner_text() else "no-text"
        link_href = link.get_attribute("href") or "no-href"
        print(f"  {i+1}. {link_text} -> {link_href}")
    
    print("\n✅ Homepage diagnostic complete.")
    assert True

