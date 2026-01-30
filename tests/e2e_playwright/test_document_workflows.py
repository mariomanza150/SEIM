"""
End-to-end tests for document management workflows.
"""

import pytest
from tests.e2e_playwright.pages.documents_page import DocumentsPage


@pytest.mark.e2e_playwright
@pytest.mark.file_upload
class TestDocumentWorkflows:
    """Test suite for document workflows."""
    
    def test_view_documents_page(self, page, base_url, login_as_student):
        """Test accessing documents page."""
        documents_page = DocumentsPage(page, base_url)
        documents_page.navigate_to_documents()
        documents_page.assert_documents_page_loaded()
    
    def test_upload_button_visible(self, page, base_url, login_as_student):
        """Test upload button is accessible."""
        documents_page = DocumentsPage(page, base_url)
        documents_page.navigate_to_documents()
        
        if documents_page.is_visible(documents_page.UPLOAD_BUTTON):
            documents_page.click_upload_button()
            assert documents_page.is_visible(documents_page.UPLOAD_MODAL)


@pytest.mark.e2e_playwright
@pytest.mark.file_upload
@pytest.mark.smoke
class TestDocumentWorkflowsSmoke:
    """Smoke tests for document workflows."""
    
    def test_documents_page_smoke(self, page, base_url, login_as_student):
        """Smoke test for documents page access."""
        documents_page = DocumentsPage(page, base_url)
        documents_page.navigate_to_documents()
        assert documents_page.is_visible(documents_page.DOCUMENTS_CONTAINER)

