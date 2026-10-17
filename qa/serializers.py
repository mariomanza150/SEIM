from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext as _
from rest_framework import serializers

from .models import Issue, IssueAttachment, IssueComment
from .redaction import scrub_diagnostics, scrub_url
from .validators import scan_attachment, validate_attachment


def _user_label(user):
    if not user:
        return None
    full = f"{user.first_name} {user.last_name}".strip()
    return {"id": str(user.pk), "email": user.email, "name": full or user.email}


class IssueAttachmentSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = IssueAttachment
        fields = (
            "id",
            "original_name",
            "content_type",
            "size",
            "kind",
            "created_at",
            "download_url",
        )

    def get_download_url(self, obj):
        return f"/api/qa/issues/{obj.issue_id}/attachments/{obj.pk}/download/"


class IssueCommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = IssueComment
        fields = ("id", "author", "body", "is_internal", "is_system", "created_at")
        read_only_fields = ("id", "author", "is_system", "created_at")

    def get_author(self, obj):
        return _user_label(obj.author)


def validate_uploads(files):
    """Validate + scan a list of uploads; returns [(file, content_type, kind)]."""
    limit = getattr(settings, "QA_MAX_ATTACHMENTS", 5)
    if len(files) > limit:
        raise serializers.ValidationError(
            {"files": _("You can attach up to %(n)d files.") % {"n": limit}}
        )
    cleaned = []
    for f in files:
        try:
            clean, ctype, kind = validate_attachment(f)
            scan_attachment(clean)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                {"files": [f"{getattr(f, 'name', '')}: {m}" for m in exc.messages]}
            ) from exc
        cleaned.append((clean, ctype, kind, getattr(f, "name", "") or clean.name))
    return cleaned


class IssueListSerializer(serializers.ModelSerializer):
    reference = serializers.CharField(read_only=True)
    reporter = serializers.SerializerMethodField()
    attachment_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Issue
        fields = (
            "id",
            "number",
            "reference",
            "title",
            "severity",
            "kind",
            "status",
            "route_name",
            "reporter",
            "reporter_role",
            "app_version",
            "build_commit",
            "attachment_count",
            "created_at",
            "updated_at",
        )

    def get_reporter(self, obj):
        return _user_label(obj.reporter)


class IssueDetailSerializer(IssueListSerializer):
    attachments = IssueAttachmentSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    acting_as = serializers.SerializerMethodField()
    assignee = serializers.SerializerMethodField()
    duplicate_of_reference = serializers.SerializerMethodField()

    class Meta(IssueListSerializer.Meta):
        fields = IssueListSerializer.Meta.fields + (
            "description",
            "steps",
            "acting_as",
            "assignee",
            "duplicate_of_reference",
            "page_url",
            "user_agent",
            "viewport",
            "locale",
            "deploy_tier",
            "diagnostics",
            "resolved_in_commit",
            "github_issue_url",
            "attachments",
            "comments",
        )

    def get_acting_as(self, obj):
        return _user_label(obj.acting_as)

    def get_assignee(self, obj):
        return _user_label(obj.assignee)

    def get_duplicate_of_reference(self, obj):
        return obj.duplicate_of.reference if obj.duplicate_of_id else None

    def get_comments(self, obj):
        show_internal = bool(self.context.get("is_triager"))
        qs = obj.comments.select_related("author").all()
        if not show_internal:
            qs = [c for c in qs if not c.is_internal]
        return IssueCommentSerializer(qs, many=True).data


class IssueCreateSerializer(serializers.ModelSerializer):
    diagnostics = serializers.JSONField(required=False)

    class Meta:
        model = Issue
        fields = (
            "title",
            "description",
            "steps",
            "severity",
            "kind",
            "page_url",
            "route_name",
            "user_agent",
            "viewport",
            "locale",
            "app_version",
            "build_commit",
            "diagnostics",
        )
        extra_kwargs = {
            "title": {"max_length": 200},
            "description": {"max_length": 10000, "required": False},
            "steps": {"max_length": 10000, "required": False},
        }

    def validate_page_url(self, value):
        return scrub_url(value)

    def validate_diagnostics(self, value):
        return scrub_diagnostics(value)

    def validate_title(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError(_("A title is required."))
        return value


class IssueReporterUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ("title", "description", "steps", "severity", "kind")


class IssueTriageUpdateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.UUIDField(required=False, allow_null=True)
    duplicate_of_number = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Issue
        fields = (
            "title",
            "description",
            "steps",
            "severity",
            "kind",
            "status",
            "resolved_in_commit",
            "assignee_id",
            "duplicate_of_number",
        )

    def validate_assignee_id(self, value):
        if value is None:
            return None
        from django.contrib.auth import get_user_model

        user = get_user_model().objects.filter(pk=value, is_active=True).first()
        if user is None:
            raise serializers.ValidationError(_("Unknown user."))
        return user

    def validate_duplicate_of_number(self, value):
        if value is None:
            return None
        issue = Issue.objects.filter(number=value).first()
        if issue is None:
            raise serializers.ValidationError(_("Unknown issue number."))
        return issue

    def update(self, instance, validated_data):
        if "assignee_id" in validated_data:
            instance.assignee = validated_data.pop("assignee_id")
        if "duplicate_of_number" in validated_data:
            dup = validated_data.pop("duplicate_of_number")
            if dup is not None and dup.pk == instance.pk:
                raise serializers.ValidationError(
                    {"duplicate_of_number": _("An issue cannot duplicate itself.")}
                )
            instance.duplicate_of = dup
        return super().update(instance, validated_data)
