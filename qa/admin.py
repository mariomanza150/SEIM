import json

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Issue, IssueAttachment, IssueComment


class IssueAttachmentInline(admin.TabularInline):
    model = IssueAttachment
    extra = 0
    fields = ("preview", "original_name", "kind", "content_type", "size", "created_at")
    readonly_fields = fields
    can_delete = True

    @admin.display(description=_("Preview"))
    def preview(self, obj):
        if not obj.pk:
            return "-"
        url = f"/api/qa/issues/{obj.issue_id}/attachments/{obj.pk}/download/"
        if (obj.content_type or "").startswith("image/"):
            return format_html(
                '<a href="{}" target="_blank" rel="noopener"><img src="{}" '
                'style="max-height:120px;max-width:200px;border:1px solid #ccc"></a>',
                url,
                url,
            )
        return format_html(
            '<a href="{}" target="_blank" rel="noopener">{}</a>', url, _("Open")
        )

    def has_add_permission(self, request, obj=None):
        return False


class IssueCommentInline(admin.StackedInline):
    model = IssueComment
    extra = 0
    fields = ("author", "body", "is_internal", "is_system", "created_at")
    readonly_fields = ("author", "is_system", "created_at")


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = (
        "reference_display",
        "title",
        "severity",
        "status",
        "kind",
        "reporter",
        "reporter_role",
        "route_name",
        "build_commit",
        "created_at",
    )
    list_filter = ("status", "severity", "kind", "reporter_role", "deploy_tier")
    search_fields = ("title", "description", "steps", "route_name", "reporter__email")
    list_select_related = ("reporter",)
    readonly_fields = (
        "number",
        "reporter",
        "acting_as",
        "reporter_role",
        "page_url",
        "route_name",
        "user_agent",
        "viewport",
        "locale",
        "app_version",
        "build_commit",
        "deploy_tier",
        "diagnostics_pretty",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            None,
            {"fields": ("number", "title", "severity", "kind", "status", "assignee")},
        ),
        (_("Report"), {"fields": ("description", "steps")}),
        (
            _("Context"),
            {
                "fields": (
                    "reporter",
                    "acting_as",
                    "reporter_role",
                    "page_url",
                    "route_name",
                    "user_agent",
                    "viewport",
                    "locale",
                    "app_version",
                    "build_commit",
                    "deploy_tier",
                    "created_at",
                    "updated_at",
                )
            },
        ),
        (
            _("Diagnostics"),
            {"fields": ("diagnostics_pretty",), "classes": ("collapse",)},
        ),
        (
            _("Resolution"),
            {"fields": ("duplicate_of", "resolved_in_commit", "github_issue_url")},
        ),
    )
    raw_id_fields = ("assignee", "duplicate_of")
    inlines = (IssueAttachmentInline, IssueCommentInline)
    actions = (
        "mark_triaged",
        "mark_in_progress",
        "mark_fixed",
        "mark_closed",
        "assign_to_me",
    )

    @admin.display(description=_("Ref"), ordering="number")
    def reference_display(self, obj):
        return obj.reference

    @admin.display(description=_("Diagnostics"))
    def diagnostics_pretty(self, obj):
        return format_html(
            '<pre style="white-space:pre-wrap;max-height:480px;overflow:auto">{}</pre>',
            json.dumps(obj.diagnostics or {}, indent=2, ensure_ascii=False),
        )

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            if isinstance(obj, IssueComment) and not obj.author_id:
                obj.author = request.user
            obj.save()
        for obj in formset.deleted_objects:
            obj.delete()
        formset.save_m2m()

    def _set_status(self, request, queryset, new_status):
        from .services import notify_status_change

        count = 0
        for issue in queryset:
            if issue.status == new_status:
                continue
            old = issue.status
            issue.status = new_status
            issue.save(update_fields=["status", "updated_at"])
            IssueComment.objects.create(
                issue=issue,
                author=request.user,
                body=f"Status: {old} → {new_status}",
                is_system=True,
            )
            notify_status_change(issue, old, request.user)
            count += 1
        self.message_user(request, _("%(n)d report(s) updated.") % {"n": count})

    @admin.action(description=_("Mark as triaged"))
    def mark_triaged(self, request, queryset):
        self._set_status(request, queryset, Issue.Status.TRIAGED)

    @admin.action(description=_("Mark as in progress"))
    def mark_in_progress(self, request, queryset):
        self._set_status(request, queryset, Issue.Status.IN_PROGRESS)

    @admin.action(description=_("Mark as fixed"))
    def mark_fixed(self, request, queryset):
        self._set_status(request, queryset, Issue.Status.FIXED)

    @admin.action(description=_("Mark as closed"))
    def mark_closed(self, request, queryset):
        self._set_status(request, queryset, Issue.Status.CLOSED)

    @admin.action(description=_("Assign to me"))
    def assign_to_me(self, request, queryset):
        n = queryset.update(assignee=request.user)
        self.message_user(request, _("%(n)d report(s) assigned to you.") % {"n": n})

    def save_model(self, request, obj, form, change):
        old_status = None
        if change and obj.pk:
            old_status = (
                Issue.objects.filter(pk=obj.pk).values_list("status", flat=True).first()
            )
        super().save_model(request, obj, form, change)
        if old_status and old_status != obj.status:
            from .services import notify_status_change

            IssueComment.objects.create(
                issue=obj,
                author=request.user,
                body=f"Status: {old_status} → {obj.status}",
                is_system=True,
            )
            notify_status_change(obj, old_status, request.user)
