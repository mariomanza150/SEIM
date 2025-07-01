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

    def has_view_permission(self, request, obj=None):
        """Allow staff, Exchange Managers, or owner to view."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if obj and hasattr(obj, "author"):
            return obj.author == request.user
        return False

    def has_change_permission(self, request, obj=None):
        """Allow staff, Exchange Managers, or owner to edit."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if obj and hasattr(obj, "author"):
            return obj.author == request.user
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow staff, Exchange Managers, or owner to delete."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if obj and hasattr(obj, "author"):
            return obj.author == request.user
        return False

    def has_add_permission(self, request):
        """Allow staff, Exchange Managers, or students to add."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name="Exchange Managers").exists():
            return True
        if request.user.groups.filter(name="Students").exists():
            return True
        return False

    def get_queryset(self, request):
        """Staff and Exchange Managers see all; students see only their own."""
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.is_staff:
            return qs
        if request.user.groups.filter(name="Exchange Managers").exists():
            return qs
        return qs.filter(author=request.user)


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

    def has_view_permission(self, request, obj=None):
        """Allow staff, Reviewers, Exchange Managers, or reviewer to view."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name__in=["Reviewers", "Exchange Managers"]).exists():
            return True
        if obj and hasattr(obj, "reviewer"):
            return obj.reviewer == request.user
        return False

    def has_change_permission(self, request, obj=None):
        """Allow staff, Reviewers, Exchange Managers, or reviewer to edit."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name__in=["Reviewers", "Exchange Managers"]).exists():
            return True
        if obj and hasattr(obj, "reviewer"):
            return obj.reviewer == request.user
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow staff, Reviewers, Exchange Managers, or reviewer to delete."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name__in=["Reviewers", "Exchange Managers"]).exists():
            return True
        if obj and hasattr(obj, "reviewer"):
            return obj.reviewer == request.user
        return False

    def has_add_permission(self, request):
        """Allow staff, Reviewers, Exchange Managers to add."""
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.user.groups.filter(name__in=["Reviewers", "Exchange Managers"]).exists():
            return True
        return False

    def get_queryset(self, request):
        """Staff, Reviewers, Exchange Managers see all; reviewers see only their own."""
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.is_staff:
            return qs
        if request.user.groups.filter(name__in=["Reviewers", "Exchange Managers"]).exists():
            return qs
        return qs.filter(reviewer=request.user)
