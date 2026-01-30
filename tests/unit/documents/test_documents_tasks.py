"""
Comprehensive tests for document tasks.

Tests for virus scanning and document processing Celery tasks.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from documents.models import Document, DocumentValidation
from documents.tasks import scan_document_virus

User = get_user_model()


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )


@pytest.fixture
def document(user, db):
    """Create a test document."""
    file = SimpleUploadedFile(
        "test.pdf",
        b"PDF file content",
        content_type="application/pdf"
    )
    
    doc = Document.objects.create(
        name="Test Document",
        file=file,
        file_type="application/pdf",
        uploaded_by=user,
        is_valid=False
    )
    return doc


@pytest.mark.django_db
@pytest.mark.celery
class TestScanDocumentVirusTask:
    """Test virus scanning Celery task."""
    
    def test_scan_document_virus_clean_file(self, document):
        """Test scanning a clean file."""
        validator_id = "validator_001"
        
        with patch('documents.tasks.scan_file_for_viruses') as mock_scan:
            # Mock clean scan result
            mock_scan.return_value = (True, None)
            
            result = scan_document_virus(str(document.id), validator_id)
            
            # Verify task completed successfully
            assert "scanned: valid" in result
            
            # Verify document was updated
            document.refresh_from_db()
            assert document.is_valid is True
            assert document.validated_at is not None
            
            # Verify validation record created
            validation = DocumentValidation.objects.filter(
                document=document,
                validator_id=validator_id
            ).first()
            
            assert validation is not None
            assert validation.result == "valid"
            assert "Scanned by async task" in validation.details
    
    def test_scan_document_virus_infected_file(self, document):
        """Test scanning an infected file."""
        validator_id = "validator_002"
        threat_name = "EICAR-Test-File"
        
        with patch('documents.tasks.scan_file_for_viruses') as mock_scan:
            # Mock infected file result
            mock_scan.return_value = (False, threat_name)
            
            result = scan_document_virus(str(document.id), validator_id)
            
            # Verify task completed
            assert "scanned: infected" in result
            
            # Verify document marked invalid
            document.refresh_from_db()
            assert document.is_valid is False
            assert document.validated_at is not None
            
            # Verify validation record with threat name
            validation = DocumentValidation.objects.filter(
                document=document,
                validator_id=validator_id
            ).first()
            
            assert validation is not None
            assert validation.result == "infected"
            assert threat_name in validation.details
    
    def test_scan_document_virus_file_not_found(self, document):
        """Test scanning when file doesn't exist."""
        validator_id = "validator_003"
        
        # Remove the file
        document.file = None
        document.save()
        
        result = scan_document_virus(str(document.id), validator_id)
        
        # Verify error handled
        assert "scanned: error" in result
        
        # Verify validation record created
        validation = DocumentValidation.objects.filter(
            document=document,
            validator_id=validator_id
        ).first()
        
        assert validation is not None
        assert validation.result == "error"
        assert "File not found" in validation.details
    
    def test_scan_document_virus_scan_error(self, document):
        """Test handling of scan failures."""
        validator_id = "validator_004"
        
        with patch('documents.tasks.scan_file_for_viruses') as mock_scan:
            # Mock scan error
            mock_scan.side_effect = Exception("Scanner unavailable")
            
            result = scan_document_virus(str(document.id), validator_id)
            
            # Verify error handled
            assert "scanned: error" in result
            
            # Verify validation record
            validation = DocumentValidation.objects.filter(
                document=document,
                validator_id=validator_id
            ).first()
            
            assert validation is not None
            assert validation.result == "error"
            assert "Scan failed" in validation.details
    
    def test_scan_document_virus_document_not_found(self):
        """Test scanning non-existent document."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        validator_id = "validator_005"
        
        result = scan_document_virus(fake_id, validator_id)
        
        # Verify error message returned
        assert "not found" in result
    
    def test_scan_document_virus_task_exception(self, document):
        """Test task handles unexpected exceptions."""
        validator_id = "validator_006"
        
        with patch('documents.tasks.scan_file_for_viruses') as mock_scan:
            # Mock unexpected exception
            mock_scan.side_effect = RuntimeError("Unexpected error")
            
            result = scan_document_virus(str(document.id), validator_id)
            
            # Verify task doesn't crash
            assert "scanned: error" in result or "failed" in result.lower()
            
            # Verify document updated
            document.refresh_from_db()
            assert document.validated_at is not None
    
    def test_scan_document_virus_updates_existing_validation(self, document):
        """Test that scanning updates document status."""
        validator_id = "validator_007"
        
        # Create initial validation
        DocumentValidation.objects.create(
            document=document,
            validator_id=validator_id,
            result="pending",
            details="Scan in progress",
            validated_at=timezone.now()
        )
        
        with patch('documents.tasks.scan_file_for_viruses') as mock_scan:
            mock_scan.return_value = (True, None)
            
            scan_document_virus(str(document.id), validator_id)
            
            # Verify new validation record created
            validations = DocumentValidation.objects.filter(
                document=document,
                validator_id=validator_id
            )
            
            # Should have 2 validations now
            assert validations.count() == 2
    
    def test_scan_document_virus_multiple_concurrent_scans(self, document):
        """Test multiple concurrent scans of same document."""
        validator_id_1 = "validator_008"
        validator_id_2 = "validator_009"
        
        with patch('documents.tasks.scan_file_for_viruses') as mock_scan:
            mock_scan.return_value = (True, None)
            
            # Simulate concurrent scans
            result1 = scan_document_virus(str(document.id), validator_id_1)
            result2 = scan_document_virus(str(document.id), validator_id_2)
            
            # Both should complete successfully
            assert "scanned: valid" in result1
            assert "scanned: valid" in result2
            
            # Verify separate validation records
            assert DocumentValidation.objects.filter(
                document=document,
                validator_id=validator_id_1
            ).exists()
            
            assert DocumentValidation.objects.filter(
                document=document,
                validator_id=validator_id_2
            ).exists()
    
    def test_scan_document_virus_with_file_path(self, document):
        """Test scanning actually calls scan function with correct path."""
        validator_id = "validator_010"
        
        with patch('documents.tasks.scan_file_for_viruses') as mock_scan:
            mock_scan.return_value = (True, None)
            
            scan_document_virus(str(document.id), validator_id)
            
            # Verify scan was called with file path
            mock_scan.assert_called_once()
            call_args = mock_scan.call_args[0]
            assert len(call_args) > 0
            # The path should be the document's file path
            assert str(call_args[0]) == str(document.file.path)
    
    def test_scan_document_virus_validation_timestamp(self, document):
        """Test that validation timestamp is set correctly."""
        validator_id = "validator_011"
        start_time = timezone.now()
        
        with patch('documents.tasks.scan_file_for_viruses') as mock_scan:
            mock_scan.return_value = (True, None)
            
            scan_document_virus(str(document.id), validator_id)
            
            end_time = timezone.now()
            
            # Verify validation timestamp is within expected range
            validation = DocumentValidation.objects.get(
                document=document,
                validator_id=validator_id
            )
            
            assert start_time <= validation.validated_at <= end_time
            
            # Verify document validated_at also set
            document.refresh_from_db()
            assert start_time <= document.validated_at <= end_time
    
    def test_scan_document_virus_preserves_document_metadata(self, document):
        """Test that scanning doesn't affect document metadata."""
        validator_id = "validator_012"
        original_name = document.name
        original_type = document.file_type
        original_uploaded_by = document.uploaded_by
        original_created_at = document.created_at
        
        with patch('documents.tasks.scan_file_for_viruses') as mock_scan:
            mock_scan.return_value = (True, None)
            
            scan_document_virus(str(document.id), validator_id)
            
            # Verify metadata unchanged
            document.refresh_from_db()
            assert document.name == original_name
            assert document.file_type == original_type
            assert document.uploaded_by == original_uploaded_by
            assert document.created_at == original_created_at
    
    def test_scan_document_virus_secondary_error_handling(self, document):
        """Test secondary error handling when validation creation fails."""
        validator_id = "validator_013"
        
        with patch('documents.tasks.scan_file_for_viruses') as mock_scan:
            # First call succeeds
            mock_scan.return_value = (True, None)
            
            # But creating validation fails due to DB error
            with patch('documents.models.DocumentValidation.objects.create') as mock_create:
                mock_create.side_effect = Exception("DB error")
                
                # Task should handle this gracefully
                result = scan_document_virus(str(document.id), validator_id)
                
                # Should still return a result (not crash)
                assert isinstance(result, str)
    
    def test_scan_document_virus_result_format(self, document):
        """Test that task returns proper result format."""
        validator_id = "validator_014"
        
        with patch('documents.tasks.scan_file_for_viruses') as mock_scan:
            mock_scan.return_value = (True, None)
            
            result = scan_document_virus(str(document.id), validator_id)
            
            # Verify result format
            assert isinstance(result, str)
            assert str(document.id) in result
            assert "scanned" in result.lower() or "scan" in result.lower()
    
    def test_scan_document_virus_idempotency(self, document):
        """Test that scanning same document multiple times is safe."""
        validator_id = "validator_015"
        
        with patch('documents.tasks.scan_file_for_viruses') as mock_scan:
            mock_scan.return_value = (True, None)
            
            # Scan multiple times
            for i in range(3):
                result = scan_document_virus(str(document.id), f"{validator_id}_{i}")
                assert "scanned" in result.lower()
            
            # Document should still be in valid state
            document.refresh_from_db()
            assert document.is_valid is True
            
            # Should have 3 validation records
            assert DocumentValidation.objects.filter(
                document=document
            ).count() == 3


