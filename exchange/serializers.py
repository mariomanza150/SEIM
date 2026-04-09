from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers

from .models import (
    Application,
    ApplicationStatus,
    Comment,
    ExchangeAgreement,
    Program,
    SavedSearch,
    TimelineEvent,
)

_TIMELINE_EVENT_FIELDS = tuple(f.name for f in TimelineEvent._meta.fields) + ("created_by_name",)
from .services import ApplicationService

_APPLICATION_MODEL_FIELDS = tuple(
    f.name for f in Application._meta.fields
) + tuple(f.name for f in Application._meta.many_to_many)


class ProgramSerializer(serializers.ModelSerializer):
    application_window_open = serializers.SerializerMethodField()
    application_window_message = serializers.SerializerMethodField()
    coordinator_details = serializers.SerializerMethodField()

    def get_application_window_open(self, obj):
        return obj.is_application_open()

    def get_application_window_message(self, obj):
        return obj.application_window_message

    def get_coordinator_details(self, obj):
        return [
            {
                "id": coordinator.id,
                "username": coordinator.username,
                "email": coordinator.email,
                "full_name": coordinator.get_full_name().strip() or coordinator.username,
            }
            for coordinator in obj.coordinators.all()
        ]

    def validate_coordinators(self, value):
        invalid_users = [user.username for user in value if not user.has_role("coordinator")]
        if invalid_users:
            raise serializers.ValidationError(
                f"Only users with the coordinator role can be assigned to programs: {', '.join(invalid_users)}."
            )
        return value

    class Meta:
        model = Program
        fields = "__all__"


