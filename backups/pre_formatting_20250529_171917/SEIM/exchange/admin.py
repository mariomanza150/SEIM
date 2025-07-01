"""
Admin configuration for the exchange application.
"""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Comment, Course, Document, Exchange, Grade, Review
from .models.timeline import Timeline, WorkflowLog
from .models.user_profile import UserProfile


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    """Admin interface for Exchange model"""

    list_display = (
        "id",
        "student_name",
        "destination_university",
        "destination_country",
        "status",
        "submission_date",
        "decision_date",
        "has_all_documents",
    )
    list_filter = ("status", "destination_country", "submission_date", "decision_date")
    search_fields = (
        "first_name",
        "last_name",
        "email",
        "destination_university",
        "student__username",
        "student__email",
    )
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at", "workflow_history")
    fieldsets = (
        (
            _("Personal Information"),
            {
                "fields": (
                    "student",
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                    "date_of_birth",
                    "passport_number",
                    "student_number",
                )
            },
        ),
        (
            _("Academic Information"),
            {
                "fields": (
                    "current_university",
                    "current_program",
                    "current_year",
                    "gpa",
                )
            },
        ),
        (
            _("Exchange Details"),
            {
                "fields": (
                    "destination_university",
                    "destination_country",
                    "exchange_program",
                    "start_date",
                    "end_date",
                )
            },
        ),
        (
            _("Status and Workflow"),
            {
                "fields": (
                    "status",
                    "submission_date",
                    "review_date",
                    "decision_date",
                    "reviewed_by",
                    "notes",
                    "workflow_history",
                )
            },
        ),
        (
            _("Additional Information"),
            {
                "fields": (
                    "motivation_letter",
                    "language_proficiency",
                    "special_requirements",
                    "emergency_contact",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("System Information"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def student_name(self, obj):
        """Display student full name"""
        return f"{obj.first_name} {obj.last_name}"

    student_name.short_description = _("Student Name")

    def has_all_documents(self, obj):
        """Display if exchange has all required documents"""
        has_docs = obj.has_required_documents()
        icon = "✅" if has_docs else "❌"
        return format_html(
            '{} <a href="{}">View Documents</a>',
            icon,
            reverse("admin:exchange_document_changelist") + f"?exchange__id={obj.id}",
        )

    has_all_documents.short_description = _("Required Documents")

    def workflow_history(self, obj):
        """Display workflow history in admin"""
        logs = obj.workflow_logs.all().order_by("-timestamp")
        if not logs:
            return _("No workflow history")

        html = "<table><tr><th>Date</th><th>From</th><th>To</th><th>User</th><th>Comment</th></tr>"
        for log in logs:
            html += f"<tr><td>{log.timestamp}</td><td>{log.from_status}</td><td>{log.to_status}</td>"
            html += f'<td>{log.user.username if log.user else "System"}</td><td>{log.comment}</td></tr>'
        html += "</table>"

        return format_html(html)

    workflow_history.short_description = _("Workflow History")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin interface for Document model"""

    list_display = (
        "id",
        "title",
        "category",
        "exchange_link",
        "status",
        "verified",
        "uploaded_at",
        "file_size_display",
    )
    list_filter = ("category", "status", "verified", "uploaded_at")
    search_fields = (
        "title",
        "description",
        "exchange__first_name",
        "exchange__last_name",
    )
    readonly_fields = (
        "file_size",
        "file_hash",
        "version",
        "uploaded_at",
        "updated_at",
        "file_preview",
    )

    def exchange_link(self, obj):
        """Display link to related exchange"""
        url = reverse("admin:exchange_exchange_change", args=[obj.exchange.id])
        return format_html('<a href="{}">{}</a>', url, str(obj.exchange))

    exchange_link.short_description = _("Exchange")

    def file_size_display(self, obj):
        """Display human-readable file size"""
        return obj.get_human_readable_size()

    file_size_display.short_description = _("File Size")

    def file_preview(self, obj):
        """Display file preview or download link"""
        if obj.get_file_extension() in [".pdf", ".jpg", ".jpeg", ".png"]:
            return format_html(
                '<a href="{}" target="_blank">View File</a>',
                reverse("exchange:document-detail", args=[obj.exchange.id, obj.id]),
            )
        return format_html('<a href="{}" download>Download File</a>', obj.file.url)

    file_preview.short_description = _("File Preview")


@admin.register(WorkflowLog)
class WorkflowLogAdmin(admin.ModelAdmin):
    """Admin interface for WorkflowLog model"""

    list_display = ("exchange", "from_status", "to_status", "user", "timestamp")
    list_filter = ("from_status", "to_status", "timestamp")
    search_fields = ("exchange__first_name", "exchange__last_name", "comment")
    readonly_fields = ("timestamp",)
    date_hierarchy = "timestamp"


@admin.register(Timeline)
class TimelineAdmin(admin.ModelAdmin):
    """Admin interface for Timeline model (legacy)"""

    list_display = ("exchange", "event_type", "description", "actor", "timestamp")
    list_filter = ("event_type", "timestamp")
    search_fields = ("exchange__first_name", "exchange__last_name", "description")
    readonly_fields = ("timestamp",)
    date_hierarchy = "timestamp"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model"""

    list_display = ("user", "institution", "department", "student_id", "position")
    list_filter = ("institution", "department", "country")
    search_fields = ("user__username", "user__email", "institution", "student_id")
    fieldsets = (
        (_("User Information"), {
            "fields": ("user",)
        }),
        (_("Personal Information"), {
            "fields": ("date_of_birth", "gender", "phone")
        }),
        (_("Contact Information"), {
            "fields": ("address", "city", "country")
        }),
        (_("Academic Information"), {
            "fields": ("student_id", "institution", "department", "current_program")
        }),
        (_("Staff Information"), {
            "fields": ("position", "office_phone")
        }),
        (_("System Information"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for Comment model"""

    list_display = (
        "exchange",
        "author",
        "comment_type",
        "created_at",
        "is_edited",
        "is_viewed_by_student",
    )
    list_filter = ("comment_type", "is_edited", "is_viewed_by_student", "created_at")
    search_fields = (
        "text",
        "author__username",
        "exchange__first_name",
        "exchange__last_name",
    )
    readonly_fields = ("created_at", "edited_at", "viewed_at")
    date_hierarchy = "created_at"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface for Review model"""

    list_display = (
        "exchange",
        "reviewer",
        "review_type",
        "decision",
        "reviewed_at",
        "is_revised",
    )
    list_filter = ("review_type", "decision", "is_revised", "reviewed_at")
    search_fields = (
        "comments",
        "conditions",
        "reviewer__username",
        "exchange__first_name",
        "exchange__last_name",
    )
    readonly_fields = ("reviewed_at", "revised_at")
    date_hierarchy = "reviewed_at"


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin interface for Course model"""

    list_display = (
        "course_code",
        "course_name",
        "exchange",
        "host_university",
        "credits",
        "status",
    )
    list_filter = ("status", "host_university")
    search_fields = (
        "course_code",
        "course_name",
        "host_university",
        "exchange__first_name",
        "exchange__last_name",
    )
    readonly_fields = ("approved_at",)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    """Admin interface for Grade model"""

    list_display = (
        "course",
        "host_grade",
        "converted_grade",
        "status",
        "date_received",
        "date_processed",
    )
    list_filter = ("status", "date_received", "date_processed")
    search_fields = (
        "course__course_code",
        "course__course_name",
        "course__exchange__first_name",
        "course__exchange__last_name",
    )
    readonly_fields = ("date_processed",)
