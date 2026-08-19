from django.db.models import Q
from rest_framework import serializers

from notifications.services import NotificationService

from .models import (
    Document,
    DocumentComment,
    DocumentResubmissionRequest,
    DocumentType,
    DocumentValidation,
    ExchangeAgreementDocument,
)
from .services import DocumentService


class ProgramRequirementNestedSerializer(serializers.Serializer):
    """Writable nested program-requirement rows on a document type."""

    id = serializers.IntegerField(required=False, allow_null=True)
    program = serializers.UUIDField()
    program_name = serializers.CharField(read_only=True)
    program_start_date = serializers.DateField(read_only=True)
    is_required = serializers.BooleanField(required=False, default=True)
    deadline = serializers.DateField(required=False, allow_null=True)
    deadline_days_before_program_deadline = serializers.IntegerField(
        required=False, allow_null=True, min_value=0
    )
    deadline_days_after_program_start = serializers.IntegerField(
        required=False, allow_null=True, min_value=0
    )
    instructions_override = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    sort_order = serializers.IntegerField(required=False, min_value=0, default=0)
    resolved_deadline = serializers.DateField(read_only=True)


class DocumentTypeSerializer(serializers.ModelSerializer):
    has_template = serializers.SerializerMethodField()
    template_filename = serializers.SerializerMethodField()
    program_requirements = ProgramRequirementNestedSerializer(
        many=True, required=False, write_only=True
    )
    requirement_count = serializers.SerializerMethodField()

    class Meta:
        model = DocumentType
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "submission_mode",
            "template_file",
            "has_template",
            "template_filename",
            "instructions",
            "faq",
            "accepted_extensions",
            "max_file_size_mb",
            "allows_multiple",
            "program_requirements",
            "requirement_count",
        )
        extra_kwargs = {
            "template_file": {"write_only": True, "required": False},
        }

    def get_has_template(self, obj):
        return bool(obj.template_file)

    def get_template_filename(self, obj):
        if not obj.template_file:
            return ""
        return obj.template_file.name.rsplit("/", 1)[-1]

    def get_requirement_count(self, obj):
        cached = getattr(obj, "requirement_count", None)
        if cached is not None:
            return cached
        return obj.program_requirements.count()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        include_reqs = self.context.get("include_program_requirements", True)
        if not include_reqs:
            ret.pop("program_requirements", None)
            return ret
        reqs = instance.program_requirements.select_related("program").order_by(
            "sort_order", "id"
        )
        ret["program_requirements"] = [
            {
                "id": req.id,
                "program": str(req.program_id),
                "program_name": req.program.name,
                "program_start_date": (
                    req.program.start_date.isoformat()
                    if req.program.start_date
                    else None
                ),
                "is_required": req.is_required,
                "deadline": req.deadline.isoformat() if req.deadline else None,
                "deadline_days_before_program_deadline": (
                    req.deadline_days_before_program_deadline
                ),
                "deadline_days_after_program_start": (
                    req.deadline_days_after_program_start
                ),
                "instructions_override": req.instructions_override or "",
                "sort_order": req.sort_order,
                "resolved_deadline": (
                    req.resolve_deadline().isoformat()
                    if req.resolve_deadline()
                    else None
                ),
            }
            for req in reqs
        ]
        return ret

    def validate_slug(self, value):
        if value in ("", None):
            return None
        return value

    def validate_accepted_extensions(self, value):
        if not value:
            return ""
        cleaned = [
            ext.strip().lower().lstrip(".")
            for ext in str(value).split(",")
            if ext.strip()
        ]
        return ",".join(cleaned)

    def _sync_program_requirements(self, instance, rows):
        from exchange.models import Program, ProgramDocumentRequirement

        if rows is None:
            return
        keep_ids = []
        for row in rows:
            program_id = row["program"]
            try:
                program = Program.objects.get(pk=program_id)
            except Program.DoesNotExist as exc:
                raise serializers.ValidationError(
                    {"program_requirements": f"Unknown program: {program_id}"}
                ) from exc
            defaults = {
                "is_required": row.get("is_required", True),
                "deadline": row.get("deadline"),
                "deadline_days_before_program_deadline": row.get(
                    "deadline_days_before_program_deadline"
                ),
                "deadline_days_after_program_start": row.get(
                    "deadline_days_after_program_start"
                ),
                "instructions_override": row.get("instructions_override") or "",
                "sort_order": row.get("sort_order") or 0,
            }
            req_id = row.get("id")
            if req_id:
                updated = ProgramDocumentRequirement.objects.filter(
                    pk=req_id, document_type=instance
                ).update(program=program, **defaults)
                if not updated:
                    raise serializers.ValidationError(
                        {
                            "program_requirements": (
                                f"Requirement {req_id} does not belong to this type."
                            )
                        }
                    )
                keep_ids.append(req_id)
            else:
                req, _ = ProgramDocumentRequirement.objects.update_or_create(
                    program=program,
                    document_type=instance,
                    defaults=defaults,
                )
                keep_ids.append(req.id)
        ProgramDocumentRequirement.objects.filter(document_type=instance).exclude(
            pk__in=keep_ids
        ).delete()

    def create(self, validated_data):
        rows = validated_data.pop("program_requirements", None)
        instance = super().create(validated_data)
        self._sync_program_requirements(instance, rows)
        return instance

    def update(self, instance, validated_data):
        rows = validated_data.pop("program_requirements", None)
        instance = super().update(instance, validated_data)
        self._sync_program_requirements(instance, rows)
        return instance


