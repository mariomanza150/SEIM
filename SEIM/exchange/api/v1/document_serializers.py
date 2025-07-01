"""
Document-related serializers for the exchange application.

This module contains serializers for handling document uploads, validation,
and verification workflows.
"""

from rest_framework import serializers

from ...models import Document
from ...validators import CompositeFileValidator


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Document model with file upload validation.

    Handles document creation, validation, and metadata extraction.
    Provides computed fields for download URLs and expiration status.
    """

    file = serializers.FileField(write_only=True, required=False)
    download_url = serializers.SerializerMethodField(read_only=True)
    is_expired = serializers.SerializerMethodField(read_only=True)
    category_display = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "file",
            "original_filename",
            "file_size",
            "mime_type",
            "category",
            "category_display",
            "description",
            "checksum",
            "is_verified",
            "verification_date",
            "verification_notes",
            "uploaded_at",
            "modified_at",
            "download_url",
            "is_expired",
            "is_public",
            "expires_at",
        ]
        read_only_fields = [
            "id",
            "original_filename",
            "file_size",
            "mime_type",
            "checksum",
            "uploaded_at",
            "modified_at",
            "uploaded_by",
        ]

    def get_download_url(self, obj):
        """
        Generate download URL for the document.

        Args:
            obj: Document instance

        Returns:
            str: Absolute URL for document download, or None if no file
        """
        request = self.context.get("request")
        if request and obj.file:
            return request.build_absolute_uri(obj.get_download_url())
        return None

    def get_is_expired(self, obj):
        """
        Check if document is expired.

        Args:
            obj: Document instance

        Returns:
            bool: True if document has expired
        """
        return obj.is_expired

    def validate_file(self, value):
        """
        Validate uploaded file using composite validation.

        Args:
            value: Uploaded file instance

        Returns:
            File instance with validation metadata attached

        Raises:
            ValidationError: If file validation fails
        """
        if value:
            validator = CompositeFileValidator()
            checksum = validator.validate(value)
            value._validated = True
            value.checksum = checksum
        return value

    def create(self, validated_data):
        """
        Create document with proper validation and metadata extraction.

        Args:
            validated_data: Validated serializer data

        Returns:
            Document: Created document instance

        Raises:
            ValidationError: If file is missing or validation fails
        """
        file = validated_data.pop("file", None)

        if not file:
            raise serializers.ValidationError({"file": "File is required"})

        # Set additional fields from the file
        validated_data["original_filename"] = file.name
        validated_data["file_size"] = file.size
        validated_data["checksum"] = getattr(file, "checksum", "")
        validated_data["uploaded_by"] = self.context["request"].user

        # Create the document
        document = Document(**validated_data)
        document.file = file
        document.save()

        return document


class DocumentVerificationSerializer(serializers.Serializer):
    """
    Serializer for document verification workflow.

    Used by administrators to approve or reject uploaded documents
    with required verification notes.
    """

    is_verified = serializers.BooleanField(required=True, help_text="Whether the document is verified as valid")
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Verification notes, required when rejecting documents",
    )

    def validate(self, attrs):
        """
        Ensure notes are provided when rejecting documents.

        Args:
            attrs: Validated attribute dictionary

        Returns:
            dict: Validated attributes

        Raises:
            ValidationError: If document is rejected without notes
        """
        if not attrs.get("is_verified") and not attrs.get("notes"):
            raise serializers.ValidationError({"notes": "Notes are required when rejecting a document"})
        return attrs
