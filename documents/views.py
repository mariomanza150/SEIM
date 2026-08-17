import mimetypes
import os

from django.db.models import Count, Prefetch, Q
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from core.cache import cache_api_response, invalidate_application_api_responses
from core.permissions import IsAdminOrReadOnly, IsCoordinatorOrAdmin, IsOwnerOrAdmin

from .filters import DocumentFilter, ExchangeAgreementDocumentFilter
from .mailmerge import (
    MERGE_FIELD_CATALOG,
    is_docx_filename,
    merge_docx,
    merge_values_for_application,
)
from .models import (
    Document,
    DocumentComment,
    DocumentResubmissionRequest,
    DocumentType,
    DocumentValidation,
    ExchangeAgreementDocument,
)
from .serializers import (
    DocumentCommentSerializer,
    DocumentResubmissionRequestSerializer,
    DocumentSerializer,
    DocumentTypeListSerializer,
    DocumentTypeSerializer,
    DocumentValidationSerializer,
    ExchangeAgreementDocumentSerializer,
)
from .services import DocumentService

# Create your views here.


class ExchangeAgreementDocumentViewSet(viewsets.ModelViewSet):
    """Staff repository files linked to exchange agreements (not application uploads)."""

    queryset = ExchangeAgreementDocument.objects.select_related(
        "agreement", "uploaded_by", "supersedes"
    ).all()
    serializer_class = ExchangeAgreementDocumentSerializer
    permission_classes = [IsCoordinatorOrAdmin]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ExchangeAgreementDocumentFilter
    search_fields = [
        "title",
        "notes",
        "agreement__title",
        "agreement__partner_institution_name",
    ]
    ordering_fields = ["created_at", "category"]


