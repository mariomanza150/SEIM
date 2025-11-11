from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIRequestFactory

from accounts.models import User
from documents import serializers
from documents.models import (
    Document,
    DocumentType,
)
from exchange.models import Application, ApplicationStatus, Program


@pytest.mark.django_db
class TestDocumentTypeSerializer:
    def test_document_type_serializer_valid(self):
        """Test DocumentTypeSerializer with valid data."""
        data = {
            'name': 'Transcript',
            'description': 'Official academic transcript'
        }
        serializer = serializers.DocumentTypeSerializer(data=data)
        assert serializer.is_valid()

        document_type = serializer.save()
        assert document_type.name == 'Transcript'
        assert document_type.description == 'Official academic transcript'

    def test_document_type_serializer_invalid(self):
        """Test DocumentTypeSerializer with invalid data."""
        data = {
            'name': '',  # Empty name should be invalid
            'description': 'Test description'
        }
        serializer = serializers.DocumentTypeSerializer(data=data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors

@pytest.mark.django_db
class TestDocumentSerializer:
    def test_document_serializer_valid(self):
        """Test DocumentSerializer with valid data."""
        factory = APIRequestFactory()
        user = User.objects.create_user(username='testuser', email='test@example.com')
        program = Program.objects.create(
            name='Test Program',
            description='A test program',
            start_date='2023-01-01',
            end_date='2023-12-31'
        )
        status = ApplicationStatus.objects.get_or_create(name='submitted')[0]
        application = Application.objects.create(
            program=program,
            student=user,
            status=status
        )
        document_type = DocumentType.objects.create(
            name='Test Document',
            description='A test document type'
        )

        file_content = b"test file content"
        file = SimpleUploadedFile("test.pdf", file_content, content_type="application/pdf")

        data = {
            'application': application.id,
            'type': document_type.id,
            'file': file,
            'uploaded_by': user.id
        }

        # Create a request with the user
        request = factory.post('/api/documents/', data)
        request.user = user

        with patch('documents.serializers.DocumentService.validate_file_type_and_size'):
            with patch('documents.serializers.DocumentService.virus_scan', return_value=True):
                with patch('documents.serializers.DocumentService.upload_document') as mock_upload:
                    mock_upload.return_value = Document.objects.create(
                        application=application,
                        type=document_type,
                        file=file,
                        uploaded_by=user
                    )

                    serializer = serializers.DocumentSerializer(data=data, context={'request': request})
                    assert serializer.is_valid()
                    document = serializer.save()
                    assert document.application == application
                    assert document.type == document_type

    def test_document_serializer_invalid_file_type(self):
        """Test DocumentSerializer with invalid file type."""
        user = User.objects.create_user(username='testuser', email='test@example.com')
        program = Program.objects.create(
            name='Test Program',
            description='A test program',
            start_date='2023-01-01',
            end_date='2023-12-31'
        )
        status = ApplicationStatus.objects.get_or_create(name='submitted')[0]
        application = Application.objects.create(
            program=program,
            student=user,
            status=status
        )
        document_type = DocumentType.objects.create(
            name='Test Document',
            description='A test document type'
        )

        file_content = b"test file content"
        file = SimpleUploadedFile("test.txt", file_content, content_type="text/plain")

        data = {
            'application': application.id,
            'type': document_type.id,
            'file': file,
            'uploaded_by': user.id
        }

        with patch('documents.serializers.DocumentService.validate_file_type_and_size') as mock_validate:
            mock_validate.side_effect = ValueError("Invalid file type")

            serializer = serializers.DocumentSerializer(data=data)
            # The ValueError should be raised during validation
            with pytest.raises(ValueError, match="Invalid file type"):
                serializer.is_valid()

    def test_document_serializer_virus_scan_failed(self):
        """Test DocumentSerializer when virus scan fails."""
        user = User.objects.create_user(username='testuser', email='test@example.com')
        program = Program.objects.create(
            name='Test Program',
            description='A test program',
            start_date='2023-01-01',
            end_date='2023-12-31'
        )
        status = ApplicationStatus.objects.get_or_create(name='submitted')[0]
        application = Application.objects.create(
            program=program,
            student=user,
            status=status
        )
        document_type = DocumentType.objects.create(
            name='Test Document',
            description='A test document type'
        )

        file_content = b"test file content"
        file = SimpleUploadedFile("test.pdf", file_content, content_type="application/pdf")

        data = {
            'application': application.id,
            'type': document_type.id,
            'file': file,
            'uploaded_by': user.id
        }

        with patch('documents.serializers.DocumentService.validate_file_type_and_size'):
            with patch('documents.serializers.DocumentService.virus_scan', return_value=False):
                serializer = serializers.DocumentSerializer(data=data)
                assert not serializer.is_valid()
                assert 'file' in serializer.errors
                assert 'virus scan' in str(serializer.errors['file'][0])

    def test_document_serializer_update_success(self):
        """Test DocumentSerializer update with valid data."""
        factory = APIRequestFactory()
        user = User.objects.create_user(username='testuser', email='test@example.com')
        program = Program.objects.create(
            name='Test Program',
            description='A test program',
            start_date='2023-01-01',
            end_date='2023-12-31'
        )
        status = ApplicationStatus.objects.get_or_create(name='submitted')[0]
        application = Application.objects.create(
            program=program,
            student=user,
            status=status
        )
        document_type = DocumentType.objects.create(
            name='Test Document',
            description='A test document type'
        )

        document = Document.objects.create(
            application=application,
            type=document_type,
            file=SimpleUploadedFile("old.pdf", b"old content"),
            uploaded_by=user
        )

        new_file = SimpleUploadedFile("new.pdf", b"new content", content_type="application/pdf")
        data = {'file': new_file}

        request = factory.get('/')
        request.user = user

        with patch('documents.serializers.DocumentService.can_replace_document', return_value=True):
            with patch('documents.serializers.DocumentService.validate_file_type_and_size'):
                with patch('documents.serializers.DocumentService.virus_scan', return_value=True):
                    serializer = serializers.DocumentSerializer(
                        document,
                        data=data,
                        context={'request': request},
                        partial=True
                    )
                    assert serializer.is_valid()
                    updated_document = serializer.save()
                    assert updated_document == document

    def test_document_serializer_update_replacement_not_allowed(self):
        """Test DocumentSerializer update when replacement is not allowed."""
        factory = APIRequestFactory()
        user = User.objects.create_user(username='testuser', email='test@example.com')
        program = Program.objects.create(
            name='Test Program',
            description='A test program',
            start_date='2023-01-01',
            end_date='2023-12-31'
        )
        status = ApplicationStatus.objects.get_or_create(name='submitted')[0]
        application = Application.objects.create(
            program=program,
            student=user,
            status=status
        )
        document_type = DocumentType.objects.create(
            name='Test Document',
            description='A test document type'
        )

        document = Document.objects.create(
            application=application,
            type=document_type,
            file=SimpleUploadedFile("old.pdf", b"old content"),
            uploaded_by=user
        )

        new_file = SimpleUploadedFile("new.pdf", b"new content", content_type="application/pdf")
        data = {'file': new_file}

        request = factory.get('/')
        request.user = user

        with patch('documents.serializers.DocumentService.can_replace_document', return_value=False):
            with patch('documents.serializers.DocumentService.validate_file_type_and_size'):
                with patch('documents.serializers.DocumentService.virus_scan', return_value=True):
                    serializer = serializers.DocumentSerializer(
                        document,
                        data=data,
                        context={'request': request},
                        partial=True
                    )
                    assert serializer.is_valid()
                    import rest_framework
                    with pytest.raises(rest_framework.serializers.ValidationError):
                        serializer.save()

@pytest.mark.django_db
class TestDocumentValidationSerializer:
    def test_document_validation_serializer_valid(self):
        """Test DocumentValidationSerializer with valid data."""
        user = User.objects.create_user(username='testuser', email='test@example.com')
        document_type = DocumentType.objects.create(name='Test Document')
        program = Program.objects.create(
            name='Test Program',
            description='A test program',
            start_date='2023-01-01',
            end_date='2023-12-31'
        )
        status = ApplicationStatus.objects.get_or_create(name='submitted')[0]
        application = Application.objects.create(
            program=program,
            student=user,
            status=status
        )
        document = Document.objects.create(
            application=application,
            type=document_type,
            file=SimpleUploadedFile("test.pdf", b"test content"),
            uploaded_by=user
        )

        data = {
            'document': document.id,
            'validator': user.id,
            'result': 'PASSED',
            'details': 'Document passed all validation checks'
        }

        serializer = serializers.DocumentValidationSerializer(data=data)
        assert serializer.is_valid()

        validation = serializer.save()
        assert validation.document == document
        assert validation.validator == user
        assert validation.result == 'PASSED'

@pytest.mark.django_db
class TestDocumentResubmissionRequestSerializer:
    def test_document_resubmission_request_serializer_valid(self):
        """Test DocumentResubmissionRequestSerializer with valid data."""
        factory = APIRequestFactory()
        user = User.objects.create_user(username='testuser', email='test@example.com')
        document_type = DocumentType.objects.create(name='Test Document')
        program = Program.objects.create(
            name='Test Program',
            description='A test program',
            start_date='2023-01-01',
            end_date='2023-12-31'
        )
        status = ApplicationStatus.objects.get_or_create(name='submitted')[0]
        application = Application.objects.create(
            program=program,
            student=user,
            status=status
        )
        document = Document.objects.create(
            application=application,
            type=document_type,
            file=SimpleUploadedFile("test.pdf", b"test content"),
            uploaded_by=user
        )

        data = {
            'document': document.id,
            'reason': 'Document is unclear and needs to be resubmitted',
            'resolved': False
        }

        # Create a request with the user
        request_obj = factory.post('/api/document-resubmissions/', data)
        request_obj.user = user

        serializer = serializers.DocumentResubmissionRequestSerializer(data=data, context={'request': request_obj})
        assert serializer.is_valid()

        request = serializer.save()
        assert request.document == document
        assert request.requested_by == user
        assert request.reason == 'Document is unclear and needs to be resubmitted'
        assert not request.resolved

@pytest.mark.django_db
class TestDocumentCommentSerializer:
    def test_document_comment_serializer_valid(self):
        """Test DocumentCommentSerializer with valid data."""
        factory = APIRequestFactory()
        user = User.objects.create_user(username='testuser', email='test@example.com')
        document_type = DocumentType.objects.create(name='Test Document')
        program = Program.objects.create(
            name='Test Program',
            description='A test program',
            start_date='2023-01-01',
            end_date='2023-12-31'
        )
        status = ApplicationStatus.objects.get_or_create(name='submitted')[0]
        application = Application.objects.create(
            program=program,
            student=user,
            status=status
        )
        document = Document.objects.create(
            application=application,
            type=document_type,
            file=SimpleUploadedFile("test.pdf", b"test content"),
            uploaded_by=user
        )

        data = {
            'document': document.id,
            'text': 'This document looks good',
            'is_private': False
        }

        # Create a request with the user
        request_obj = factory.post('/api/document-comments/', data)
        request_obj.user = user

        serializer = serializers.DocumentCommentSerializer(data=data, context={'request': request_obj})
        assert serializer.is_valid()

        comment = serializer.save()
        assert comment.document == document
        assert comment.author == user
        assert comment.text == 'This document looks good'
        assert not comment.is_private

    def test_document_comment_serializer_private_comment(self):
        """Test DocumentCommentSerializer with private comment."""
        factory = APIRequestFactory()
        user = User.objects.create_user(username='testuser', email='test@example.com')
        document_type = DocumentType.objects.create(name='Test Document')
        program = Program.objects.create(
            name='Test Program',
            description='A test program',
            start_date='2023-01-01',
            end_date='2023-12-31'
        )
        status = ApplicationStatus.objects.get_or_create(name='submitted')[0]
        application = Application.objects.create(
            program=program,
            student=user,
            status=status
        )
        document = Document.objects.create(
            application=application,
            type=document_type,
            file=SimpleUploadedFile("test.pdf", b"test content"),
            uploaded_by=user
        )

        data = {
            'document': document.id,
            'text': 'Internal note: Document needs review',
            'is_private': True
        }

        # Create a request with the user
        request_obj = factory.post('/api/document-comments/', data)
        request_obj.user = user

        serializer = serializers.DocumentCommentSerializer(data=data, context={'request': request_obj})
        assert serializer.is_valid()

        comment = serializer.save()
        assert comment.is_private
