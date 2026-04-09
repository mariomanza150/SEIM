import mimetypes
import os

from django.db.models import Prefetch, Q
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from core.cache import cache_api_response
from core.permissions import IsCoordinatorOrAdmin, IsOwnerOrAdmin

from .filters import DocumentFilter, ExchangeAgreementDocumentFilter
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
    """ViewSet for document types - authenticated users can view, only admins can modify."""

    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

    @cache_api_response(timeout=600)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=600)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


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
        if hasattr(user, 'has_role') and (user.has_role('coordinator') or user.has_role('admin')):
            return Document.objects.select_related(
                'application',
                'application__student',
                'application__program',
                'application__status',
                'type',
                'uploaded_by'
            ).prefetch_related(
                'uploaded_by__roles',
                Prefetch("documentvalidation_set", queryset=val_qs),
                Prefetch("documentresubmissionrequest_set", queryset=resub_qs),
                Prefetch("documentcomment_set", queryset=comment_qs),
            )

        # Students can only see their own documents
        return Document.objects.filter(
            Q(uploaded_by=user) | Q(application__student=user)
        ).select_related(
            'application',
            'application__student',
            'application__program',
            'application__status',
            'type',
            'uploaded_by'
        ).prefetch_related(
            'uploaded_by__roles',
            Prefetch("documentvalidation_set", queryset=val_qs),
            Prefetch("documentresubmissionrequest_set", queryset=resub_qs),
            Prefetch("documentcomment_set", queryset=comment_qs),
        )

    def perform_create(self, serializer):
        """Set uploaded_by to current user on creation."""
        serializer.save(uploaded_by=self.request.user)

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
        if not content_type:
            content_type = "application/octet-stream"
        filename = os.path.basename(file_field.name)
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
        if not (getattr(user, "has_role", None) and (user.has_role("coordinator") or user.has_role("admin"))):
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

        if hasattr(user, 'has_role') and (user.has_role('coordinator') or user.has_role('admin')):
            return DocumentValidation.objects.select_related(
                'document',
                'document__application',
                'document__type',
                'validator'
            )

        # Students can only see validations for their documents
        return DocumentValidation.objects.filter(
            Q(document__uploaded_by=user) | Q(document__application__student=user)
        ).select_related(
            'document',
            'document__application',
            'document__type',
            'validator'
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

        if hasattr(user, 'has_role') and (user.has_role('coordinator') or user.has_role('admin')):
            return DocumentResubmissionRequest.objects.select_related(
                'document',
                'document__application',
                'document__type',
                'requested_by'
            )

        # Students can only see requests for their documents
        return DocumentResubmissionRequest.objects.filter(
            Q(document__uploaded_by=user) | Q(document__application__student=user)
        ).select_related(
            'document',
            'document__application',
            'document__type',
            'requested_by'
        )

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

        if hasattr(user, 'has_role') and (user.has_role('coordinator') or user.has_role('admin')):
            return DocumentComment.objects.select_related(
                'document',
                'document__application',
                'author'
            )

        # Students can only see public comments on their documents
        return DocumentComment.objects.filter(
            Q(author=user) |
            Q(document__application__student=user, is_private=False)
        ).select_related(
            'document',
            'document__application',
            'author'
        )

    def perform_create(self, serializer):
        document = serializer.validated_data["document"]
        if not DocumentService.user_can_access_document(self.request.user, document):
            raise PermissionDenied("You cannot comment on this document.")
        serializer.save(author=self.request.user)

    @cache_api_response(timeout=300)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=300)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
