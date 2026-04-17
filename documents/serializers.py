from django.db.models import Q
from rest_framework import serializers

from .models import (
    Document,
    DocumentComment,
    DocumentResubmissionRequest,
    DocumentType,
    DocumentValidation,
    ExchangeAgreementDocument,
)
from notifications.services import NotificationService

from .services import DocumentService


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = "__all__"


class DocumentTypeSummarySerializer(serializers.ModelSerializer):
    """Compact type payload for nested document responses (list/detail)."""

    class Meta:
        model = DocumentType
        fields = ("id", "name", "description")


class DocumentValidationSerializer(serializers.ModelSerializer):
    validator_name = serializers.SerializerMethodField()

    class Meta:
        model = DocumentValidation
        fields = [f.name for f in DocumentValidation._meta.concrete_fields] + [
            "validator_name",
        ]

    def get_validator_name(self, obj):
        v = obj.validator
        if not v:
            return None
        name = v.get_full_name().strip()
        return name or v.username


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

    class Meta:
        model = DocumentComment
        fields = "__all__"
        read_only_fields = ["author", "created_at"]

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
        ]
        read_only_fields = ["uploaded_by", "validated_at", "is_valid"]

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
        DocumentService.validate_file_type_and_size(file)
        if not DocumentService.virus_scan(file):
            raise serializers.ValidationError("File failed virus scan.")
        return file

    def create(self, validated_data):
        uploaded_by = self.context["request"].user
        return DocumentService.upload_document(
            validated_data["application"],
            validated_data["type"],
            validated_data["file"],
            uploaded_by,
        )

    def update(self, instance, validated_data):
        if not DocumentService.can_replace_document(
            instance, self.context["request"].user
        ):
            raise serializers.ValidationError(
                "Document cannot be replaced. A resubmission request is required or you need admin privileges."
            )

        if "file" in validated_data:
            file = validated_data["file"]
            DocumentService.validate_file_type_and_size(file)
            if not DocumentService.virus_scan(file):
                raise serializers.ValidationError("File failed virus scan.")

        file_replacing = "file" in validated_data
        user = self.context["request"].user
        instance = super().update(instance, validated_data)
        if file_replacing and user.has_role("student"):
            if instance.application.student_id == user.id:
                DocumentService.notify_coordinators_document_replaced(instance)
        elif file_replacing:
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