@pytest.mark.django_db
class TestDocumentTaskIntegration:
    """Integration tests for document tasks with real objects."""
    
    def test_full_scan_workflow(self, document):
        """Test complete scan workflow from start to finish."""
        validator_id = "integration_validator"
        
        # Verify initial state
        assert document.is_valid is False
        assert document.validated_at is None
        
        with patch('documents.tasks.scan_file_for_viruses') as mock_scan:
            mock_scan.return_value = (True, None)
            
            # Run scan task
            result = scan_document_virus(str(document.id), validator_id)
            
            # Verify complete workflow
            assert "valid" in result.lower()
            
            # Check document updated
            document.refresh_from_db()
            assert document.is_valid is True
            assert document.validated_at is not None
            
            # Check validation created
            validation = DocumentValidation.objects.get(
                document=document,
                validator_id=validator_id
            )
            assert validation.result == "valid"
            assert validation.validated_at is not None
    
    def test_infected_file_workflow(self, document):
        """Test workflow for infected file detection."""
        validator_id = "infected_validator"
        
        with patch('documents.tasks.scan_file_for_viruses') as mock_scan:
            mock_scan.return_value = (False, "Trojan.Generic")
            
            # Run scan task
            result = scan_document_virus(str(document.id), validator_id)
            
            # Verify infected handling
            assert "infected" in result.lower()
            
            # Document should be marked invalid
            document.refresh_from_db()
            assert document.is_valid is False
            
            # Validation should record threat
            validation = DocumentValidation.objects.get(
                document=document,
                validator_id=validator_id
            )
            assert validation.result == "infected"
            assert "Trojan" in validation.details
