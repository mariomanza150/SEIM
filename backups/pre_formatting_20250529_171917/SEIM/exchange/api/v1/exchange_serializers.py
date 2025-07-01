"""
Exchange application serializers for the exchange application.

This module contains serializers for handling student exchange applications,
their submission workflow, and related operations.
"""

from rest_framework import serializers

from ...models import Exchange
from .document_serializers import DocumentSerializer


class ExchangeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Exchange model with nested documents.

    Handles the complete exchange application data including
    student information, program details, and document attachments.
    Provides computed fields for submission status and requirements.
    """

    documents = DocumentSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    can_submit = serializers.SerializerMethodField()
    has_required_documents = serializers.SerializerMethodField()
    student_username = serializers.CharField(source="student.username", read_only=True)

    class Meta:
        model = Exchange
        fields = [
            "id",
            "student",
            "student_username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "date_of_birth",
            "passport_number",
            "student_id",
            "current_university",
            "current_program",
            "current_year",
            "gpa",
            "destination_university",
            "destination_country",
            "exchange_program",
            "start_date",
            "end_date",
            "status",
            "status_display",
            "submission_date",
            "review_date",
            "decision_date",
            "motivation_letter",
            "language_proficiency",
            "special_requirements",
            "emergency_contact",
            "reviewed_by",
            "notes",
            "created_at",
            "updated_at",
            "documents",
            "can_submit",
            "has_required_documents",
        ]
        read_only_fields = [
            "id",
            "student",
            "submission_date",
            "review_date",
            "decision_date",
            "reviewed_by",
            "created_at",
            "updated_at",
        ]

    def get_can_submit(self, obj):
        """
        Check if exchange application can be submitted.

        Args:
            obj: Exchange instance

        Returns:
            bool: True if application meets submission requirements
        """
        return obj.can_submit()

    def get_has_required_documents(self, obj):
        """
        Check if all required documents are uploaded.

        Args:
            obj: Exchange instance

        Returns:
            bool: True if all required documents are present
        """
        return obj.has_required_documents()

    def create(self, validated_data):
        """
        Create exchange application with current user as student.

        Args:
            validated_data: Validated serializer data

        Returns:
            Exchange: Created exchange application instance
        """
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)


class ExchangeSubmitSerializer(serializers.Serializer):
    """
    Serializer for submitting an exchange application.

    Requires explicit confirmation from the student that all
    information is correct and complete before submission.
    """

    confirm = serializers.BooleanField(
        required=True, help_text="Confirm that all information is correct and complete"
    )

    def validate_confirm(self, value):
        """
        Ensure confirmation is provided for submission.

        Args:
            value: Boolean confirmation value

        Returns:
            bool: Validated confirmation value

        Raises:
            ValidationError: If confirmation is not true
        """
        if not value:
            raise serializers.ValidationError(
                "You must confirm to submit the application"
            )
        return value
