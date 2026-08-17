from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from grades.models import GradeScale

from .models import (
    AcademicLevel,
    AllowedEmailDomain,
    BankInstitution,
    HomeAcademicProgram,
    Permission,
    Profile,
    Role,
    SchoolFaculty,
    Unidad,
    User,
    UserSession,
    UserSettings,
)


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="primary_role", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "middle_name",
            "last_name",
            "mothers_last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "role",
        )


_CEFR_LEVELS = frozenset({"A1", "A2", "B1", "B2", "C1", "C2"})


class CatalogSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "name", "code", "ordering")


class AllowedEmailDomainSerializer(CatalogSerializer):
    class Meta(CatalogSerializer.Meta):
        model = AllowedEmailDomain


class AcademicLevelSerializer(CatalogSerializer):
    class Meta(CatalogSerializer.Meta):
        model = AcademicLevel


class SchoolFacultySerializer(CatalogSerializer):
    class Meta(CatalogSerializer.Meta):
        model = SchoolFaculty


class UnidadSerializer(CatalogSerializer):
    class Meta(CatalogSerializer.Meta):
        model = Unidad


class BankInstitutionSerializer(CatalogSerializer):
    class Meta(CatalogSerializer.Meta):
        model = BankInstitution


class HomeAcademicProgramSerializer(CatalogSerializer):
    school_name = serializers.CharField(source="school.name", read_only=True)

    class Meta(CatalogSerializer.Meta):
        model = HomeAcademicProgram
        fields = CatalogSerializer.Meta.fields + ("school", "school_name")


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source="user.first_name")
    middle_name = serializers.CharField(
        source="user.middle_name", required=False, allow_blank=True
    )
    last_name = serializers.CharField(source="user.last_name")
    mothers_last_name = serializers.CharField(
        source="user.mothers_last_name", required=False, allow_blank=True
    )
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source="user.email", read_only=True)
    role = serializers.CharField(source="user.primary_role", read_only=True)
    is_admin = serializers.BooleanField(source="user.is_admin", read_only=True)
    is_staff = serializers.BooleanField(source="user.is_staff", read_only=True)
    is_superuser = serializers.BooleanField(source="user.is_superuser", read_only=True)
    gpa = serializers.FloatField(required=False, allow_null=True)
    language = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    language_level = serializers.ChoiceField(
        choices=[
            ("A1", "A1"),
            ("A2", "A2"),
            ("B1", "B1"),
            ("B2", "B2"),
            ("C1", "C1"),
            ("C2", "C2"),
        ],
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    additional_languages = serializers.JSONField(required=False, default=list)
    academic_level = serializers.PrimaryKeyRelatedField(
        queryset=AcademicLevel.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    school = serializers.PrimaryKeyRelatedField(
        queryset=SchoolFaculty.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    unidad = serializers.PrimaryKeyRelatedField(
        queryset=Unidad.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    home_academic_program = serializers.PrimaryKeyRelatedField(
        queryset=HomeAcademicProgram.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    bank_institution = serializers.PrimaryKeyRelatedField(
        queryset=BankInstitution.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    grade_scale = serializers.PrimaryKeyRelatedField(
        queryset=GradeScale.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    credits_approved_percent = serializers.FloatField(required=False, allow_null=True)
    academic_level_name = serializers.CharField(
        source="academic_level.name", read_only=True
    )
    school_name = serializers.CharField(source="school.name", read_only=True)
    unidad_name = serializers.CharField(source="unidad.name", read_only=True)
    home_academic_program_name = serializers.CharField(
        source="home_academic_program.name", read_only=True
    )
    bank_institution_name = serializers.CharField(
        source="bank_institution.name", read_only=True
    )
    grade_scale_name = serializers.CharField(source="grade_scale.name", read_only=True)
    is_personal_academic_complete = serializers.BooleanField(read_only=True)
    is_eligibility_complete = serializers.BooleanField(read_only=True)
    is_ready_to_apply = serializers.BooleanField(read_only=True)
    missing_apply_fields = serializers.SerializerMethodField()
    computed_semester = serializers.SerializerMethodField()
    effective_semester = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return " ".join(
            part
            for part in (
                obj.user.first_name,
                obj.user.middle_name,
                obj.user.last_name,
                obj.user.mothers_last_name,
            )
            if part
        )

    def get_computed_semester(self, obj):
        if not obj.ingress_date:
            return None
        return Profile.calculate_semester_from_ingress(obj.ingress_date)

    def get_effective_semester(self, obj):
        return obj.get_effective_semester()

    def get_missing_apply_fields(self, obj):
        return obj.missing_apply_fields()

    class Meta:
        model = Profile
        fields = (
            "secondary_email",
            "username",
            "first_name",
            "middle_name",
            "last_name",
            "mothers_last_name",
            "full_name",
            "email",
            "role",
            "is_admin",
            "is_staff",
            "is_superuser",
            "matricula",
            "academic_level",
            "academic_level_name",
            "school",
            "school_name",
            "unidad",
            "unidad_name",
            "home_academic_program",
            "home_academic_program_name",
            "gender",
            "date_of_birth",
            "birthplace",
            "postal_code",
            "passport_number",
            "mobile_phone",
            "rfc",
            "bank_institution",
            "bank_institution_name",
            "clabe",
            "gpa",
            "grade_scale",
            "grade_scale_name",
            "ingress_date",
            "current_semester",
            "computed_semester",
            "effective_semester",
            "credits_approved_percent",
            "language",
            "language_level",
            "additional_languages",
            "is_personal_academic_complete",
            "is_eligibility_complete",
            "is_ready_to_apply",
            "missing_apply_fields",
        )

    def to_internal_value(self, data):
        if hasattr(data, "copy"):
            data = data.copy()
        else:
            data = dict(data)
        empty_to_null = (
            "date_of_birth",
            "ingress_date",
            "academic_level",
            "school",
            "unidad",
            "home_academic_program",
            "bank_institution",
            "grade_scale",
            "gpa",
            "current_semester",
            "credits_approved_percent",
            "secondary_email",
            "language",
            "language_level",
        )
        for key in empty_to_null:
            if key in data and data[key] == "":
                data[key] = None
        return super().to_internal_value(data)

    def validate_matricula(self, value):
        return value or None

    def validate_clabe(self, value):
        return value or ""

    def validate(self, attrs):
        attrs = super().validate(attrs)
        school = attrs.get("school", getattr(self.instance, "school", None))
        program = attrs.get(
            "home_academic_program",
            getattr(self.instance, "home_academic_program", None),
        )
        if program and (not school or program.school_id != school.id):
            raise serializers.ValidationError(
                {
                    "home_academic_program": (
                        "The academic program must belong to the selected school."
                    )
                }
            )
        credits = attrs.get(
            "credits_approved_percent",
            getattr(self.instance, "credits_approved_percent", None),
        )
        if credits is not None and (credits < 0 or credits > 100):
            raise serializers.ValidationError(
                {"credits_approved_percent": "Must be between 0 and 100."}
            )
        semester = attrs.get(
            "current_semester", getattr(self.instance, "current_semester", None)
        )
        if semester is not None and semester < 1:
            raise serializers.ValidationError(
                {"current_semester": "Must be at least 1."}
            )
        return attrs

    def validate_additional_languages(self, value):
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("Must be a list.")
        if len(value) > 20:
            raise serializers.ValidationError("At most 20 additional languages.")
        cleaned = []
        for i, item in enumerate(value):
            if not isinstance(item, dict):
                raise serializers.ValidationError(
                    f"Entry {i + 1} must be an object with name and optional level."
                )
            name = str(item.get("name", "")).strip()
            if not name:
                raise serializers.ValidationError(
                    f"Entry {i + 1}: language name is required."
                )
            if len(name) > 64:
                raise serializers.ValidationError(
                    f"Entry {i + 1}: language name is too long."
                )
            level = str(item.get("level", "")).strip() or ""
            if level and level not in _CEFR_LEVELS:
                raise serializers.ValidationError(
                    f"Entry {i + 1}: level must be one of {', '.join(sorted(_CEFR_LEVELS))} or empty."
                )
            cleaned.append({"name": name, "level": level})
        return cleaned

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save(update_fields=[*user_data.keys()])
        return instance


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = "__all__"


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True, allow_blank=False)
    middle_name = serializers.CharField(required=True, allow_blank=False)
    last_name = serializers.CharField(required=True, allow_blank=False)
    mothers_last_name = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password",
            "password2",
            "first_name",
            "middle_name",
            "last_name",
            "mothers_last_name",
        )

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate_email(self, value):
        domain = value.rsplit("@", 1)[-1].strip().lower()
        if not AllowedEmailDomain.objects.filter(
            name__iexact=domain, is_active=True
        ).exists():
            raise serializers.ValidationError(
                "Email domain is not allowed for registration."
            )
        return value.strip().lower()

    def create(self, validated_data):
        """
        Create user using AccountService.

        Delegates registration logic to the service layer.
        """
        from .services import AccountService

        password = validated_data.pop("password")
        validated_data.pop("password2", None)
        first_name = validated_data.pop("first_name", "")
        middle_name = validated_data.pop("middle_name", "")
        last_name = validated_data.pop("last_name", "")
        mothers_last_name = validated_data.pop("mothers_last_name", "")
        username = validated_data["username"]
        email = validated_data["email"]

        try:
            user = AccountService.register_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                mothers_last_name=mothers_last_name,
            )
            return user
        except ValueError as e:
            raise serializers.ValidationError({"detail": str(e)})


class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=64)

    def validate(self, data):
        if not data.get("token"):
            raise serializers.ValidationError({"token": "This field is required."})
        try:
            user = User.objects.get(email_verification_token=data["token"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"token": "Invalid verification token."})
        if user.is_email_verified:
            raise serializers.ValidationError({"token": "Email already verified."})
        data["user"] = user
        return data

    def save(self, **kwargs):
        """Verify email using AccountService."""
        from .services import AccountService

        user = self.validated_data["user"]
        token = self.validated_data["token"]

        try:
            user = AccountService.verify_email(user, token)
            return user
        except ValueError as e:
            raise serializers.ValidationError({"token": str(e)})


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validate credentials using AccountService.

        Delegates all authentication logic to the service layer.
        """
        from .services import AccountService

        login = data.get("login")
        password = data.get("password")

        try:
            # Use AccountService for authentication
            auth_user = AccountService.authenticate_user(login, password)
            data["user"] = auth_user
            return data
        except ValueError as e:
            # Re-raise as serializer validation error
            raise AuthenticationFailed(str(e))


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        """Validate that the email exists in the system."""
        from django.contrib.auth import get_user_model

        User = get_user_model()

        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "No account found with this email address."
            )

        return value

    def save(self, **kwargs):
        """
        Initiate password reset using AccountService.
        """
        from .services import AccountService

        email = self.validated_data["email"]
        AccountService.initiate_password_reset(email)
        return {"detail": "Password reset email sent"}


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField(max_length=64)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        """Validate that the email and token combination is valid."""
        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            user = User.objects.get(email=data["email"])
            # Check if token matches (in real implementation, you'd check against stored token)
            # For now, we validate that the user exists
            if not user:
                raise serializers.ValidationError("Invalid email or token.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or token.")

        return data

    def save(self, **kwargs):
        """Reset password using AccountService."""
        from .services import AccountService

        try:
            user = AccountService.reset_password(
                email=self.validated_data["email"],
                token=self.validated_data["token"],
                new_password=self.validated_data["new_password"],
            )
            return user
        except ValueError as e:
            raise serializers.ValidationError({"detail": str(e)})


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError as exc:
            errors = exc.detail
            if "new_password2" in errors:
                errors["new_password"] = errors.pop("new_password2")
            raise serializers.ValidationError(errors)

    def validate(self, data):
        if not data.get("new_password") or not data.get("new_password2"):
            raise serializers.ValidationError(
                {"new_password": "Both new password fields are required."}
            )
        if data["new_password"] != data["new_password2"]:
            raise serializers.ValidationError(
                {"new_password": "New passwords do not match."}
            )
        return data

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def save(self, **kwargs):
        """Change password using AccountService."""
        from .services import AccountService

        user = self.context["request"].user

        try:
            user = AccountService.change_password(
                user=user,
                old_password=self.validated_data["old_password"],
                new_password=self.validated_data["new_password"],
            )
            return user
        except ValueError as e:
            raise serializers.ValidationError({"old_password": str(e)})


class UserSettingsSerializer(serializers.ModelSerializer):
    """Serializer for user settings."""

    class Meta:
        model = UserSettings
        fields = [
            "theme",
            "font_size",
            "high_contrast",
            "reduce_motion",
            "email_applications",
            "email_documents",
            "email_comments",
            "email_programs",
            "email_system",
            "inapp_applications",
            "inapp_documents",
            "inapp_comments",
            "inapp_programs",
            "inapp_system",
            "notification_digest_frequency",
            "email_notification_digest",
            "profile_public",
            "share_analytics",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        settings, created = UserSettings.objects.get_or_create(
            user=user, defaults=validated_data
        )
        if not created:
            return self.update(settings, validated_data)
        return settings

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AppearanceSettingsSerializer(serializers.ModelSerializer):
    """Serializer for appearance settings only."""

    class Meta:
        model = UserSettings
        fields = ["theme", "font_size"]

    def create(self, validated_data):
        user = self.context["request"].user
        settings, created = UserSettings.objects.get_or_create(
            user=user, defaults=validated_data
        )
        if not created:
            for attr, value in validated_data.items():
                setattr(settings, attr, value)
            settings.save()
        return settings


class NotificationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for notification settings only."""

    class Meta:
        model = UserSettings
        fields = [
            "email_applications",
            "email_documents",
            "email_comments",
            "email_programs",
            "email_system",
            "inapp_applications",
            "inapp_documents",
            "inapp_comments",
            "inapp_programs",
            "inapp_system",
            "notification_digest_frequency",
            "email_notification_digest",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        settings, created = UserSettings.objects.get_or_create(
            user=user, defaults=validated_data
        )
        if not created:
            for attr, value in validated_data.items():
                setattr(settings, attr, value)
            settings.save()
        return settings


class PrivacySettingsSerializer(serializers.ModelSerializer):
    """Serializer for privacy settings only."""

    class Meta:
        model = UserSettings
        fields = ["profile_public", "share_analytics"]

    def create(self, validated_data):
        user = self.context["request"].user
        settings, created = UserSettings.objects.get_or_create(
            user=user, defaults=validated_data
        )
        if not created:
            for attr, value in validated_data.items():
                setattr(settings, attr, value)
            settings.save()
        return settings


class UserSessionSerializer(serializers.ModelSerializer):
    """Serializer for user sessions."""

    class Meta:
        model = UserSession
        fields = ["id", "device", "location", "last_activity", "is_active"]
        read_only_fields = ["id", "device", "location", "last_activity", "is_active"]


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout request."""

    refresh = serializers.CharField(
        required=False, help_text="JWT refresh token to blacklist"
    )


class LogoutResponseSerializer(serializers.Serializer):
    """Serializer for logout response."""

    message = serializers.CharField()


class DeleteAccountResponseSerializer(serializers.Serializer):
    """Serializer for account deletion response."""

    detail = serializers.CharField()


class ProfileUpdateRequestSerializer(serializers.Serializer):
    """Serializer for profile update request."""

    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=False, max_length=150)
    last_name = serializers.CharField(required=False, max_length=150)


class ProfileUpdateResponseSerializer(serializers.Serializer):
    """Serializer for profile update response."""

    detail = serializers.CharField()


class RevokeSessionRequestSerializer(serializers.Serializer):
    """Serializer for session revocation request."""

    pass  # No request body needed, session_id is in URL


class RevokeSessionResponseSerializer(serializers.Serializer):
    """Serializer for session revocation response."""

    detail = serializers.CharField()
