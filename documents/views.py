from django.db.models import Q
from rest_framework import permissions, viewsets

from core.cache import cache_api_response
from core.permissions import IsOwnerOrAdmin

from .models import (
    Document,
    DocumentComment,
    DocumentResubmissionRequest,
    DocumentType,
    DocumentValidation,
)
from .serializers import (
    DocumentCommentSerializer,
    DocumentResubmissionRequestSerializer,
    DocumentSerializer,
    DocumentTypeSerializer,
    DocumentValidationSerializer,
)

# Create your views here.


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

    def get_queryset(self):
        """
        Filter documents based on user permissions.

        - Students: Only their own documents
        - Coordinators/Admins: All documents
        """
        user = self.request.user

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
                'documentvalidation_set',
                'documentvalidation_set__validator',
                'documentresubmissionrequest_set',
                'documentresubmissionrequest_set__requested_by',
                'documentcomment_set',
                'documentcomment_set__author'
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
            'documentvalidation_set',
            'documentvalidation_set__validator',
            'documentresubmissionrequest_set',
            'documentresubmissionrequest_set__requested_by',
            'documentcomment_set',
            'documentcomment_set__author'
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

    def perform_create(self, serializer):
        """Set requested_by to current user on creation."""
        serializer.save(requested_by=self.request.user)

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
        """Set author to current user on creation."""
        serializer.save(author=self.request.user)

    @cache_api_response(timeout=300)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=300)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
