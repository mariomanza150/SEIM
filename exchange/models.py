from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel, UUIDModel

# Statuses that count toward program seat capacity (excludes draft, rejected, cancelled, waitlist).
SEAT_HOLDING_APPLICATION_STATUS_NAMES = frozenset(
    {"submitted", "under_review", "approved", "completed"}
)


class Program(UUIDModel, TimeStampedModel):
    """Represents an exchange program (e.g., Erasmus, semester abroad)."""

    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    application_open_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Date when students can begin submitting new applications."),
    )
    application_deadline = models.DateField(
        null=True,
        blank=True,
        help_text=_("Last date students can create a new application for this program."),
    )
    is_active = models.BooleanField(default=True)
    min_gpa = models.FloatField(
        null=True, blank=True, help_text=_("Minimum GPA required for eligibility.")
    )
    required_language = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text=_("Required language for eligibility."),
    )
    min_language_level = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        choices=[
            ('A1', _('Beginner (A1)')),
            ('A2', _('Elementary (A2)')),
            ('B1', _('Intermediate (B1)')),
            ('B2', _('Upper Intermediate (B2)')),
            ('C1', _('Advanced (C1)')),
            ('C2', _('Proficient (C2)')),
        ],
        help_text=_("Minimum language proficiency level (CEFR scale).")
    )
    max_age = models.PositiveIntegerField(
        null=True, blank=True, help_text=_("Maximum age for eligibility.")
    )
    min_age = models.PositiveIntegerField(
        null=True, blank=True, help_text=_("Minimum age for eligibility.")
    )
    auto_reject_ineligible = models.BooleanField(
        default=False,
        help_text=_("Automatically reject applications that don't meet eligibility criteria.")
    )
    recurring = models.BooleanField(
        default=False, help_text=_("Is this program recurring (e.g., every semester)?")
    )
    # Link to dynamic form created via django-dynforms
    application_form = models.ForeignKey(
        'application_forms.FormType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("Dynamic application form for this program")
    )
    coordinators = models.ManyToManyField(
        "accounts.User",
        blank=True,
        related_name="coordinated_programs",
        help_text=_("Coordinators responsible for this program."),
    )
    required_document_types = models.ManyToManyField(
        "documents.DocumentType",
        blank=True,
        related_name="programs_requiring",
        help_text=_(
            "Applicants must upload these document types and have them marked valid before submitting."
        ),
    )
    enrollment_capacity = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_(
            "Maximum number of seat-holding applications (submitted / under review / approved / completed). "
            "Leave blank for no limit."
        ),
    )
    waitlist_when_full = models.BooleanField(
        default=True,
        help_text=_(
            "When capacity is full, new submissions are placed on the waitlist instead of being rejected."
        ),
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_application_window_status(self, on_date=None):
        today = on_date or timezone.localdate()

        if self.application_open_date and today < self.application_open_date:
            return {
                "is_open": False,
                "reason": "not_open_yet",
                "message": f"Applications open on {self.application_open_date:%B %d, %Y}.",
            }

        if self.application_deadline and today > self.application_deadline:
            return {
                "is_open": False,
                "reason": "closed",
                "message": f"Applications closed on {self.application_deadline:%B %d, %Y}.",
            }

        if self.application_open_date and self.application_deadline:
            return {
                "is_open": True,
                "reason": "open",
                "message": (
                    f"Applications are open from {self.application_open_date:%B %d, %Y} "
                    f"through {self.application_deadline:%B %d, %Y}."
                ),
            }

        if self.application_deadline:
            return {
                "is_open": True,
                "reason": "open",
                "message": f"Applications are open until {self.application_deadline:%B %d, %Y}.",
            }

        if self.application_open_date:
            return {
                "is_open": True,
                "reason": "open",
                "message": f"Applications opened on {self.application_open_date:%B %d, %Y}.",
            }

        return {
            "is_open": True,
            "reason": "always_open",
            "message": "Applications are currently open.",
        }

    def is_application_open(self, on_date=None):
        return self.get_application_window_status(on_date)["is_open"]

    @property
    def application_window_message(self):
        return self.get_application_window_status()["message"]

    @property
    def is_application_open_now(self):
        return self.is_application_open()

    def count_seat_holding_applications(self) -> int:
        return self.application_set.filter(
            withdrawn=False,
            status__name__in=SEAT_HOLDING_APPLICATION_STATUS_NAMES,
        ).count()

    def enrollment_slots_remaining(self) -> int | None:
        if self.enrollment_capacity is None:
            return None
        return max(0, self.enrollment_capacity - self.count_seat_holding_applications())

    def is_at_enrollment_capacity(self) -> bool:
        if self.enrollment_capacity is None:
            return False
        return self.count_seat_holding_applications() >= self.enrollment_capacity

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.end_date and self.start_date and self.end_date <= self.start_date:
            raise ValidationError({"end_date": "End date must be after start date."})

        if (
            self.application_open_date
            and self.application_deadline
            and self.application_deadline < self.application_open_date
        ):
            raise ValidationError({
                "application_deadline": "Application deadline must be on or after the application open date."
            })

        if self.application_open_date and self.application_open_date > self.start_date:
            raise ValidationError({
                "application_open_date": "Application open date must be on or before the program start date."
            })

        if self.application_deadline and self.application_deadline > self.start_date:
            raise ValidationError({
                "application_deadline": "Application deadline must be on or before the program start date."
            })


class ExchangeAgreement(UUIDModel, TimeStampedModel):
    """Operational exchange / cooperation agreement (distinct from CMS marketing convenio pages)."""

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        ACTIVE = "active", _("Active")
        SUSPENDED = "suspended", _("Suspended")
        EXPIRED = "expired", _("Expired")
        TERMINATED = "terminated", _("Terminated")
        RENEWAL_PENDING = "renewal_pending", _("Renewal pending")

    class AgreementType(models.TextChoices):
        BILATERAL = "bilateral", _("Bilateral")
        MULTILATERAL = "multilateral", _("Multilateral")
        ERASMUS = "erasmus", _("Erasmus+")
        SPECIFIC = "specific", _("Specific program")
        OTHER = "other", _("Other")

    title = models.CharField(
        max_length=255,
        help_text=_("Short title for staff (e.g. framework agreement name)."),
    )
    partner_institution_name = models.CharField(max_length=255)
    partner_country = models.CharField(max_length=120, blank=True, default="")
    partner_reference_id = models.CharField(
        max_length=120,
        blank=True,
        default="",
        help_text=_("Partner’s own agreement or contract reference, if any."),
    )
    internal_reference = models.CharField(
        max_length=64,
        blank=True,
        default="",
        db_index=True,
        help_text=_("Optional internal tracking code."),
    )
    agreement_type = models.CharField(
        max_length=32,
        choices=AgreementType.choices,
        default=AgreementType.BILATERAL,
    )
    programs = models.ManyToManyField(
        "Program",
        blank=True,
        related_name="exchange_agreements",
        help_text=_("Exchange programs governed or covered by this agreement."),
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Leave blank if no fixed end date."),
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    notes = models.TextField(blank=True, default="")
    renewed_from = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="renewal_successors",
        help_text=_("Prior agreement this record continues when created as a renewal successor."),
    )
    renewal_follow_up_due = models.DateField(
        null=True,
        blank=True,
        help_text=_("Optional staff deadline for renewal follow-up."),
    )

    class Meta:
        ordering = ["-start_date", "partner_institution_name", "title"]
        verbose_name = _("Exchange agreement")
        verbose_name_plural = _("Exchange agreements")
        indexes = [
            models.Index(fields=["status", "end_date"], name="exagreement_status_end_idx"),
        ]

    def __str__(self):
        return f"{self.title} — {self.partner_institution_name}"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": _("End date must be on or after the start date.")})

        if self.renewed_from_id and self.pk and self.renewed_from_id == self.pk:
            raise ValidationError({"renewed_from": _("An agreement cannot reference itself as predecessor.")})


class AgreementExpirationReminderLog(UUIDModel, TimeStampedModel):
    """Records that a given pre-expiry milestone was notified (prevents duplicate sends)."""

    agreement = models.ForeignKey(
        "ExchangeAgreement",
        on_delete=models.CASCADE,
        related_name="expiration_reminder_logs",
    )
    days_before = models.PositiveIntegerField()
    agreement_end_date = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["agreement", "days_before", "agreement_end_date"],
                name="uniq_agreement_expiry_reminder_milestone",
            )
        ]
        verbose_name = _("Agreement expiration reminder log")
        verbose_name_plural = _("Agreement expiration reminder logs")

    def __str__(self):
        return f"{self.agreement_id} @ {self.days_before}d before {self.agreement_end_date}"


