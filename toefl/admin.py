from django.contrib import admin

from toefl.models import PracticeAttempt


@admin.register(PracticeAttempt)
class PracticeAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "external_session_id",
        "user",
        "exam_code",
        "percent",
        "earned",
        "total",
        "completed_at",
    )
    list_filter = ("exam_code",)
    search_fields = ("external_session_id", "client_ref", "user__email", "user__username")
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "raw_payload",
        "categories",
        "weakest",
        "items",
    )
    ordering = ("-completed_at",)
