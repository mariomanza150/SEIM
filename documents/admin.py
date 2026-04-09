from django.contrib import admin

from .models import (
    Document,
    DocumentResubmissionRequest,
    DocumentType,
    DocumentValidation,
    ExchangeAgreementDocument,
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
    search_fields = ("title", "notes", "agreement__title", "agreement__partner_institution_name")
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


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)
    readonly_fields = ("id",)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("application", "type", "uploaded_by", "is_valid", "validated_at")
    search_fields = ("application__id", "type__name", "uploaded_by__email")
    list_filter = ("is_valid", "type")
    list_editable = ("is_valid",)
    readonly_fields = ("created_at", "updated_at", "validated_at")
    fieldsets = (
        (None, {"fields": ("application", "type", "file", "uploaded_by", "is_valid")}),
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