class Application(UUIDModel, TimeStampedModel):
    """Student application for a program. No user logic here; delegates to accounts.User."""

    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    student = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    assigned_coordinator = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_applications",
        help_text=_("Coordinator explicitly assigned to review this application."),
    )
    status = models.ForeignKey("ApplicationStatus", on_delete=models.PROTECT)
    submitted_at = models.DateTimeField(null=True, blank=True)
    withdrawn = models.BooleanField(default=False)
    dynamic_form_current_step = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text=_(
            "Current step key when the program uses a multi-step application form "
            "(see FormType.step_definitions)."
        ),
    )

    class Meta:
        indexes = [
            models.Index(fields=['student', 'status'], name='app_student_status_idx'),
            models.Index(fields=['program', 'status'], name='app_program_status_idx'),
            models.Index(fields=['student', 'withdrawn'], name='app_student_withdrawn_idx'),
            models.Index(fields=['submitted_at'], name='app_submitted_idx'),
            models.Index(fields=['-created_at'], name='app_created_desc_idx'),
        ]
        ordering = ['-created_at']
        verbose_name = _('Application')
        verbose_name_plural = _('Applications')

    def __str__(self):
        return f"{self.student} - {self.program}"

    @property
    def effective_coordinator(self):
        if self.assigned_coordinator_id:
            return self.assigned_coordinator

        if hasattr(self.program, "coordinators"):
            program_coordinators = list(self.program.coordinators.all()[:2])
            if len(program_coordinators) == 1:
                return program_coordinators[0]

        return None


