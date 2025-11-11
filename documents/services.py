import logging
import mimetypes
import os

# Disable magic on Windows to avoid access violations
import sys

from django.db import transaction
from django.utils import timezone

# Initialize magic module and availability flag
magic = None
MAGIC_AVAILABLE = False

if not sys.platform.startswith('win'):
    # Try to import pylibmagic before magic for compatibility with Python 3.12
    try:
        try:
            import pylibmagic  # noqa: F401  # Ensures libmagic is available for python-magic
        except ImportError:
            pass  # pylibmagic is optional, only needed for python-magic compatibility
        import magic
        MAGIC_AVAILABLE = True
    except (ImportError, OSError, Exception):
        magic = None
        MAGIC_AVAILABLE = False

from notifications.services import NotificationService

from .models import Document, DocumentResubmissionRequest, DocumentValidation
from .tasks import scan_document_virus


class DocumentService:
    """
    Service for document upload, validation, and resubmission workflows.
    """

    ALLOWED_FILE_TYPES = ["application/pdf", "image/jpeg", "image/png"]
    MAX_FILE_SIZE_MB = 10
    MAX_RESUBMISSIONS = 3

    @staticmethod
    def validate_file_type_and_size(file):
        """Check file type and size against allowed types and max size."""
        file.seek(0)

        # Use magic if available, otherwise fallback to mimetypes
        if MAGIC_AVAILABLE and magic is not None:
            mime_type = magic.from_buffer(file.read(2048), mime=True)
        else:
            # Fallback to mimetypes for Windows compatibility
            file.read(2048)
            mime_type, _ = mimetypes.guess_type(file.name)
            if not mime_type:
                # Try to guess from file extension
                mime_type = mimetypes.guess_type(file.name)[0] or 'application/octet-stream'

        file.seek(0)
        if mime_type not in DocumentService.ALLOWED_FILE_TYPES:
            raise ValueError("File type not allowed.")
        if file.size > DocumentService.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise ValueError("File size exceeds maximum allowed.")
        return True

    @staticmethod
    def virus_scan(file):
        """Scan file for viruses using configured virus scanner."""
        # Save file to temporary location for scanning
        import tempfile

        from .virus_scanner import scan_file_for_viruses

        # Get file content
        file.seek(0)
        file_content = file.read()
        file.seek(0)  # Reset file pointer

        # Create temporary file for scanning
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.name)[1]) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        try:
            # Scan the temporary file
            is_clean, threat_name = scan_file_for_viruses(temp_file_path)
            return is_clean
        except Exception as e:
            # Log the error and return False (file rejected)
            logger = logging.getLogger(__name__)
            logger.error(f"Virus scan failed: {e}")
            return False
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    @staticmethod
    @transaction.atomic
    def upload_document(application, doc_type, file, uploaded_by):
        """Upload a new document for an application with file type/size and virus scan validation."""
        DocumentService.validate_file_type_and_size(file)
        # Async virus scan
        document = Document.objects.create(
            application=application, type=doc_type, file=file, uploaded_by=uploaded_by
        )
        scan_document_virus.delay(str(document.id), str(uploaded_by.id))
        return document

    @staticmethod
    @transaction.atomic
    def validate_document(document: Document, validator, result, details=""):
        """Validate a document (virus scan, integrity check, etc.)."""
        validation = DocumentValidation.objects.create(
            document=document, validator=validator, result=result, details=details
        )
        document.is_valid = result == "valid"
        document.validated_at = timezone.now()
        document.save()
        return validation

    @staticmethod
    def can_request_resubmission(document):
        """Limit the number of resubmissions per document."""
        return (
            DocumentResubmissionRequest.objects.filter(document=document).count()
            < DocumentService.MAX_RESUBMISSIONS
        )

    @staticmethod
    @transaction.atomic
    def request_resubmission(document: Document, requested_by, reason):
        """Request a resubmission for a document, enforcing resubmission limit."""
        if not DocumentService.can_request_resubmission(document):
            raise ValueError("Maximum number of resubmissions reached.")
        req = DocumentResubmissionRequest.objects.create(
            document=document, requested_by=requested_by, reason=reason
        )

        # Notify student about document resubmission request
        NotificationService.send_notification(
            document.uploaded_by,
            "document_resubmission_request",
            f"Document resubmission requested for {document.type.name}. Reason: {reason}",
        )

        return req

    @staticmethod
    def can_replace_document(document: Document, user):
        """Check if document can be replaced based on application status and resubmission requests."""
        application = document.application

        # If application is still in draft, allow replacement
        if application.status.name == "draft":
            return True

        # If application is submitted or later, check for resubmission request
        if application.status.name in [
            "submitted",
            "under_review",
            "approved",
            "rejected",
        ]:
            # Check if there's a pending resubmission request for this document
            has_pending_request = DocumentResubmissionRequest.objects.filter(
                document=document, resolved=False
            ).exists()

            if has_pending_request:
                return True

            # Allow admins to override
            if hasattr(user, "role") and user.role == "admin":
                return True

            return False

        return False
