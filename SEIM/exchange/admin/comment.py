"""
Admin configuration for Comment and Review models.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from ..models.applications.comment import Comment
from ..models import Review


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for Comment model"""

    list_display = (
        "id",
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
    fieldsets = (
        (
            _("Comment Information"),
            {
                "fields": (
                    "exchange",
                    "author",
                    "comment_type",
                    "text",
                )
            },
        ),
        (
            _("Visibility and Status"),
            {
                "fields": (
                    "is_visible_to_student",
                    "is_viewed_by_student",
                    "viewed_at",
                    "is_edited",
                    "edited_at",
                )
            },
        ),
        (
            _("System Information"),
            {
                "fields": ("created_at",),
                "classes": ("collapse",)
            },
        ),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface for Review model"""

    list_display = (
        "id",
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
    fieldsets = (
        (
            _("Review Information"),
            {
                "fields": (
                    "exchange",
                    "reviewer",
                    "review_type",
                )
            },
        ),
        (
            _("Decision"),
            {
                "fields": (
                    "decision",
                    "comments",
                    "conditions",
                )
            },
        ),
        (
            _("Revision Information"),
            {
                "fields": (
                    "is_revised",
                    "revised_at",
                    "revision_reason",
                )
            },
        ),
        (
            _("System Information"),
            {
                "fields": ("reviewed_at",),
                "classes": ("collapse",)
            },
        ),
    )