class DocumentTypeListSerializer(DocumentTypeSerializer):
    class Meta(DocumentTypeSerializer.Meta):
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "submission_mode",
            "has_template",
            "template_filename",
            "accepted_extensions",
            "max_file_size_mb",
            "allows_multiple",
            "requirement_count",
        )

    def to_representation(self, instance):
        self.context["include_program_requirements"] = False
        return super().to_representation(instance)


class DocumentTypeSummarySerializer(serializers.ModelSerializer):
    """Compact type payload for nested document responses (list/detail)."""

    has_template = serializers.SerializerMethodField()

    class Meta:
        model = DocumentType
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "submission_mode",
            "instructions",
            "faq",
            "accepted_extensions",
            "max_file_size_mb",
            "allows_multiple",
            "has_template",
        )

    def get_has_template(self, obj):
        return bool(obj.template_file)


def _user_display_name(user):
    if not user:
        return ""
    name = user.get_full_name().strip()
    return name or user.username or getattr(user, "email", "") or ""


class DocumentValidationSerializer(serializers.ModelSerializer):
    validator_name = serializers.SerializerMethodField()

    class Meta:
        model = DocumentValidation
        fields = [f.name for f in DocumentValidation._meta.concrete_fields] + [
            "validator_name",
        ]

    def get_validator_name(self, obj):
        if not obj.validator:
            return None
        return _user_display_name(obj.validator)


class DocumentResubmissionRequestSerializer(serializers.ModelSerializer):
    requested_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DocumentResubmissionRequest
        fields = "__all__"
        read_only_fields = ["requested_by", "requested_at"]

    def create(self, validated_data):
        validated_data.pop("resolved", None)
        user = self.context["request"].user
        return DocumentService.request_resubmission(
            validated_data["document"],
            user,
            validated_data["reason"],
        )


class DocumentCommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = DocumentComment
        fields = "__all__"
        read_only_fields = ["author", "author_name", "created_at"]

    def get_author_name(self, obj):
        return _user_display_name(obj.author)

    def create(self, validated_data):
        req = self.context.get("request")
        if req is not None:
            validated_data.setdefault("author", req.user)
        comment = super().create(validated_data)
        author = comment.author
        doc = comment.document
        if not comment.is_private:
            student = doc.application.student
            if student.id != author.id and (
                author.has_role("coordinator") or author.has_role("admin")
            ):
                excerpt = (comment.text or "")[:500]
                NotificationService.send_notification(
                    student,
                    "Feedback on your document",
                    f"Regarding {doc.type.name}: {excerpt}",
                    notification_type="both",
                    action_url=f"/documents/{doc.id}/",
                    action_text="View document",
                    category="info",
                    settings_category="comments",
                    transactional_route_key="document_staff_comment_public",
                )
        NotificationService.broadcast_application_sync(
            str(doc.application_id), "document_comment_added", str(doc.id)
        )
        return comment


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField(read_only=True)
    uploaded_by_name = serializers.SerializerMethodField()
    validations = DocumentValidationSerializer(
        many=True, read_only=True, source="documentvalidation_set"
    )
    resubmission_requests = DocumentResubmissionRequestSerializer(
        many=True, read_only=True, source="documentresubmissionrequest_set"
    )
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [f.name for f in Document._meta.concrete_fields] + [
            "validations",
            "resubmission_requests",
            "comments",
            "uploaded_by_name",
        ]
        read_only_fields = ["uploaded_by", "uploaded_by_name", "validated_at", "is_valid"]

    def get_uploaded_by_name(self, obj):
        return _user_display_name(obj.uploaded_by) or None

    def get_comments(self, obj):
        qs = obj.documentcomment_set.all().order_by("created_at")
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            u = request.user
            staff = getattr(u, "has_role", None) and (
                u.has_role("coordinator") or u.has_role("admin")
            )
            if not staff:
                qs = qs.filter(Q(is_private=False) | Q(author=u))
        return DocumentCommentSerializer(qs, many=True).data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["type"] = DocumentTypeSummarySerializer(
            instance.type, context=self.context
        ).data
        ret["application"] = {
            "id": str(instance.application_id),
            "program_name": instance.application.program.name,
        }
        return ret

    def validate_file(self, file):
        # Type-aware checks run in create/update once document type is known.
        try:
            DocumentService.validate_file_type_and_size(file)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        if not DocumentService.virus_scan(file):
            raise serializers.ValidationError("File failed virus scan.")
        return file

    def create(self, validated_data):
        uploaded_by = self.context["request"].user
        try:
            return DocumentService.upload_document(
                validated_data["application"],
                validated_data["type"],
                validated_data["file"],
                uploaded_by,
            )
        except ValueError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc

    def update(self, instance, validated_data):
        user = self.context["request"].user
        if not DocumentService.can_replace_document(instance, user):
            raise serializers.ValidationError(
                "Document cannot be replaced. A resubmission request is required or you need admin privileges."
            )

        if "file" in validated_data:
            file = validated_data["file"]
            for_staff = getattr(user, "has_role", None) and (
                user.has_role("coordinator") or user.has_role("admin")
            )
            try:
                DocumentService.ensure_upload_allowed(
                    instance.application,
                    instance.type,
                    for_staff=bool(for_staff),
                    replacing=True,
                )
                DocumentService.validate_file_type_and_size(
                    file, document_type=instance.type
                )
            except ValueError as exc:
                raise serializers.ValidationError({"file": str(exc)}) from exc
            if not DocumentService.virus_scan(file):
                raise serializers.ValidationError("File failed virus scan.")

        file_replacing = "file" in validated_data
        instance = super().update(instance, validated_data)
        if file_replacing:
            DocumentService.resolve_open_resubmission_requests(instance)
            if user.has_role("student") and instance.application.student_id == user.id:
                DocumentService.notify_coordinators_document_replaced(instance)
            else:
                NotificationService.broadcast_application_sync(
                    str(instance.application_id), "document_replaced", str(instance.id)
                )
        return instance


class ExchangeAgreementDocumentSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ExchangeAgreementDocument
        fields = "__all__"
        read_only_fields = ("uploaded_by",)

    def validate_file(self, file):
        try:
            DocumentService.validate_file_type_and_size(file)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc))
        if not DocumentService.virus_scan(file):
            raise serializers.ValidationError("File failed virus scan.")
        return file

    def validate(self, attrs):
        sup = attrs.get("supersedes")
        if sup is None:
            return attrs
        agreement = attrs.get("agreement")
        category = attrs.get("category")
        if self.instance:
            agreement = agreement or self.instance.agreement
            category = category if category is not None else self.instance.category
        if agreement and sup.agreement_id != agreement.id:
            raise serializers.ValidationError(
                {"supersedes": "Prior document must belong to the same agreement."}
            )
        if category is not None and sup.category != category:
            raise serializers.ValidationError(
                {"supersedes": "Prior document must use the same category."}
            )
        return attrs

    def create(self, validated_data):
        validated_data["uploaded_by"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("supersedes", None)
        validated_data.pop("agreement", None)
        if "file" in validated_data:
            file = validated_data["file"]
            try:
                DocumentService.validate_file_type_and_size(file)
            except ValueError as exc:
                raise serializers.ValidationError({"file": str(exc)})
            if not DocumentService.virus_scan(file):
                raise serializers.ValidationError({"file": "File failed virus scan."})
        return super().update(instance, validated_data)
