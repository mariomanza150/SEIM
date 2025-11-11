"""
Application Forms Admin Configuration

Provides Django admin interface for managing custom form types and submissions.
"""

from django import forms
from django.contrib import admin

from .models import FormSubmission, FormType


class FormTypeAdminForm(forms.ModelForm):
    """Custom form for FormType admin with JSON schema validation"""

    schema = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 10,
            'cols': 80,
            'placeholder': '''Example schema:
{
    "type": "object",
    "properties": {
        "name": {"type": "string", "title": "Full Name"},
        "email": {"type": "string", "format": "email", "title": "Email"},
        "age": {"type": "number", "title": "Age", "minimum": 0}
    },
    "required": ["name", "email"]
}'''
        }),
        required=False,
        help_text="JSON Schema defining the form structure"
    )

    ui_schema = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 8,
            'cols': 80,
            'placeholder': '''Example UI schema:
{
    "name": {"ui:placeholder": "Enter your full name"},
    "email": {"ui:widget": "email"},
    "age": {"ui:widget": "updown", "ui:title": "Your Age"}
}'''
        }),
        required=False,
        help_text="Optional UI schema for form rendering"
    )

    class Meta:
        model = FormType
        fields = '__all__'


class FormSubmissionInline(admin.TabularInline):
    """Inline display of form submissions"""
    model = FormSubmission
    readonly_fields = ('submitted_at', 'submitted_by', 'responses')
    fields = ('submitted_at', 'submitted_by', 'program', 'application')
    extra = 0
    max_num = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(FormType)
class FormTypeAdmin(admin.ModelAdmin):
    """Admin interface for Form Types"""
    form = FormTypeAdminForm
    list_display = ['name', 'form_type', 'is_active', 'created_by', 'created_at', 'get_field_count']
    list_filter = ['form_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'get_field_count', 'get_required_fields']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'form_type', 'description', 'is_active')
        }),
        ('Form Structure', {
            'fields': ('schema', 'ui_schema', 'get_field_count', 'get_required_fields'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [FormSubmissionInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Non-superusers can only see forms they created
            qs = qs.filter(created_by=request.user)
        return qs

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_field_count(self, obj):
        """Display the number of fields in the form"""
        return obj.get_field_count()
    get_field_count.short_description = 'Field Count'

    def get_required_fields(self, obj):
        """Display the required fields"""
        fields = obj.get_required_fields()
        return ', '.join(fields) if fields else 'None'
    get_required_fields.short_description = 'Required Fields'


@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    """Admin interface for Form Submissions"""
    list_display = ['form_type', 'submitted_by', 'submitted_at', 'program', 'application', 'get_response_count']
    list_filter = ['form_type', 'submitted_at', 'program']
    search_fields = ['form_type__name', 'submitted_by__username', 'submitted_by__email']
    readonly_fields = ['submitted_at', 'updated_at', 'responses', 'get_response_count']

    # Make submission data readable
    fieldsets = (
        ('Submission Info', {
            'fields': ('form_type', 'submitted_by', 'program', 'application')
        }),
        ('Data', {
            'fields': ('responses', 'get_response_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('submitted_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Non-superusers can only see submissions to forms they created
            qs = qs.filter(form_type__created_by=request.user)
        return qs

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_response_count(self, obj):
        """Display the number of responses"""
        return obj.get_response_count()
    get_response_count.short_description = 'Response Count'