class ApplicationStatus(models.Model):
    """Status for application workflow (draft, submitted, under_review, etc.)."""

    name = models.CharField(max_length=50, unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class Comment(UUIDModel, TimeStampedModel):
    """Comments on applications, can be internal or visible to students."""

    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    text = models.TextField()
    is_private = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"Comment by {self.author} on {self.application}"


class TimelineEvent(UUIDModel, TimeStampedModel):
    """Tracks status changes and key events for an application."""

    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="timeline_events"
    )
    event_type = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True
    )

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.event_type} - {self.description}"


class SavedSearch(UUIDModel, TimeStampedModel):
    """Saved search filters for users (coordinators/admins)."""

    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name='saved_searches')
    name = models.CharField(max_length=100, help_text="Name for this saved search")
    search_type = models.CharField(
        max_length=20,
        choices=[
            ("program", "Program Search"),
            ("application", "Application Search"),
            ("exchange_agreement", "Exchange agreement registry"),
            ("document", "Application document list"),
            ("agreement_document", "Agreement document repository"),
            ("calendar", "Deadlines / calendar view"),
        ],
        help_text="Type of search (programs, applications, or staff list views)",
    )
    filters = models.JSONField(
        default=dict,
        help_text="JSON object containing filter parameters"
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Use this search as default for this user"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Saved Search'
        verbose_name_plural = 'Saved Searches'
        indexes = [
            models.Index(fields=['user', 'search_type'], name='savedsearch_user_type_idx'),
            models.Index(fields=['user', 'is_default'], name='savedsearch_user_default_idx'),
        ]

    def __str__(self):
        return f"{self.name} ({self.search_type}) - {self.user.username}"

    def save(self, *args, **kwargs):
        """Ensure only one default search per type per user."""
        if self.is_default:
            # Clear other defaults for this user and search type
            SavedSearch.objects.filter(
                user=self.user,
                search_type=self.search_type,
                is_default=True
            ).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)
