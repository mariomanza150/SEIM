"""
Tests for PDF Viewer functionality.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from ..models import Document, Exchange


class TestPDFViewer(TestCase):
    """Test suite for PDF viewer functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()

        # Create test user
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Create test exchange
        self.exchange = Exchange.objects.create(
            student=self.user,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            student_id="STU001",
            current_university="Test University",
            current_program="Computer Science",
            current_year=3,
            gpa=Decimal("3.5"),
            destination_university="MIT",
            destination_country="USA",
            exchange_program="Exchange Program A",
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=180),
            status="SUBMITTED",
        )

        # Create test PDF document
        self.pdf_document = Document.objects.create(
            exchange=self.exchange,
            name="Test Document",
            category="transcript",
            file=SimpleUploadedFile(
                "test_document.pdf",
                b"%PDF-1.4 test content",
                content_type="application/pdf",
            ),
            uploaded_by=self.user,
        )

        # Create test image document
        self.image_document = Document.objects.create(
            exchange=self.exchange,
            name="Test Image",
            category="passport",
            file=SimpleUploadedFile(
                "test_image.jpg", b"fake image data", content_type="image/jpeg"
            ),
            uploaded_by=self.user,
        )

    def test_document_detail_view_pdf(self):
        """Test document detail view with PDF file."""
        self.client.login(username="testuser", password="testpass123")

        url = reverse(
            "exchange:document-detail",
            kwargs={"exchange_pk": self.exchange.pk, "pk": self.pdf_document.pk},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "pdf-viewer-container")
        self.assertContains(response, "data-pdf-url")
        self.assertContains(response, self.pdf_document.name)
        self.assertContains(response, "PDF.js")

    def test_document_detail_view_image(self):
        """Test document detail view with image file."""
        self.client.login(username="testuser", password="testpass123")

        url = reverse(
            "exchange:document-detail",
            kwargs={"exchange_pk": self.exchange.pk, "pk": self.image_document.pk},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "non-pdf-preview")
        self.assertContains(response, "<img")
        self.assertContains(response, self.image_document.file.url)
        self.assertNotContains(response, "pdf-viewer-container")

    def test_document_detail_view_access_control(self):
        """Test access control for document detail view."""
        # Create another user
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="otherpass123"
        )

        # Try to access document without login
        url = reverse(
            "exchange:document-detail",
            kwargs={"exchange_pk": self.exchange.pk, "pk": self.pdf_document.pk},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Login as other user and try to access
        self.client.login(username="otheruser", password="otherpass123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_pdf_viewer_javascript_initialization(self):
        """Test that PDF viewer JavaScript is properly included."""
        self.client.login(username="testuser", password="testpass123")

        url = reverse(
            "exchange:document-detail",
            kwargs={"exchange_pk": self.exchange.pk, "pk": self.pdf_document.pk},
        )
        response = self.client.get(url)

        # Check for PDF.js and custom viewer script inclusion
        self.assertContains(response, "pdf.min.js")
        self.assertContains(response, "pdf.worker.min.js")
        self.assertContains(response, "pdf_viewer.js")

        # Check for PDF viewer initialization
        self.assertContains(response, "PDFViewer")
        self.assertContains(
            response, 'data-pdf-url="' + self.pdf_document.file.url + '"'
        )

    def test_document_info_display(self):
        """Test that document information is correctly displayed."""
        self.client.login(username="testuser", password="testpass123")

        url = reverse(
            "exchange:document-detail",
            kwargs={"exchange_pk": self.exchange.pk, "pk": self.pdf_document.pk},
        )
        response = self.client.get(url)

        # Check document information display
        self.assertContains(response, "Transcript")  # Category display
        self.assertContains(response, self.pdf_document.uploaded_at.strftime("%B"))
        self.assertContains(response, '<i class="fas fa-download"></i> Download')

    def test_download_button(self):
        """Test download button functionality."""
        self.client.login(username="testuser", password="testpass123")

        url = reverse(
            "exchange:document-detail",
            kwargs={"exchange_pk": self.exchange.pk, "pk": self.pdf_document.pk},
        )
        response = self.client.get(url)

        # Check for download button
        self.assertContains(response, f'href="{self.pdf_document.file.url}"')
        self.assertContains(response, "download")

    def test_non_pdf_file_preview(self):
        """Test preview for non-PDF, non-image files."""
        # Create a document with unsupported file type
        doc = Document.objects.create(
            exchange=self.exchange,
            name="Test Document",
            category="other",
            file=SimpleUploadedFile(
                "test_document.docx",
                b"fake docx data",
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
            uploaded_by=self.user,
        )

        self.client.login(username="testuser", password="testpass123")

        url = reverse(
            "exchange:document-detail",
            kwargs={"exchange_pk": self.exchange.pk, "pk": doc.pk},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Preview is not available for this file type")
        self.assertContains(response, "Please download the file to view it")
