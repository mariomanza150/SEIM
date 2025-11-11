"""
Application Forms Views

API views for form types and submissions.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import FormSubmission, FormType
from .serializers import (
    FormSubmissionListSerializer,
    FormSubmissionSerializer,
    FormTypeListSerializer,
    FormTypeSerializer,
)


class FormTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Form Types.

    Provides CRUD operations for custom form types.
    Admin users can create and manage forms.
    Other users can view active forms.
    """
    queryset = FormType.objects.all()
    serializer_class = FormTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['form_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Use lightweight serializer for list views"""
        if self.action == 'list':
            return FormTypeListSerializer
        return FormTypeSerializer

    def get_queryset(self):
        """Filter forms based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user

        # Admin users see all forms
        if user.has_role('admin'):
            return queryset

        # Non-admin users see only active forms
        return queryset.filter(is_active=True)

    def perform_create(self, serializer):
        """Auto-assign created_by to current user"""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def form_schema(self, request, pk=None):
        """
        Get just the form schema for rendering.

        Endpoint: /api/application-forms/form-types/{id}/form_schema/
        """
        form_type = self.get_object()
        return Response({
            'id': form_type.id,
            'name': form_type.name,
            'description': form_type.description,
            'schema': form_type.schema,
            'ui_schema': form_type.ui_schema,
            'required_fields': form_type.get_required_fields()
        })

    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        """
        Get all submissions for this form type.

        Endpoint: /api/application-forms/form-types/{id}/submissions/
        """
        form_type = self.get_object()
        submissions = form_type.submissions.all()

        # Filter by user if not admin
        if not request.user.has_role('admin'):
            submissions = submissions.filter(submitted_by=request.user)

        serializer = FormSubmissionListSerializer(submissions, many=True)
        return Response(serializer.data)


class FormSubmissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Form Submissions.

    Provides CRUD operations for form submissions.
    Users can create submissions and view their own.
    Admins can view all submissions.
    """
    queryset = FormSubmission.objects.all()
    serializer_class = FormSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['form_type', 'program', 'application']
    search_fields = ['form_type__name', 'submitted_by__username']
    ordering_fields = ['submitted_at']
    ordering = ['-submitted_at']

    def get_serializer_class(self):
        """Use lightweight serializer for list views"""
        if self.action == 'list':
            return FormSubmissionListSerializer
        return FormSubmissionSerializer

    def get_queryset(self):
        """Filter submissions based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user

        # Admin users see all submissions
        if user.has_role('admin'):
            return queryset

        # Coordinator users see all submissions (no program-coordinator association in model)
        if user.has_role('coordinator'):
            return queryset.all()

        # Regular users see only their own submissions
        return queryset.filter(submitted_by=user)

    def perform_create(self, serializer):
        """Auto-assign submitted_by to current user"""
        serializer.save(submitted_by=self.request.user)

