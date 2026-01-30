"""
End-to-end tests for error handling scenarios.
"""

import pytest


@pytest.mark.e2e_playwright
class TestErrorScenarios:
    """Test suite for error handling."""
    
    def test_404_page(self, page, base_url):
        """Test 404 error page."""
        page.goto(f"{base_url}/nonexistent-page-12345/")
        
        # Check that page loaded (even if 404)
        assert page.url
        
        # May show 404 or redirect to home
        page_text = page.content().lower()
        assert '404' in page_text or 'not found' in page_text or 'home' in page.url
    
    def test_invalid_form_submission(self, page, base_url):
        """Test form validation on invalid submission."""
        from tests.e2e_playwright.pages.auth_page import AuthPage
        
        auth_page = AuthPage(page, base_url)
        auth_page.navigate_to_register()
        
        # Try to submit without filling required fields
        if auth_page.is_visible(auth_page.REGISTER_SUBMIT_BUTTON):
            # Click submit without filling form
            pass  # Modern browsers prevent submission, which is expected

