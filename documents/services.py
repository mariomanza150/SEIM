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

from django.core.exceptions import ValidationError

from notifications.services import NotificationService

from .models import Document, DocumentResubmissionRequest, DocumentType, DocumentValidation
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
        NotificationService.broadcast_application_sync(
            str(application.id), "document_uploaded", str(document.id)
        )
        return document

    @staticmethod
    def user_can_access_document(user, document: Document) -> bool:
        """Whether the user may view or comment on this application document."""
        if getattr(user, "has_role", None):
            if user.has_role("coordinator") or user.has_role("admin"):
                return True
        return (
            document.uploaded_by_id == user.id
            or document.application.student_id == user.id
        )

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
        NotificationService.broadcast_application_sync(
            str(document.application_id), "document_validated", str(document.id)
        )
        if result != "valid":
            DocumentService._notify_student_document_invalid(document, details)
        return validation

    @staticmethod
    def _notify_student_document_invalid(document: Document, details: str) -> None:
        from notifications.services import NotificationService

        msg = (details or "").strip()
        if not msg:
            msg = (
                f"Your {document.type.name} was not accepted. "
                "Please review staff comments or resubmission requests on the document page."
            )
        NotificationService.send_notification(
            document.application.student,
            "Document not accepted",
            msg,
            notification_type="both",
            action_url=f"/documents/{document.id}/",
            action_text="View document",
            category="warning",
            settings_category="documents",
        )

    @staticmethod
    def notify_coordinators_document_replaced(document: Document) -> None:
        """Notify program/assignment staff when the student uploads a new file."""
        from notifications.services import NotificationService

        app = document.application
        student = app.student
        label = student.get_full_name().strip() or student.username
        recipients = []
        if app.assigned_coordinator_id:
            recipients.append(app.assigned_coordinator)
        else:
            recipients = list(app.program.coordinators.all()[:10])
        if not recipients:
            return
        body = f"{label} uploaded a new file for {document.type.name}."
        for user in recipients:
            NotificationService.send_notification(
                user,
                "Document resubmitted",
                body,
                notification_type="both",
                action_url=f"/documents/{document.id}/",
                action_text="Review document",
                category="info",
                settings_category="documents",
            )
        NotificationService.broadcast_application_sync(
            str(app.id), "document_replaced", str(document.id)
        )

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

        student = document.application.student
        NotificationService.send_notification(
            student,
            "Document resubmission requested",
            f"{document.type.name}: {reason}",
            notification_type="both",
            action_url=f"/documents/{document.id}/",
            action_text="View document",
            category="warning",
            settings_category="documents",
        )
        NotificationService.broadcast_application_sync(
            str(document.application_id), "document_resubmission_requested", str(document.id)
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

    @staticmethod
    def build_application_document_checklist(application):
        """
        Compare program required document types to uploads on this application.

        Status per type (latest upload for that type): missing, pending_review,
        resubmit_requested, approved.
        """
        program = application.program
        required = list(program.required_document_types.all().order_by("name"))
        if not required:
            return {
                "complete": True,
                "required_count": 0,
                "approved_count": 0,
                "items": [],
            }

        items = []
        approved_count = 0
        for dt in required:
            latest = (
                Document.objects.filter(application=application, type=dt)
                .order_by("-created_at")
                .first()
            )
            entry = {
                "document_type_id": dt.id,
                "name": dt.name,
                "description": dt.description or "",
                "status": "missing",
                "document_id": None,
                "resubmission_reason": None,
            }
            if not latest:
                items.append(entry)
                continue

            entry["document_id"] = str(latest.id)
            open_req = (
                DocumentResubmissionRequest.objects.filter(document=latest, resolved=False)
                .order_by("-requested_at")
                .first()
            )
            if open_req:
                entry["status"] = "resubmit_requested"
                entry["resubmission_reason"] = open_req.reason
            elif latest.is_valid:
                entry["status"] = "approved"
                approved_count += 1
            else:
                entry["status"] = "pending_review"
            items.append(entry)

        return {
            "complete": approved_count == len(required),
            "required_count": len(required),
            "approved_count": approved_count,
            "items": items,
        }

    @staticmethod
    def ensure_required_documents_approved(application):
        """Raise ValueError if required document types are not all approved."""
        summary = DocumentService.build_application_document_checklist(application)
        if summary["complete"]:
            return
        problems = [
            f"{item['name']} ({item['status']})"
            for item in summary["items"]
            if item["status"] != "approved"
        ]
        raise ValueError(
            "Required documents are not all approved yet: " + "; ".join(problems)
        )

    @staticmethod
    def intersect_program_required_document_type_ids(program, candidate_ids):
        """
        Document types listed on a form step that are also required for the program,
        preserving step order.
        """
        if not candidate_ids:
            return []
        required_set = set(program.required_document_types.values_list("id", flat=True))
        out = []
        for x in candidate_ids:
            try:
                pk = int(x)
            except (TypeError, ValueError):
                continue
            if pk in required_set:
                out.append(pk)
        return out

    @staticmethod
    def step_required_document_types_meta(program, step_layout_entry):
        """Resolved document types for a step (intersection with program requirements)."""
        ids = step_layout_entry.get("required_document_type_ids") or []
        eff = DocumentService.intersect_program_required_document_type_ids(program, ids)
        if not eff:
            return []
        return list(
            DocumentType.objects.filter(pk__in=eff)
            .order_by("name")
            .values("id", "name", "description")
        )

    @staticmethod
    def enrich_form_steps_for_program(form_type, program):
        """Attach required_document_types metadata to each step for API consumers."""
        steps = form_type.get_multi_step_layout()
        out = []
        for s in steps:
            meta = DocumentService.step_required_document_types_meta(program, s)
            row = {**s, "required_document_types": meta}
            out.append(row)
        return out

    @staticmethod
    def ensure_step_documents_approved(application, form_type, completed_step_key: str):
        """
        Before advancing past a multi-step form step, ensure that document types
        configured on that step (and required by the program) are approved uploads.
        """
        if not form_type.is_multi_step():
            return
        step_def = None
        for s in form_type.step_definitions or []:
            if str(s.get("key", "")) == str(completed_step_key):
                step_def = s
                break
        if not step_def:
            return
        raw_ids = step_def.get("required_document_type_ids") or []
        if not isinstance(raw_ids, list) or not raw_ids:
            return
        try:
            candidate = [int(x) for x in raw_ids]
        except (TypeError, ValueError):
            raise ValidationError("Invalid required_document_type_ids on form step.") from None
        effective = DocumentService.intersect_program_required_document_type_ids(
            application.program, candidate
        )
        if not effective:
            return
        summary = DocumentService.build_application_document_checklist(application)
        by_id = {item["document_type_id"]: item for item in summary["items"]}
        problems = []
        for dt_id in effective:
            item = by_id.get(dt_id)
            if not item or item["status"] != "approved":
                name = item["name"] if item else f"Document type #{dt_id}"
                st = item["status"] if item else "missing"
                problems.append(f"{name} ({st})")
        if problems:
            raise ValidationError(
                "Upload and get approval for required documents before continuing: "
                + "; ".join(problems)
            )
