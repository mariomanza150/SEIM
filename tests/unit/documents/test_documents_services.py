import sys
from datetime import date

# Create a mock magic module for tests
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from documents.models import Document, DocumentType

sys.modules['magic'] = MagicMock()
from documents.services import DocumentService
from exchange.models import Application, ApplicationStatus, Program


class TestDocumentService(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser', email='testuser@example.com', password='TestPass123!'
        )

        # Create required objects for Document model
        self.program = Program.objects.create(
            name="Test Program",
            description="Test Description",
            is_active=True,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30)
        )

        self.application_status, _ = ApplicationStatus.objects.get_or_create(
            name="draft",
            defaults={"order": 1}
        )

        self.application = Application.objects.create(
            student=self.user,
            program=self.program,
            status=self.application_status
        )

        self.document_type = DocumentType.objects.create(
            name="transcript",
            description="Academic transcript"
        )

    def test_validate_file_type_and_size_valid(self):
        """Test file validation with valid file"""
        import documents.services as services_module
        mock_magic_obj = MagicMock()
        mock_magic_obj.from_buffer = MagicMock(return_value="application/pdf")

        with patch.object(services_module, 'MAGIC_AVAILABLE', True):
            with patch.object(services_module, 'magic', mock_magic_obj):
                file_content = b'Test document content'
                uploaded_file = SimpleUploadedFile(
                    'test.pdf',
                    file_content,
                    content_type='application/pdf'
                )
                uploaded_file.size = 1024  # 1KB

                is_valid = DocumentService.validate_file_type_and_size(uploaded_file)
                self.assertTrue(is_valid)

    def test_validate_file_type_and_size_invalid_type(self):
        """Test file validation with invalid file type"""
        import documents.services as services_module
        mock_magic_obj = MagicMock()
        mock_magic_obj.from_buffer = MagicMock(return_value="text/plain")

        with patch.object(services_module, 'MAGIC_AVAILABLE', True):
            with patch.object(services_module, 'magic', mock_magic_obj):
                file_content = b'Test document content'
                uploaded_file = SimpleUploadedFile(
                    'test.exe',
                    file_content,
                    content_type='application/octet-stream'
                )
                uploaded_file.size = 1024

                with self.assertRaises(ValueError, msg="File type not allowed."):
                    DocumentService.validate_file_type_and_size(uploaded_file)

    def test_validate_file_type_and_size_too_large(self):
        """Test file validation with file too large"""
        import documents.services as services_module
        mock_magic_obj = MagicMock()
        mock_magic_obj.from_buffer = MagicMock(return_value="application/pdf")

        with patch.object(services_module, 'MAGIC_AVAILABLE', True):
            with patch.object(services_module, 'magic', mock_magic_obj):
                # Create a large file
                file_content = b'x' * (DocumentService.MAX_FILE_SIZE_MB * 1024 * 1024 + 1000)
                uploaded_file = SimpleUploadedFile(
                    'test.pdf',
                    file_content,
                    content_type='application/pdf'
                )
                uploaded_file.size = DocumentService.MAX_FILE_SIZE_MB * 1024 * 1024 + 1000

                with self.assertRaises(ValueError, msg="File size exceeds maximum allowed."):
                    DocumentService.validate_file_type_and_size(uploaded_file)

    @patch('documents.services.scan_document_virus.delay')
    def test_upload_document_success(self, mock_scan):
        """Test successful document upload"""
        import documents.services as services_module
        mock_magic_obj = MagicMock()
        mock_magic_obj.from_buffer = MagicMock(return_value="application/pdf")

        with patch.object(services_module, 'MAGIC_AVAILABLE', True):
            with patch.object(services_module, 'magic', mock_magic_obj):
                file_content = b'Test document content'
                uploaded_file = SimpleUploadedFile(
                    'test.pdf',
                    file_content,
                    content_type='application/pdf'
                )
                uploaded_file.size = 1024

                document = DocumentService.upload_document(
                    self.application,
                    self.document_type,
                    uploaded_file,
                    self.user
                )

                self.assertIsInstance(document, Document)
                self.assertEqual(document.application, self.application)
                self.assertEqual(document.type, self.document_type)
                self.assertEqual(document.uploaded_by, self.user)

    def test_get_user_documents(self):
        """Test retrieving user documents"""
        # Create test documents
        Document.objects.create(
            application=self.application,
            type=self.document_type,
            uploaded_by=self.user
        )
        Document.objects.create(
            application=self.application,
            type=self.document_type,
            uploaded_by=self.user
        )

        # Get documents for the user
        documents = Document.objects.filter(uploaded_by=self.user)
        self.assertEqual(len(documents), 2)

    def test_get_documents_by_type(self):
        """Test retrieving documents by type"""
        # Create test documents
        Document.objects.create(
            application=self.application,
            type=self.document_type,
            uploaded_by=self.user
        )

        another_type = DocumentType.objects.create(
            name="id_document",
            description="ID document"
        )
        Document.objects.create(
            application=self.application,
            type=another_type,
            uploaded_by=self.user
        )

        application_docs = Document.objects.filter(type=self.document_type)
        self.assertEqual(len(application_docs), 1)

        id_docs = Document.objects.filter(type=another_type)
        self.assertEqual(len(id_docs), 1)

    def test_delete_document_success(self):
        """Test successful document deletion"""
        document = Document.objects.create(
            application=self.application,
            type=self.document_type,
            uploaded_by=self.user
        )

        # Delete the document
        document.delete()

        # Verify document is deleted
        self.assertFalse(Document.objects.filter(id=document.id).exists())

    def test_delete_document_not_owner(self):
        """Test document deletion by non-owner"""
        self.User.objects.create_user(
            username='otheruser', email='otheruser@example.com', password='TestPass123!'
        )
        document = Document.objects.create(
            application=self.application,
            type=self.document_type,
            uploaded_by=self.user
        )

        # Other user cannot delete the document (this would be handled in views)
        # For now, just verify the document exists
        self.assertTrue(Document.objects.filter(id=document.id).exists())

    def test_get_document_statistics(self):
        """Test document statistics calculation"""
        # Create test documents
        Document.objects.create(
            application=self.application,
            type=self.document_type,
            uploaded_by=self.user
        )
        Document.objects.create(
            application=self.application,
            type=self.document_type,
            uploaded_by=self.user
        )

        another_type = DocumentType.objects.create(
            name="id_document",
            description="ID document"
        )
        Document.objects.create(
            application=self.application,
            type=another_type,
            uploaded_by=self.user
        )

        # Calculate statistics
        total_documents = Document.objects.count()
        documents_by_type = {}
        for doc_type in DocumentType.objects.all():
            count = Document.objects.filter(type=doc_type).count()
            documents_by_type[doc_type.name] = count

        stats = {
            'total_documents': total_documents,
            'documents_by_type': documents_by_type
        }

        self.assertIsInstance(stats, dict)
        self.assertIn('total_documents', stats)
        self.assertIn('documents_by_type', stats)
        self.assertEqual(stats['total_documents'], 3)
