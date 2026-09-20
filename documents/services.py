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

if not sys.platform.startswith("win"):
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

from .models import (
    Document,
    DocumentResubmissionRequest,
    DocumentType,
    DocumentValidation,
)
from .tasks import scan_document_virus


class DocumentService:
    """
    Service for document upload, validation, and resubmission workflows.
    """

    ALLOWED_FILE_TYPES = ["application/pdf", "image/jpeg", "image/png"]
    # Keep in sync with frontend-vue/src/utils/documentApi.js DEFAULT_ACCEPTED_EXTENSIONS.
    DEFAULT_ACCEPTED_EXTENSIONS = ["pdf", "jpg", "jpeg", "png"]
    EXTENSION_MIME = {
        "pdf": "application/pdf",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
        "bmp": "image/bmp",
        "tif": "image/tiff",
        "tiff": "image/tiff",
        "heic": "image/heic",
        "heif": "image/heif",
        "doc": "application/msword",
        "docx": (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        "odt": "application/vnd.oasis.opendocument.text",
        "rtf": "application/rtf",
        "xls": "application/vnd.ms-excel",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "ods": "application/vnd.oasis.opendocument.spreadsheet",
        "csv": "text/csv",
        "ppt": "application/vnd.ms-powerpoint",
        "pptx": (
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        ),
        "odp": "application/vnd.oasis.opendocument.presentation",
        "txt": "text/plain",
        "md": "text/markdown",
        "zip": "application/zip",
        "7z": "application/x-7z-compressed",
        "rar": "application/vnd.rar",
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "m4a": "audio/mp4",
        "mp4": "video/mp4",
        "mov": "video/quicktime",
        "webm": "video/webm",
        "eml": "message/rfc822",
        "msg": "application/vnd.ms-outlook",
    }
    MAX_FILE_SIZE_MB = 10
    MAX_RESUBMISSIONS = 3

    @staticmethod
    def _detect_mime(file) -> str:
        file.seek(0)
        if MAGIC_AVAILABLE and magic is not None:
            mime_type = magic.from_buffer(file.read(2048), mime=True)
        else:
            file.read(2048)
            mime_type, _ = mimetypes.guess_type(file.name)
            if not mime_type:
                mime_type = (
                    mimetypes.guess_type(file.name)[0] or "application/octet-stream"
                )
        file.seek(0)
        return mime_type or "application/octet-stream"

    @staticmethod
    def validate_file_type_and_size(file, document_type: DocumentType | None = None):
        """Check file type and size against allowed types and max size (per-type overrides)."""
        mime_type = DocumentService._detect_mime(file)

        allowed_mimes = list(DocumentService.ALLOWED_FILE_TYPES)
        if document_type is not None:
            exts = document_type.parsed_accepted_extensions()
            if exts:
                allowed_mimes = []
                seen = set()
                for ext in exts:
                    mime = DocumentService.EXTENSION_MIME.get(ext)
                    if not mime:
                        mime, _ = mimetypes.guess_type(f"file.{ext}")
                    if mime and mime not in seen:
                        seen.add(mime)
                        allowed_mimes.append(mime)
                if not allowed_mimes:
                    allowed_mimes = list(DocumentService.ALLOWED_FILE_TYPES)

        if mime_type not in allowed_mimes:
            raise ValueError("File type not allowed.")

        max_mb = DocumentService.MAX_FILE_SIZE_MB
        if document_type is not None and document_type.max_file_size_mb:
            max_mb = document_type.max_file_size_mb
        if file.size > max_mb * 1024 * 1024:
            raise ValueError("File size exceeds maximum allowed.")
        return True

    @staticmethod
    def resolved_accepted_extensions(document_type: DocumentType | None = None) -> list[str]:
        """Extensions for a type, falling back to global defaults when unset."""
        if document_type is not None:
            exts = document_type.parsed_accepted_extensions()
            if exts:
                return list(exts)
        return list(DocumentService.DEFAULT_ACCEPTED_EXTENSIONS)

    @staticmethod
    def resolved_accepted_extensions_csv(document_type: DocumentType | None = None) -> str:
        return ",".join(DocumentService.resolved_accepted_extensions(document_type))

    @staticmethod
    def get_requirement_for_application(application, document_type):
        """Return ProgramDocumentRequirement for this application/type, if any."""
        from exchange.models import ProgramDocumentRequirement

        return (
            ProgramDocumentRequirement.objects.filter(
                program_id=application.program_id, document_type=document_type
            )
            .select_related("program", "document_type")
            .first()
        )

    @staticmethod
    def ensure_upload_allowed(
        application, document_type, *, for_staff=False, replacing=False
    ):
        """
        Block student uploads past per-doc deadline (staff may still review late uploads).
        Also enforce allows_multiple / instructions_only.
        """
        if (
            document_type.submission_mode
            == DocumentType.SubmissionMode.INSTRUCTIONS_ONLY
        ):
            raise ValueError(
                "This document type is instructions-only and does not accept uploads."
            )

        requirement = DocumentService.get_requirement_for_application(
            application, document_type
        )
        if requirement and requirement.is_overdue() and not for_staff:
            latest = (
                Document.objects.filter(application=application, type=document_type)
                .order_by("-created_at")
                .first()
            )
            open_resub = False
            if latest:
                open_resub = DocumentResubmissionRequest.objects.filter(
                    document=latest, resolved=False
                ).exists()
            if not open_resub:
                raise ValueError(
                    "The deadline for this document has passed; new uploads are not allowed."
                )

        if not replacing and not document_type.allows_multiple:
            existing_count = DocumentService.current_documents(
                application, document_type
            ).count()
            if existing_count > 0:
                raise ValueError(
                    "This document type allows only one file. Replace the existing upload instead."
                )

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
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=os.path.splitext(file.name)[1]
        ) as temp_file:
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
        """Upload a new document for an application with file type/size and virus scan validation.

        Only the applicant may upload. Staff review/approve/reject; they must not
        upload or replace files on the student's behalf.
        """
        if application.student_id != getattr(uploaded_by, "id", None):
            raise ValueError(
                "Only the applicant can upload documents for this application."
            )
        DocumentService.ensure_upload_allowed(
            application, doc_type, for_staff=False
        )
        DocumentService.validate_file_type_and_size(file, document_type=doc_type)
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
    def current_documents_qs(application, document_type=None):
        """Uploads that have not been superseded by a newer replace."""
        qs = Document.objects.filter(application=application)
        if document_type is not None:
            qs = qs.filter(type=document_type)
        return qs.filter(successors__isnull=True).order_by("-created_at")

    @staticmethod
    def current_documents(application, document_type=None):
        return DocumentService.current_documents_qs(application, document_type)

    @staticmethod
    def is_document_current(document: Document) -> bool:
        if DocumentService._related_is_prefetched(document, "successors"):
            return len(list(document.successors.all())) == 0
        return not document.successors.exists()

    @staticmethod
    def version_chain(document: Document) -> list:
        """Older versions only (walk supersedes), newest-first after the tip."""
        chain = []
        seen = set()
        current = document.supersedes
        while current is not None and current.id not in seen:
            seen.add(current.id)
            chain.append(current)
            current = current.supersedes
        return chain

    @staticmethod
    def filter_current_from_list(docs: list) -> list:
        """Keep docs that are not pointed at by another doc's supersedes in the list/DB."""
        if not docs:
            return []
        superseded_ids = {d.supersedes_id for d in docs if d.supersedes_id}
        # Also treat as superseded if a successor exists outside this list.
        current = []
        for doc in docs:
            if doc.id in superseded_ids:
                continue
            if DocumentService.is_document_current(doc):
                current.append(doc)
        return current

    @staticmethod
    def _status_for_single_upload(document: Document) -> str:
        open_req = DocumentService._open_resubmission_for(document)
        if open_req:
            return "resubmit_requested"
        if document.is_valid:
            return "approved"
        if document.validated_at:
            return "invalid"
        return "pending_review"

    @staticmethod
    def _aggregate_upload_status(current_uploads: list) -> tuple[str, object | None, str | None]:
        """
        Aggregate checklist status for current siblings.

        Priority: resubmit_requested > invalid > missing > pending_review > approved.
        Returns (status, primary_document, resubmission_reason).
        """
        if not current_uploads:
            return "missing", None, None

        statuses = []
        reason = None
        primary_resub = None
        for doc in current_uploads:
            st = DocumentService._status_for_single_upload(doc)
            statuses.append((st, doc))
            if st == "resubmit_requested" and reason is None:
                open_req = DocumentService._open_resubmission_for(doc)
                if open_req:
                    reason = open_req.reason
                    primary_resub = doc

        if any(st == "resubmit_requested" for st, _ in statuses):
            return "resubmit_requested", primary_resub or statuses[0][1], reason
        if any(st == "invalid" for st, _ in statuses):
            invalid_doc = next(doc for st, doc in statuses if st == "invalid")
            return "invalid", invalid_doc, None
        if any(st == "pending_review" for st, _ in statuses):
            pending_doc = next(doc for st, doc in statuses if st == "pending_review")
            return "pending_review", pending_doc, None
        # All approved — primary is newest
        return "approved", current_uploads[0], None

    @staticmethod
    @transaction.atomic
    def replace_document(document: Document, file, uploaded_by):
        """Create a new Document that supersedes ``document`` (keeps prior file)."""
        if not DocumentService.can_replace_document(document, uploaded_by):
            raise ValueError(
                "Document cannot be replaced. Only the applicant may replace a file "
                "before approval, or after staff marks it invalid / requests resubmission."
            )
        if not DocumentService.is_document_current(document):
            raise ValueError("Only the current version of a document can be replaced.")

        DocumentService.ensure_upload_allowed(
            document.application,
            document.type,
            for_staff=False,
            replacing=True,
        )
        DocumentService.validate_file_type_and_size(file, document_type=document.type)
        if not DocumentService.virus_scan(file):
            raise ValueError("File failed virus scan.")

        new_doc = Document.objects.create(
            application=document.application,
            type=document.type,
            file=file,
            uploaded_by=uploaded_by,
            supersedes=document,
            is_valid=False,
            validated_at=None,
        )
        DocumentService.resolve_open_resubmission_requests(document)
        scan_document_virus.delay(str(new_doc.id), str(uploaded_by.id))
        DocumentService.notify_coordinators_document_replaced(new_doc)
        return new_doc

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
            transactional_route_key="document_validation_rejected",
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
                transactional_route_key="document_replaced_staff",
            )
        NotificationService.broadcast_application_sync(
            str(app.id), "document_replaced", str(document.id)
        )

    @staticmethod
    def mark_resubmission_notifications_read(document: Document) -> int:
        """Clear leftover student inbox items for this document's resubmit request."""
        from notifications.models import Notification

        doc_id = str(document.id)
        return Notification.objects.filter(
            recipient_id=document.application.student_id,
            is_read=False,
            title="Document resubmission requested",
            action_url__contains=doc_id,
        ).update(is_read=True)

    @staticmethod
    def resolve_open_resubmission_requests(document: Document) -> int:
        """Mark pending resubmission requests as addressed after a new file is uploaded."""
        updated = DocumentResubmissionRequest.objects.filter(
            document=document, resolved=False
        ).update(resolved=True)
        DocumentService.mark_resubmission_notifications_read(document)
        return updated

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
            transactional_route_key="document_resubmission_requested",
        )
        NotificationService.broadcast_application_sync(
            str(document.application_id),
            "document_resubmission_requested",
            str(document.id),
        )

        return req

    @staticmethod
    def _has_open_resubmission(document: Document) -> bool:
        return DocumentResubmissionRequest.objects.filter(
            document=document, resolved=False
        ).exists()

    @staticmethod
    def document_is_locked_approved(document: Document) -> bool:
        """True when the upload is valid/approved and staff has not reopened it."""
        if not (document.is_valid and document.validated_at):
            return False
        return not DocumentService._has_open_resubmission(document)

    @staticmethod
    def can_replace_document(document: Document, user):
        """Whether the applicant may replace this file.

        - Only the application student may replace (staff review only).
        - Once marked valid/approved, locked until staff requests resubmission
          or marks the document invalid.
        - After submit, replacement is allowed across non-terminal statuses
          (under_review, nominated, waitlist, etc.) when resubmit is open or
          the document was marked invalid.
        """
        application = document.application

        if application.student_id != getattr(user, "id", None):
            return False

        if not DocumentService.is_document_current(document):
            return False

        if DocumentService.document_is_locked_approved(document):
            return False

        status_name = getattr(application.status, "name", "") or ""
        if status_name in {"cancelled", "completed"}:
            return False

        if status_name == "draft":
            return True

        has_pending_request = DocumentService._has_open_resubmission(document)
        if has_pending_request:
            return True
        if document.validated_at and not document.is_valid:
            return True
        return False

    @staticmethod
    def can_download_template(application, document_type, user) -> bool:
        """Whether the user may download a (prefilled) template for this requirement.

        Staff may always download. Students may not once their upload for this
        type is valid/approved (until staff requests resubmission or invalidates).
        """
        if getattr(user, "has_role", None) and (
            user.has_role("coordinator") or user.has_role("admin")
        ):
            return True
        if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
            return True
        if application.student_id != getattr(user, "id", None):
            return False

        latest = (
            DocumentService.current_documents(application, document_type)
            .select_related("type")
            .first()
        )
        if latest is None:
            return True
        return not DocumentService.document_is_locked_approved(latest)

    @staticmethod
    def _related_is_prefetched(instance, lookup: str) -> bool:
        cache = getattr(instance, "_prefetched_objects_cache", None)
        return bool(cache and lookup in cache)

    @staticmethod
    def _program_document_requirements(program):
        """Prefer prefetched through-model rows; otherwise query once."""
        from exchange.models import ProgramDocumentRequirement

        if DocumentService._related_is_prefetched(
            program, "program_document_requirements"
        ):
            reqs = list(program.program_document_requirements.all())
            reqs.sort(key=lambda r: (r.sort_order, r.id))
            return reqs
        return list(
            ProgramDocumentRequirement.objects.filter(program=program)
            .select_related("document_type", "required_from_status")
            .order_by("sort_order", "id")
        )

    @staticmethod
    def _uploads_by_type(application):
        """Group uploads by type_id using prefetch when available."""
        if DocumentService._related_is_prefetched(application, "document_set"):
            docs = list(application.document_set.all())
        else:
            docs = list(
                Document.objects.filter(application=application).select_related("type")
            )
        docs.sort(key=lambda d: d.created_at, reverse=True)
        by_type: dict = {}
        for doc in docs:
            by_type.setdefault(doc.type_id, []).append(doc)
        return by_type

    @staticmethod
    def _open_resubmission_for(document):
        """Latest unresolved resubmission; use prefetch when present."""
        if DocumentService._related_is_prefetched(
            document, "documentresubmissionrequest_set"
        ):
            open_reqs = [
                r
                for r in document.documentresubmissionrequest_set.all()
                if not r.resolved
            ]
            open_reqs.sort(key=lambda r: r.requested_at, reverse=True)
            return open_reqs[0] if open_reqs else None
        return (
            DocumentResubmissionRequest.objects.filter(
                document=document, resolved=False
            )
            .order_by("-requested_at")
            .first()
        )

    @staticmethod
    def build_application_document_checklist(application):
        """
        Compare program document requirements to uploads on this application.

        Status per type (latest upload for that type): missing, pending_review,
        invalid, resubmit_requested, approved, n_a (instructions_only).
        Includes deadline / overdue flags for UI and coordinator review.

        Results are cached on ``application._document_checklist_cache`` for the
        request so readiness / checklist / form-step fields do not rebuild.
        Uses prefetched requirements, documents, and resubmissions when present.
        """
        cached = getattr(application, "_document_checklist_cache", None)
        if cached is not None:
            return cached

        requirements = DocumentService._program_document_requirements(application.program)
        if not requirements:
            result = {
                "complete": True,
                "required_count": 0,
                "approved_count": 0,
                "items": [],
            }
            application._document_checklist_cache = result
            return result

        items = []
        approved_count = 0
        required_count = 0
        from exchange.lifecycle_requirements import (
            document_completeness_gate,
            document_is_due,
            effective_document_required_from,
        )

        current_status = (
            application.status.name if getattr(application, "status", None) else "draft"
        )
        gate_status = document_completeness_gate(current_status)
        uploads_by_type = DocumentService._uploads_by_type(application)

        for req in requirements:
            dt = req.document_type
            scheduled_required = bool(getattr(req, "is_required", True))
            required_from = effective_document_required_from(req)
            due_now = document_is_due(req, current_status)
            counts_toward_complete = document_is_due(req, gate_status)
            if counts_toward_complete:
                required_count += 1

            deadline = req.resolve_deadline()
            overdue = req.is_overdue()
            instructions = (
                getattr(req, "instructions_override", None) or ""
            ).strip() or (dt.instructions or "")
            entry = {
                "document_type_id": dt.id,
                "slug": dt.slug or "",
                "name": dt.name,
                "description": dt.description or "",
                "submission_mode": dt.submission_mode,
                "is_required": scheduled_required,
                "required_from_status": required_from,
                "due_now": due_now,
                "counts_toward_complete": counts_toward_complete,
                "status": "missing",
                "document_id": None,
                "resubmission_reason": None,
                "deadline": deadline.isoformat() if deadline else None,
                "is_overdue": overdue,
                "instructions": instructions,
                "faq": dt.faq or "",
                "has_template": bool(dt.template_file),
                "allows_multiple": dt.allows_multiple,
                "accepted_extensions": DocumentService.resolved_accepted_extensions_csv(
                    dt
                ),
                "max_file_size_mb": dt.max_file_size_mb,
                "upload_count": 0,
                "uploads": [],
            }

            if dt.submission_mode == DocumentType.SubmissionMode.INSTRUCTIONS_ONLY:
                entry["status"] = "n_a"
                if counts_toward_complete:
                    approved_count += 1
                items.append(entry)
                continue

            all_uploads = uploads_by_type.get(dt.id, [])
            current_uploads = DocumentService.filter_current_from_list(all_uploads)
            entry["upload_count"] = len(current_uploads)
            entry["uploads"] = [
                {
                    "document_id": str(doc.id),
                    "status": DocumentService._status_for_single_upload(doc),
                    "created_at": doc.created_at.isoformat() if doc.created_at else None,
                    "is_valid": bool(doc.is_valid),
                    "validated_at": (
                        doc.validated_at.isoformat() if doc.validated_at else None
                    ),
                }
                for doc in current_uploads
            ]

            status, primary, reason = DocumentService._aggregate_upload_status(
                current_uploads
            )
            entry["status"] = status
            if primary is not None:
                entry["document_id"] = str(primary.id)
            if reason:
                entry["resubmission_reason"] = reason
            if status == "approved" and counts_toward_complete:
                approved_count += 1
            items.append(entry)

        result = {
            "complete": approved_count == required_count,
            "required_count": required_count,
            "approved_count": approved_count,
            "items": items,
        }
        application._document_checklist_cache = result
        return result

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
        rows = list(
            DocumentType.objects.filter(pk__in=eff)
            .order_by("name")
            .values(
                "id",
                "name",
                "description",
                "instructions",
                "faq",
                "submission_mode",
                "accepted_extensions",
                "max_file_size_mb",
                "template_file",
            )
        )
        for row in rows:
            row["has_template"] = bool(row.pop("template_file"))
        return rows

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
            raise ValidationError(
                "Invalid required_document_type_ids on form step."
            ) from None
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
