from rest_framework import serializers

from .models import (
    Document,
    DocumentComment,
    DocumentResubmissionRequest,
    DocumentType,
    DocumentValidation,
)
from .services import DocumentService


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = "__all__"


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Document
        fields = "__all__"
        read_only_fields = ['uploaded_by', 'validated_at', 'is_valid']

    def validate_file(self, file):
        DocumentService.validate_file_type_and_size(file)
        if not DocumentService.virus_scan(file):
            raise serializers.ValidationError("File failed virus scan.")
        return file

    def create(self, validated_data):
        # uploaded_by is now set in perform_create, not here
        uploaded_by = self.context['request'].user
        return DocumentService.upload_document(
            validated_data["application"],
            validated_data["type"],
            validated_data["file"],
            uploaded_by,
        )

    def update(self, instance, validated_data):
        # Check if document replacement is allowed
        if not DocumentService.can_replace_document(
            instance, self.context["request"].user
        ):
            raise serializers.ValidationError(
                "Document cannot be replaced. A resubmission request is required or you need admin privileges."
            )

        # Validate new file if provided
        if "file" in validated_data:
            file = validated_data["file"]
            DocumentService.validate_file_type_and_size(file)
            if not DocumentService.virus_scan(file):
                raise serializers.ValidationError("File failed virus scan.")

        return super().update(instance, validated_data)


class DocumentValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentValidation
        fields = "__all__"


class DocumentResubmissionRequestSerializer(serializers.ModelSerializer):
    requested_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DocumentResubmissionRequest
        fields = "__all__"
        read_only_fields = ['requested_by', 'requested_at']

    def create(self, validated_data):
        # Set requested_by from request context if available
        if 'request' in self.context:
            validated_data['requested_by'] = self.context['request'].user
        return super().create(validated_data)


class DocumentCommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DocumentComment
        fields = "__all__"
        read_only_fields = ['author', 'created_at']

    def create(self, validated_data):
        # Set author from request context if available
        if 'request' in self.context:
            validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
