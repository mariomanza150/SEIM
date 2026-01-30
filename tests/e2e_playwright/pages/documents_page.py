"""
Documents Page Object for document management.
"""

from pathlib import Path
from typing import List
from .base_page import BasePage


class DocumentsPage(BasePage):
    """Page object for documents page."""
    
    # Page elements
    DOCUMENTS_CONTAINER = '[data-testid="documents-list"], .documents-container'
    DOCUMENT_CARD = '.document-card, [data-testid^="document-"]'
    DOCUMENT_NAME = '.document-name'
    DOCUMENT_STATUS = '.document-status, .badge-status'
    
    # Upload
    UPLOAD_BUTTON = '[data-testid="upload-document"], button:has-text("Upload")'
    UPLOAD_MODAL = '[data-testid="upload-modal"], #uploadDocumentModal'
    FILE_INPUT = '[data-testid="file-input"], input[type="file"]'
    DOCUMENT_TYPE_SELECT = '[data-testid="document-type"], select[name="document_type"]'
    UPLOAD_SUBMIT_BUTTON = '[data-testid="upload-submit"], button:has-text("Upload")'
    
    # Actions
    DOWNLOAD_BUTTON = '[data-testid="download"], .btn-download'
    DELETE_BUTTON = '[data-testid="delete"], .btn-delete'
    VIEW_BUTTON = '[data-testid="view"], .btn-view'
    
    # Messages
    SUCCESS_MESSAGE = '.alert-success'
    ERROR_MESSAGE = '.alert-danger'
    
    def navigate_to_documents(self) -> None:
        """Navigate to documents page."""
        self.navigate('documents/')
    
    def assert_documents_page_loaded(self) -> None:
        """Assert that documents page is loaded."""
        self.assert_url_contains('documents')
        self.assert_element_visible(self.DOCUMENTS_CONTAINER)
    
    def click_upload_button(self) -> None:
        """Click upload document button."""
        self.click(self.UPLOAD_BUTTON)
        self.wait_for_selector(self.UPLOAD_MODAL)
    
    def upload_document(self, file_path: str, document_type: str = None) -> None:
        """
        Upload a document.
        
        Args:
            file_path: Path to the file to upload
            document_type: Optional document type
        """
        # Set file
        self.page.locator(self.FILE_INPUT).set_input_files(file_path)
        
        # Select document type if provided
        if document_type:
            self.select_option(self.DOCUMENT_TYPE_SELECT, document_type)
        
        # Click upload
        self.click(self.UPLOAD_SUBMIT_BUTTON)
        self.wait_for_no_loading_indicators()
    
    def get_document_count(self) -> int:
        """
        Get count of visible documents.
        
        Returns:
            Number of documents
        """
        return self.page.locator(self.DOCUMENT_CARD).count()
    
    def get_document_names(self) -> List[str]:
        """
        Get all document names.
        
        Returns:
            List of document names
        """
        names = []
        count = self.page.locator(self.DOCUMENT_CARD).count()
        for i in range(count):
            name = self.page.locator(self.DOCUMENT_CARD).nth(i).locator(self.DOCUMENT_NAME).text_content()
            if name:
                names.append(name.strip())
        return names
    
    def get_document_status(self, document_name: str) -> str:
        """
        Get status of a document.
        
        Args:
            document_name: Name of the document
        
        Returns:
            Document status
        """
        card = self.page.locator(f'.document-card:has-text("{document_name}")')
        status = card.locator(self.DOCUMENT_STATUS).text_content()
        return status.strip() if status else ''
    
    def download_document(self, document_name: str) -> None:
        """
        Download a document.
        
        Args:
            document_name: Name of the document
        """
        card = self.page.locator(f'.document-card:has-text("{document_name}")')
        with self.page.expect_download() as download_info:
            card.locator(self.DOWNLOAD_BUTTON).click()
        download = download_info.value
        return download
    
    def delete_document(self, document_name: str) -> None:
        """
        Delete a document.
        
        Args:
            document_name: Name of the document
        """
        card = self.page.locator(f'.document-card:has-text("{document_name}")')
        card.locator(self.DELETE_BUTTON).click()
        self.wait_for_no_loading_indicators()
    
    def has_document(self, document_name: str) -> bool:
        """
        Check if a document exists.
        
        Args:
            document_name: Name of the document
        
        Returns:
            True if document exists
        """
        return self.is_visible(f'.document-card:has-text("{document_name}")', timeout=2000)