class DocumentTypeViewSet(viewsets.ModelViewSet):
    """Document type catalog: authenticated read; admin create/update/delete."""

    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["submission_mode", "allows_multiple"]
    search_fields = ["name", "slug", "description"]
    ordering_fields = ["name", "id"]
    ordering = ["name"]
    lookup_field = "pk"

    def get_queryset(self):
        qs = DocumentType.objects.all().annotate(
            requirement_count=Count("program_requirements")
        )
        if self.action == "retrieve":
            return qs.prefetch_related("program_requirements__program")
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return DocumentTypeListSerializer
        return DocumentTypeSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        if self.action == "list":
            ctx["include_program_requirements"] = False
        return ctx

    @action(detail=False, methods=["get"], url_path="merge-fields")
    def merge_fields(self, request):
        """Word MERGEFIELD names available for template prefilling."""
        return Response({"fields": MERGE_FIELD_CATALOG})

    @action(
        detail=True,
        methods=["post"],
        url_path="upload-template",
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload_template(self, request, pk=None):
        """Attach or replace the downloadable template file (admin)."""
        doc_type = self.get_object()
        upload = request.FILES.get("template_file") or request.FILES.get("file")
        if not upload:
            return Response(
                {"template_file": ["A template file is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        name = (upload.name or "").lower()
        if not (
            name.endswith(".docx")
            or name.endswith(".pdf")
            or name.endswith(".doc")
            or name.endswith(".odt")
        ):
            return Response(
                {
                    "template_file": [
                        "Template must be a Word (.docx), PDF, or similar document."
                    ]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        doc_type.template_file = upload
        doc_type.save(update_fields=["template_file"])
        serializer = DocumentTypeSerializer(doc_type, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["delete"], url_path="template")
    def delete_template(self, request, pk=None):
        """Remove the attached template file (admin)."""
        doc_type = self.get_object()
        if doc_type.template_file:
            doc_type.template_file.delete(save=True)
        serializer = DocumentTypeSerializer(doc_type, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="download-template")
    def download_template(self, request, pk=None):
        """Download template; .docx files are prefilled when ?application= is set."""
        doc_type = self.get_object()
        if not doc_type.template_file:
            return Response(
                {"detail": "No template file available for this document type."},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            handle = doc_type.template_file.open("rb")
            raw = handle.read()
            handle.close()
        except FileNotFoundError:
            return Response(
                {"detail": "Template file missing on server."},
                status=status.HTTP_404_NOT_FOUND,
            )

        filename = os.path.basename(doc_type.template_file.name)
        application_id = request.query_params.get("application")
        if application_id and is_docx_filename(filename):
            from exchange.models import Application

            application = get_object_or_404(
                Application.objects.select_related(
                    "student",
                    "student__profile",
                    "student__profile__school",
                    "student__profile__unidad",
                    "student__profile__academic_level",
                    "student__profile__home_academic_program",
                    "student__profile__bank_institution",
                    "program",
                    "host_institution",
                    "host_school",
                    "host_academic_program",
                ),
                pk=application_id,
            )
            user = request.user
            is_staff = getattr(user, "has_role", None) and (
                user.has_role("coordinator") or user.has_role("admin")
            )
            if not is_staff and application.student_id != user.id:
                raise PermissionDenied(
                    "You cannot download a prefilled template for this application."
                )
            values = merge_values_for_application(application)
            raw = merge_docx(raw, values)
            stem, ext = os.path.splitext(filename)
            filename = f"{stem}_{application.student.username}{ext}"

        content_type, _ = mimetypes.guess_type(filename)
        response = HttpResponse(
            raw, content_type=content_type or "application/octet-stream"
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for documents with role-based permissions and filtering."""

    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = DocumentFilter
    ordering_fields = ["created_at", "validated_at"]

    def get_queryset(self):
        """
        Filter documents based on user permissions.

        - Students: Only their own documents
        - Coordinators/Admins: All documents
        """
        user = self.request.user

        val_qs = DocumentValidation.objects.select_related("validator").order_by(
            "validated_at", "created_at"
        )
        resub_qs = DocumentResubmissionRequest.objects.select_related(
            "requested_by"
        ).order_by("-requested_at")
        comment_qs = DocumentComment.objects.select_related("author").order_by(
            "created_at"
        )

        # Coordinators and admins can see all documents
        if hasattr(user, "has_role") and (
            user.has_role("coordinator") or user.has_role("admin")
        ):
            return Document.objects.select_related(
                "application",
                "application__student",
                "application__program",
                "application__status",
                "type",
                "uploaded_by",
            ).prefetch_related(
                "uploaded_by__roles",
                Prefetch("documentvalidation_set", queryset=val_qs),
                Prefetch("documentresubmissionrequest_set", queryset=resub_qs),
                Prefetch("documentcomment_set", queryset=comment_qs),
            )

        # Students can only see their own documents
        return (
            Document.objects.filter(Q(uploaded_by=user) | Q(application__student=user))
            .select_related(
                "application",
                "application__student",
                "application__program",
                "application__status",
                "type",
                "uploaded_by",
            )
            .prefetch_related(
                "uploaded_by__roles",
                Prefetch("documentvalidation_set", queryset=val_qs),
                Prefetch("documentresubmissionrequest_set", queryset=resub_qs),
                Prefetch("documentcomment_set", queryset=comment_qs),
            )
        )

    def perform_create(self, serializer):
        """Set uploaded_by to current user on creation."""
        serializer.save(uploaded_by=self.request.user)
        invalidate_application_api_responses(serializer.instance.application)

    def perform_update(self, serializer):
        serializer.save()
        invalidate_application_api_responses(serializer.instance.application)

    def perform_destroy(self, instance):
        application = instance.application
        instance.delete()
        invalidate_application_api_responses(application)

    @cache_api_response(timeout=300)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=300)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=["get"], url_path="preview")
    def preview(self, request, pk=None):
        """Stream the file for inline preview (JWT auth; same access as retrieve)."""
        document = self.get_object()
        file_field = document.file
        if not file_field:
            return Response(
                {"detail": "No file attached."},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            file_handle = file_field.open("rb")
        except FileNotFoundError:
            return Response(
                {"detail": "File missing on server."},
                status=status.HTTP_404_NOT_FOUND,
            )
        content_type, _ = mimetypes.guess_type(file_field.name)
        filename = os.path.basename(file_field.name)
        try:
            head = file_handle.read(5)
            file_handle.seek(0)
        except Exception:
            head = b""
        name_l = (file_field.name or filename or "").lower()
        if name_l.endswith(".pdf") or head.startswith(b"%PDF"):
            content_type = "application/pdf"
        elif not content_type:
            content_type = "application/octet-stream"
        response = FileResponse(file_handle, content_type=content_type)
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response

    @action(detail=True, methods=["post"])
    def validate_document(self, request, pk=None):
        """
        Mark document as valid or invalid (coordinator/admin only).
        POST with body: { "result": "valid"|"invalid", "details": "optional note" }
        """
        document = self.get_object()
        user = request.user
        if not (
            getattr(user, "has_role", None)
            and (user.has_role("coordinator") or user.has_role("admin"))
        ):
            return Response(
                {"detail": "Only coordinators or admins can validate documents."},
                status=status.HTTP_403_FORBIDDEN,
            )
        result_val = (request.data.get("result") or "").lower()
        if result_val not in ("valid", "invalid"):
            return Response(
                {"result": ["Must be 'valid' or 'invalid'."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        details = request.data.get("details") or ""
        try:
            DocumentService.validate_document(document, user, result_val, details)
            document.refresh_from_db()
            invalidate_application_api_responses(document.application)
            serializer = self.get_serializer(document)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class DocumentValidationViewSet(viewsets.ModelViewSet):
    """ViewSet for document validations with role-based access."""

    queryset = DocumentValidation.objects.all()
    serializer_class = DocumentValidationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter validations based on user permissions."""
        user = self.request.user

        if hasattr(user, "has_role") and (
            user.has_role("coordinator") or user.has_role("admin")
        ):
            return DocumentValidation.objects.select_related(
                "document", "document__application", "document__type", "validator"
            )

        # Students can only see validations for their documents
        return DocumentValidation.objects.filter(
            Q(document__uploaded_by=user) | Q(document__application__student=user)
        ).select_related(
            "document", "document__application", "document__type", "validator"
        )

    @cache_api_response(timeout=300)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=300)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class DocumentResubmissionRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for document resubmission requests with role-based access."""

    queryset = DocumentResubmissionRequest.objects.all()
    serializer_class = DocumentResubmissionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter resubmission requests based on user permissions."""
        user = self.request.user

        if hasattr(user, "has_role") and (
            user.has_role("coordinator") or user.has_role("admin")
        ):
            return DocumentResubmissionRequest.objects.select_related(
                "document", "document__application", "document__type", "requested_by"
            )

        # Students can only see requests for their documents
        return DocumentResubmissionRequest.objects.filter(
            Q(document__uploaded_by=user) | Q(document__application__student=user)
        ).select_related(
            "document", "document__application", "document__type", "requested_by"
        )

    def perform_create(self, serializer):
        serializer.save()
        document = serializer.instance.document
        invalidate_application_api_responses(document.application)

    def perform_update(self, serializer):
        serializer.save()
        document = serializer.instance.document
        invalidate_application_api_responses(document.application)

    @cache_api_response(timeout=300)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=300)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class DocumentCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for document comments with role-based access."""

    queryset = DocumentComment.objects.all()
    serializer_class = DocumentCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter comments based on user permissions."""
        user = self.request.user

        if hasattr(user, "has_role") and (
            user.has_role("coordinator") or user.has_role("admin")
        ):
            return DocumentComment.objects.select_related(
                "document", "document__application", "author"
            )

        # Students can only see public comments on their documents
        return DocumentComment.objects.filter(
            Q(author=user) | Q(document__application__student=user, is_private=False)
        ).select_related("document", "document__application", "author")

    def perform_create(self, serializer):
        document = serializer.validated_data["document"]
        if not DocumentService.user_can_access_document(self.request.user, document):
            raise PermissionDenied("You cannot comment on this document.")
        serializer.save(author=self.request.user)
        invalidate_application_api_responses(document.application)

    @cache_api_response(timeout=300)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=300)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
