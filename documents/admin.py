from django.contrib import admin

from .models import (
    Document,
    DocumentResubmissionRequest,
    DocumentType,
    DocumentValidation,
    ExchangeAgreementDocument,
    FileTypeFamily,
)


class DocumentValidationInline(admin.TabularInline):
    model = DocumentValidation
    extra = 0
    fields = ("validator", "result", "details", "validated_at")
    readonly_fields = ("validated_at",)


@admin.register(ExchangeAgreementDocument)
class ExchangeAgreementDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "agreement",
        "category",
        "uploaded_by",
        "created_at",
        "supersedes",
    )
    list_filter = ("category", "agreement")
    search_fields = (
        "title",
        "notes",
        "agreement__title",
        "agreement__partner_institution_name",
    )
    raw_id_fields = ("agreement", "supersedes", "uploaded_by")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("agreement", "category", "title", "file", "supersedes")}),
        ("Notes", {"fields": ("notes",)}),
        ("Audit", {"fields": ("uploaded_by", "created_at", "updated_at")}),
    )

    def save_model(self, request, obj, form, change):
        if not change and not obj.uploaded_by_id:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(FileTypeFamily)
class FileTypeFamilyAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "extensions", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "aliases", "extensions")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order", "name")


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "submission_mode",
        "allows_multiple",
        "max_file_size_mb",
    )
    list_filter = ("submission_mode", "allows_multiple", "file_type_families")
    search_fields = ("name", "slug", "description")
    readonly_fields = ("id",)
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("file_type_families",)
    fieldsets = (
        (None, {"fields": ("name", "slug", "description", "submission_mode")}),
        (
            "Student guidance",
            {"fields": ("instructions", "faq", "template_file")},
        ),
        (
            "Upload constraints",
            {
                "fields": (
                    "file_type_families",
                    "accepted_extensions",
                    "max_file_size_mb",
                    "allows_multiple",
                )
            },
        ),
        (
            "Version history visibility",
            {
                "fields": (
                    "version_history_visibility",
                    "version_history_student",
                    "version_history_coordinator",
                    "version_history_admin",
                )
            },
        ),
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "application",
        "type",
        "uploaded_by",
        "is_valid",
        "validated_at",
        "supersedes",
    )
    search_fields = ("application__id", "type__name", "uploaded_by__email")
    list_filter = ("is_valid", "type")
    list_editable = ("is_valid",)
    raw_id_fields = ("application", "type", "uploaded_by", "supersedes")
    readonly_fields = ("created_at", "updated_at", "validated_at")
    fieldsets = (
        (None, {"fields": ("application", "type", "file", "uploaded_by", "is_valid", "supersedes")}),
        ("Validation", {"fields": ("validated_at",)}),
        ("Audit", {"fields": ("created_at", "updated_at")}),
    )
    inlines = [DocumentValidationInline]


@admin.register(DocumentValidation)
class DocumentValidationAdmin(admin.ModelAdmin):
    list_display = ("document", "validator", "result", "validated_at")
    search_fields = ("document__id", "validator__email", "result")
    readonly_fields = ("validated_at", "created_at", "updated_at")


@admin.register(DocumentResubmissionRequest)
class DocumentResubmissionRequestAdmin(admin.ModelAdmin):
    list_display = ("document", "requested_by", "resolved", "requested_at")
    search_fields = ("document__id", "requested_by__email", "reason")
    list_filter = ("resolved",)
    readonly_fields = ("requested_at", "created_at", "updated_at")
