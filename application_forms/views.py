"""
Application Forms Views

API views for form types and submissions.
"""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import render
from django.views.generic import TemplateView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from documents.services import DocumentService
from exchange.models import Program

from .models import FormStepTemplate, FormSubmission, FormType
from .serializers import (
    ApplyStepTemplateSerializer,
    FormStepTemplateListSerializer,
    FormStepTemplateSerializer,
    FormSubmissionListSerializer,
    FormSubmissionSerializer,
    FormTypeListSerializer,
    FormTypeSerializer,
)
from .step_template_service import apply_step_template_to_form_type


def is_admin(user):
    """Check if user is admin - either has admin role OR is superuser"""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.has_role('admin')


class AdminOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return is_admin(self.request.user)


class IsSeimAdmin(permissions.BasePermission):
    """Admin role or superuser (matches is_admin)."""

    def has_permission(self, request, view):
        return is_admin(request.user)


class FormTypeListView(LoginRequiredMixin, AdminOnlyMixin, TemplateView):
    """List view for form types"""
    template_name = 'application_forms/list.html'


class EnhancedFormBuilderView(LoginRequiredMixin, AdminOnlyMixin, TemplateView):
    """Enhanced form builder view with custom UI"""
    template_name = 'application_forms/builder.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_id = kwargs.get('pk')
        context['form_id'] = form_id
        # Pass form_id to template for JavaScript
        if form_id:
            context['form_id_js'] = form_id
        return context


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
        program_id = request.query_params.get("program")
        steps = form_type.get_multi_step_layout()
        if program_id:
            try:
                program = Program.objects.prefetch_related("required_document_types").get(
                    pk=program_id
                )
            except (Program.DoesNotExist, ValueError):
                program = None
            if program:
                steps = DocumentService.enrich_form_steps_for_program(form_type, program)
        return Response({
            'id': form_type.id,
            'name': form_type.name,
            'description': form_type.description,
            'schema': form_type.schema,
            'ui_schema': form_type.ui_schema,
            'required_fields': form_type.get_required_fields(),
            'multi_step': form_type.is_multi_step(),
            'steps': steps,
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

    @action(detail=True, methods=["post"], url_path="apply-step-template")
    def apply_step_template(self, request, pk=None):
        """Merge a FormStepTemplate into this form (schema, ui_schema, step_definitions)."""
        if not is_admin(request.user):
            return Response(status=403)
        form_type = self.get_object()
        ser = ApplyStepTemplateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        vd = ser.validated_data
        if vd.get("template_id") is not None:
            template = FormStepTemplate.objects.get(pk=vd["template_id"])
        else:
            template = FormStepTemplate.objects.get(slug=vd["slug"])
        raw_key = ser.validated_data.get("step_key") or ""
        step_key = raw_key.strip() or None
        try:
            apply_step_template_to_form_type(form_type, template, step_key=step_key)
        except DjangoValidationError as e:
            if hasattr(e, "message_dict") and e.message_dict:
                return Response(e.message_dict, status=400)
            return Response({"detail": e.messages}, status=400)
        out = FormTypeSerializer(form_type, context={"request": request})
        return Response(out.data)


class FormStepTemplateViewSet(viewsets.ModelViewSet):
    """
    Reusable step templates (list/retrieve for authenticated; writes admin-only).
    """

    queryset = FormStepTemplate.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "slug", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsSeimAdmin()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "list":
            return FormStepTemplateListSerializer
        return FormStepTemplateSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if is_admin(self.request.user):
            return qs
        return qs.filter(is_active=True)

    def get_object(self):
        obj = super().get_object()
        if not is_admin(self.request.user) and not obj.is_active:
            raise NotFound()
        return obj


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
