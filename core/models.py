import uuid

from django.db import models

# Create your models here.


class UUIDModel(models.Model):
    """
    Abstract base model with UUID primary key.
    Use for all domain models to ensure global uniqueness.
    No domain-specific logic here.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """
    Abstract base model with created/updated timestamps.
    Use for all models that require audit trails.
    No domain-specific logic here.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class InstitutionFeatureSettings(TimeStampedModel):
    """
    Singleton institution feature flags (admin-toggleable).

    Row is always ``pk=1``. Historical scholarship data is kept when flags
    are turned off; surfaces and APIs hide it instead of deleting.
    """

    scholarships_enabled = models.BooleanField(
        default=True,
        help_text=(
            "When false, hide scholarship scoring, ruleset editor, awards, "
            "and cohort exports (data is retained)."
        ),
    )
    document_version_history_enabled = models.BooleanField(
        default=True,
        help_text=(
            "Master switch for application-document version history UI/API. "
            "When false, no role sees prior file versions."
        ),
    )
    document_version_history_student = models.BooleanField(
        default=False,
        help_text="When history is enabled, students may see prior versions.",
    )
    document_version_history_coordinator = models.BooleanField(
        default=True,
        help_text="When history is enabled, coordinators may see prior versions.",
    )
    document_version_history_admin = models.BooleanField(
        default=True,
        help_text="When history is enabled, admins may see prior versions.",
    )

    class Meta:
        verbose_name = "Institution feature settings"
        verbose_name_plural = "Institution feature settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Singleton must not be deleted; reset to defaults instead.
        self.scholarships_enabled = True
        self.document_version_history_enabled = True
        self.document_version_history_student = False
        self.document_version_history_coordinator = True
        self.document_version_history_admin = True
        self.save(
            update_fields=[
                "scholarships_enabled",
                "document_version_history_enabled",
                "document_version_history_student",
                "document_version_history_coordinator",
                "document_version_history_admin",
                "updated_at",
            ]
        )

    def __str__(self):
        return "Institution feature settings"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @classmethod
    def scholarships_are_enabled(cls) -> bool:
        return bool(cls.get_solo().scholarships_enabled)
