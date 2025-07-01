"""
Admin configuration for the exchange application.
"""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import (
    Comment,
    Course,
    Document,
    Grade,
    Review,
    BulkAction,
    BulkActionItem,
    BulkActionLog,
)
from .models.applications.exchange import Exchange
from .models.applications.timeline import Timeline, WorkflowLog
from .models.people.user_profile import UserProfile
from .models.people.student_profile import StudentProfile
from .models.people.staff_profile import StaffProfile
from .models.people.contact_profile import ContactProfile


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    """Admin interface for Exchange model"""

    list_display = (
        "id",
        "student",
        "host_university",
        "destination_country",
        "status",
        "submission_date",
        "decision_date",
        "has_all_documents",
    )
    list_filter = (
        "status",
        "destination_country",
        "submission_date",
        "decision_date",
    )
    search_fields = (
        "student__username",
        "student__email",
        "student__first_name",
        "student__last_name",
        "host_university",
        "destination_country",
    )
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at", "workflow_history")
    fieldsets = (
        (
            _("Student Information"),
            {
                "fields": (
                    "student",
                )
            },
        ),
        (
            _("Academic Information"),
            {
                "fields": (
                    "home_university",
                    "degree",
                    "major",
                    "program",
                    "academic_year",
                    "current_semester",
                )
            },
        ),
        (
            _("Exchange Details"),
            {
                "fields": (
                    "host_university",
                    "destination_country",
                )
            },
        ),
        (
            _("Application Details"),
            {
                "fields": (
                    "study_goals",
                    "referral_source",
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
            _("System Information"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )



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
        "exchange__student__first_name",
        "exchange__student__last_name",
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
    search_fields = ("exchange__student__first_name", "exchange__student__last_name", "comment")
    readonly_fields = ("timestamp",)
    date_hierarchy = "timestamp"


@admin.register(Timeline)
class TimelineAdmin(admin.ModelAdmin):
    """Admin interface for Timeline model (legacy)"""

    list_display = ("exchange", "event_type", "description", "actor", "timestamp")
    list_filter = ("event_type", "timestamp")
    search_fields = ("exchange__student__first_name", "exchange__student__last_name", "description")
    readonly_fields = ("timestamp",)
    date_hierarchy = "timestamp"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model (LEGACY - To be removed)"""

    list_display = ("user", "institution", "department", "student_id", "position")
    list_filter = ("institution", "department", "country")
    search_fields = ("user__username", "user__email", "institution", "student_id")
    fieldsets = (
        (_("User Information"), {"fields": ("user",)}),
        (_("Personal Information"), {"fields": ("date_of_birth", "gender", "phone")}),
        (_("Contact Information"), {"fields": ("address", "city", "country")}),
        (_("Academic Information"), {"fields": ("student_id", "institution", "department", "current_program")}),
        (_("Staff Information"), {"fields": ("position", "office_phone")}),
        (_("System Information"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """Admin interface for StudentProfile model"""

    list_display = ("user", "student_id", "university", "department", "current_semester", "is_active")
    list_filter = ("is_active", "current_semester", "university", "department")
    search_fields = ("user__username", "user__email", "student_id", "department")
    fieldsets = (
        (_("User Information"), {"fields": ("user",)}),
        (_("Personal Information"), {"fields": ("date_of_birth", "gender", "phone_number", "emergency_contact")}),
        (_("Address"), {"fields": ("address_line1", "address_line2", "city", "state_province", "postal_code", "country")}),
        (_("Academic Information"), {"fields": ("student_id", "university", "department", "major", "current_semester", "academic_level")}),
        (_("Status"), {"fields": ("is_active", "is_verified", "last_login")}),
        (_("System Information"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    readonly_fields = ("created_at", "updated_at", "last_login")


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    """Admin interface for StaffProfile model"""

    list_display = ("user", "staff_id", "university", "department", "position", "is_active")
    list_filter = ("is_active", "position", "university", "department")
    search_fields = ("user__username", "user__email", "staff_id", "department")
    fieldsets = (
        (_("User Information"), {"fields": ("user",)}),
        (_("Personal Information"), {"fields": ("date_of_birth", "gender", "phone_number", "emergency_contact")}),
        (_("Address"), {"fields": ("address_line1", "address_line2", "city", "state_province", "postal_code", "country")}),
        (_("Staff Information"), {"fields": ("staff_id", "university", "department", "position", "office_location", "office_phone")}),
        (_("Status"), {"fields": ("is_active", "is_verified", "last_login")}),
        (_("System Information"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    readonly_fields = ("created_at", "updated_at", "last_login")


@admin.register(ContactProfile)
class ContactProfileAdmin(admin.ModelAdmin):
    """Admin interface for ContactProfile model"""

    list_display = ("user", "university", "department", "position", "is_primary", "is_active")
    list_filter = ("is_active", "is_primary", "university")
    search_fields = ("user__username", "user__email", "department", "position")
    fieldsets = (
        (_("User Information"), {"fields": ("user",)}),
        (_("Personal Information"), {"fields": ("date_of_birth", "gender", "phone_number", "emergency_contact")}),
        (_("Address"), {"fields": ("address_line1", "address_line2", "city", "state_province", "postal_code", "country")}),
        (_("Contact Information"), {"fields": ("university", "department", "position", "office_phone", "mobile_phone", "is_primary")}),
        (_("Availability"), {"fields": ("availability_notes", "preferred_contact_method")}),
        (_("Status"), {"fields": ("is_active", "is_verified", "last_login")}),
        (_("System Information"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    readonly_fields = ("created_at", "updated_at", "last_login")


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
        "exchange__student__first_name",
        "exchange__student__last_name",
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
        "exchange__student__first_name",
        "exchange__student__last_name",
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
        "exchange__student__first_name",
        "exchange__student__last_name",
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
        "course__exchange__student__first_name",
        "course__exchange__student__last_name",
    )
    readonly_fields = ("date_processed",)


@admin.register(BulkAction)
class BulkActionAdmin(admin.ModelAdmin):
    """Admin interface for BulkAction model"""
    list_display = ("id", "name", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")


@admin.register(BulkActionItem)
class BulkActionItemAdmin(admin.ModelAdmin):
    """Admin interface for BulkActionItem model"""
    list_display = ("id", "bulk_action", "exchange", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("exchange__student__first_name", "exchange__student__last_name", "bulk_action__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(BulkActionLog)
class BulkActionLogAdmin(admin.ModelAdmin):
    """Admin interface for BulkActionLog model"""
    list_display = ("id", "bulk_action", "timestamp", "user", "action_type", "status")
    list_filter = ("action_type", "status", "timestamp")
    search_fields = ("bulk_action__name", "user__username", "comment")
    readonly_fields = ("timestamp",)