class ApplicationSerializer(serializers.ModelSerializer):
    status = serializers.SlugRelatedField(slug_field="name", read_only=True)
    submitted_at = serializers.DateTimeField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(read_only=True)
    dynamic_form_submission = serializers.SerializerMethodField()
    dynamic_form_layout = serializers.SerializerMethodField()
    document_checklist = serializers.SerializerMethodField()
    assigned_coordinator_name = serializers.SerializerMethodField()
    effective_coordinator = serializers.SerializerMethodField()
    student_display_name = serializers.SerializerMethodField()
    student_email = serializers.SerializerMethodField()
    program_name = serializers.SerializerMethodField()
    readiness = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = _APPLICATION_MODEL_FIELDS + (
            "dynamic_form_submission",
            "dynamic_form_layout",
            "document_checklist",
            "readiness",
            "assigned_coordinator_name",
            "effective_coordinator",
            "student_display_name",
            "student_email",
            "program_name",
        )

    def get_dynamic_form_submission(self, obj):
        submission = ApplicationService.get_dynamic_form_submission(obj)
        if not submission:
            return None

        return {
            "id": submission.id,
            "form_type": submission.form_type_id,
            "responses": submission.responses,
            "submitted_at": submission.submitted_at,
            "updated_at": submission.updated_at,
        }

    def get_assigned_coordinator_name(self, obj):
        coordinator = obj.assigned_coordinator
        if not coordinator:
            return None
        return coordinator.get_full_name().strip() or coordinator.username

    def get_effective_coordinator(self, obj):
        coordinator = obj.effective_coordinator
        if not coordinator:
            return None
        return {
            "id": coordinator.id,
            "username": coordinator.username,
            "email": coordinator.email,
            "full_name": coordinator.get_full_name().strip() or coordinator.username,
        }

    def get_student_display_name(self, obj):
        s = obj.student
        name = s.get_full_name().strip()
        return name or s.username or s.email

    def get_student_email(self, obj):
        return obj.student.email

    def get_program_name(self, obj):
        return obj.program.name

    def get_readiness(self, obj):
        from exchange.readiness import compute_application_readiness

        view = self.context.get("view")
        for_list = bool(view and getattr(view, "action", None) == "list")
        return compute_application_readiness(obj, include_dynamic_form=not for_list)

    def get_dynamic_form_layout(self, obj):
        ft = obj.program.application_form
        if not ft:
            return {
                "multi_step": False,
                "steps": [],
                "current_step": obj.dynamic_form_current_step,
            }
        return {
            "multi_step": ft.is_multi_step(),
            "steps": ft.get_multi_step_layout(),
            "current_step": obj.dynamic_form_current_step,
        }

    def get_document_checklist(self, obj):
        view = self.context.get("view")
        if view and getattr(view, "action", None) == "list":
            return None
        from documents.services import DocumentService

        return DocumentService.build_application_document_checklist(obj)

    def _get_dynamic_form_data(self):
        request = self.context.get("request")
        if not request:
            return {}

        data = {
            key: value
            for key, value in request.data.items()
            if key.startswith("df_")
        }
        if "dynamic_form_current_step" in request.data:
            data["dynamic_form_current_step"] = request.data.get("dynamic_form_current_step")
        return data

    def _process_dynamic_form_submission(self, application, user, dynamic_form_data):
        if not dynamic_form_data:
            return None

        try:
            return ApplicationService.process_dynamic_form_submission(
                application=application,
                form_data=dynamic_form_data,
                user=user,
            )
        except DjangoValidationError as exc:
            messages = exc.messages if hasattr(exc, "messages") else [str(exc)]
            raise serializers.ValidationError({"dynamic_form": messages})

    def validate(self, data):
        # For create operations, get student from request context
        # For update operations, student is already set on the instance
        request = self.context.get('request')
        user = self.instance.student if self.instance else (request.user if request else None)
        program = data.get("program")

        if not self.instance and program:
            try:
                ApplicationService.check_application_window(program)
            except ValueError as e:
                raise serializers.ValidationError({"program": str(e)})

        # Only check eligibility for students creating applications
        if user and program and user.has_role("student"):
            try:
                ApplicationService.check_eligibility(user, program)
            except ValueError as e:
                raise serializers.ValidationError(
                    {"program": str(e).replace("Eligibility requirements not met:\n- ", "").split("\n- ")}
                    if "\n- " in str(e)
                    else {"program": str(e)}
                )
            if not ApplicationService.can_submit_application(user, program):
                raise serializers.ValidationError(
                    {"program": "Active application already exists for this program."}
                )

        return data

    def validate_assigned_coordinator(self, value):
        if value and not value.has_role("coordinator"):
            raise serializers.ValidationError("Assigned coordinator must have the coordinator role.")
        return value

    def _request_can_manage_assignments(self):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        return bool(user and (user.has_role("admin") or user.has_role("coordinator")))

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data["student"] = request.user

        if not self._request_can_manage_assignments():
            validated_data.pop("assigned_coordinator", None)

        # Set default status to 'draft' if not provided
        if "status" not in validated_data:
            validated_data["status"] = ApplicationStatus.objects.get(name="draft")

        dynamic_form_data = self._get_dynamic_form_data()

        with transaction.atomic():
            application = super().create(validated_data)

            if not application.assigned_coordinator_id:
                default_coordinator = ApplicationService.get_default_coordinator(application.program)
                if default_coordinator:
                    application.assigned_coordinator = default_coordinator
                    application.save(update_fields=["assigned_coordinator"])

            if request and dynamic_form_data:
                self._process_dynamic_form_submission(
                    application=application,
                    user=request.user,
                    dynamic_form_data=dynamic_form_data,
                )

        return application

    def update(self, instance, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        new_status_name = request.data.get("status") if request else None

        if not self._request_can_manage_assignments():
            validated_data.pop("assigned_coordinator", None)

        dynamic_form_data = self._get_dynamic_form_data()

        with transaction.atomic():
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

            if request and dynamic_form_data:
                self._process_dynamic_form_submission(
                    application=instance,
                    user=request.user,
                    dynamic_form_data=dynamic_form_data,
                )

        return result


class ApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationStatus
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    author_name = serializers.SerializerMethodField()
    author_role = serializers.CharField(source="author.role", read_only=True)
    
    def validate_text(self, value):
        """Sanitize comment text to prevent XSS attacks."""
        import re
        # Remove script tags and other dangerous HTML
        value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
        value = re.sub(r'<iframe[^>]*>.*?</iframe>', '', value, flags=re.IGNORECASE | re.DOTALL)
        value = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', value, flags=re.IGNORECASE)  # Remove event handlers
        return value

    def get_author_name(self, obj):
        full_name = obj.author.get_full_name().strip()
        return full_name or obj.author.username or obj.author.email
    
    class Meta:
        model = Comment
        fields = "__all__"


class TimelineEventSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = TimelineEvent
        fields = _TIMELINE_EVENT_FIELDS

    def get_created_by_name(self, obj):
        user = obj.created_by
        if not user:
            return None
        name = user.get_full_name().strip()
        return name or user.username or user.email


class SavedSearchSerializer(serializers.ModelSerializer):
    """Serializer for SavedSearch model."""
    
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = SavedSearch
        fields = "__all__"
    
    def create(self, validated_data):
        """Set user from request context."""
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user
        return super().create(validated_data)


class ExchangeAgreementSerializer(serializers.ModelSerializer):
    programs = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Program.objects.all(), required=False
    )

    class Meta:
        model = ExchangeAgreement
        fields = "__all__"

    def create(self, validated_data):
        programs = validated_data.pop("programs", None)
        instance = ExchangeAgreement.objects.create(**validated_data)
        if programs is not None:
            instance.programs.set(programs)
        return instance

    def update(self, instance, validated_data):
        programs = validated_data.pop("programs", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if programs is not None:
            instance.programs.set(programs)
        return instance


class CalendarEventSerializer(serializers.Serializer):
    """Serializer for calendar events in FullCalendar format."""
    
    id = serializers.CharField()
    title = serializers.CharField()
    start = serializers.DateTimeField()
    end = serializers.DateTimeField(required=False, allow_null=True)
    url = serializers.URLField(required=False, allow_null=True)
    className = serializers.CharField(required=False, allow_null=True)
    backgroundColor = serializers.CharField(required=False, allow_null=True)
    borderColor = serializers.CharField(required=False, allow_null=True)
    allDay = serializers.BooleanField(default=False)
