from rest_framework import serializers

from .models import (
    Application,
    ApplicationStatus,
    Comment,
    Program,
    TimelineEvent,
)
from .services import ApplicationService


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = "__all__"


class ApplicationSerializer(serializers.ModelSerializer):
    status = serializers.SlugRelatedField(slug_field="name", read_only=True)
    submitted_at = serializers.DateTimeField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Application
        fields = "__all__"

    def validate(self, data):
        # For create operations, get student from request context
        # For update operations, student is already set on the instance
        request = self.context.get('request')
        user = self.instance.student if self.instance else (request.user if request else None)
        program = data.get("program")

        # Only check eligibility for students creating applications
        if user and program and user.has_role("student"):
            ApplicationService.check_eligibility(user, program)
            if not ApplicationService.can_submit_application(user, program):
                raise serializers.ValidationError(
                    "Active application already exists for this program."
                )

        return data

    def create(self, validated_data):
        # Set default status to 'draft' if not provided
        if "status" not in validated_data:
            validated_data["status"] = ApplicationStatus.objects.get(name="draft")

        # Extract dynamic form data from request before creating application
        request = self.context.get('request')
        dynamic_form_data = {}

        if request:
            for key, value in request.data.items():
                if key.startswith('df_'):
                    dynamic_form_data[key] = value

        application = super().create(validated_data)

        # Process dynamic form if present
        if dynamic_form_data and request:
            try:
                ApplicationService.process_dynamic_form_submission(
                    application=application,
                    form_data=dynamic_form_data,
                    user=request.user
                )
            except Exception as e:
                # Log error but don't fail application creation
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error processing dynamic form: {str(e)}")

        return application

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        new_status_name = request.data.get("status") if request else None

        # Extract dynamic form data for update
        dynamic_form_data = {}
        if request:
            for key, value in request.data.items():
                if key.startswith('df_'):
                    dynamic_form_data[key] = value

        if new_status_name and new_status_name != instance.status.name:
            # Only allow status transition via service
            try:
                ApplicationService.transition_status(instance, user, new_status_name)
                instance.refresh_from_db()
            except ValueError as e:
                raise serializers.ValidationError(str(e))
            # Remove status from validated_data to avoid double update
            validated_data.pop("status", None)

        result = super().update(instance, validated_data)

        # Update dynamic form data if present
        if dynamic_form_data and request:
            try:
                ApplicationService.process_dynamic_form_submission(
                    application=instance,
                    form_data=dynamic_form_data,
                    user=request.user
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error updating dynamic form: {str(e)}")

        return result


class ApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationStatus
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    
    def validate_text(self, value):
        """Sanitize comment text to prevent XSS attacks."""
        import re
        # Remove script tags and other dangerous HTML
        value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
        value = re.sub(r'<iframe[^>]*>.*?</iframe>', '', value, flags=re.IGNORECASE | re.DOTALL)
        value = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', value, flags=re.IGNORECASE)  # Remove event handlers
        return value
    
    class Meta:
        model = Comment
        fields = "__all__"


class TimelineEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimelineEvent
        fields = "__all__"
