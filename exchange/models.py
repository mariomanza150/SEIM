from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel, UUIDModel

# Statuses that count toward program seat capacity (excludes draft, rejected, cancelled, waitlist).
SEAT_HOLDING_APPLICATION_STATUS_NAMES = frozenset(
    {"submitted", "under_review", "approved", "completed", "nominated"}
)

# Application statuses in which students may propose host course grades.
SUBJECT_GRADE_ELIGIBLE_STATUS_NAMES = frozenset(
    {"approved", "nominated", "completed"}
)

# Historic subject-plan snapshots kept per application (not counting the live set).
MAX_SUBJECT_PLAN_VERSIONS = 3


class EligibilityRuleSet(UUIDModel, TimeStampedModel):
    """
    Persisted eligibility ruleset.

    When a program links an active ruleset, ``ApplicationService.check_eligibility``
    applies ``rules_json.program_overrides`` on top of program scalar fields.

    ``schema_version`` is the *document* format version (see
    ``exchange.eligibility_ruleset_schema``), not the evaluation engine
    ``ELIGIBILITY_SCHEMA_VERSION``. ``content_revision`` increments whenever
    ``rules_json`` changes so staff can track overlay edits.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    schema_version = models.PositiveIntegerField(default=2)
    content_revision = models.PositiveIntegerField(
        default=1,
        help_text=_("Increments when rules_json changes (edit versioning)."),
    )
    rules_json = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name", "-created_at"]

    def __str__(self):
        return self.name


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
        help_text=_(
            "Last date students can create a new application for this program."
        ),
    )
    is_active = models.BooleanField(default=True)
    min_gpa = models.FloatField(
        null=True,
        blank=True,
        help_text=_(
            "Minimum GPA required for eligibility (4.0-normalized via student grade scale)."
        ),
    )
    min_semester = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Minimum academic semester required for eligibility."),
    )
    min_credits_approved_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Minimum percentage of approved credits required (0–100)."),
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
            ("A1", _("Beginner (A1)")),
            ("A2", _("Elementary (A2)")),
            ("B1", _("Intermediate (B1)")),
            ("B2", _("Upper Intermediate (B2)")),
            ("C1", _("Advanced (C1)")),
            ("C2", _("Proficient (C2)")),
        ],
        help_text=_("Minimum language proficiency level (CEFR scale)."),
    )
    min_toefl_score = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Minimum TOEFL score required for eligibility (when set)."),
    )
    max_age = models.PositiveIntegerField(
        null=True, blank=True, help_text=_("Maximum age for eligibility.")
    )
    min_age = models.PositiveIntegerField(
        null=True, blank=True, help_text=_("Minimum age for eligibility.")
    )
    auto_reject_ineligible = models.BooleanField(
        default=False,
        help_text=_(
            "Automatically reject applications that don't meet eligibility criteria."
        ),
    )
    recurring = models.BooleanField(
        default=False, help_text=_("Is this program recurring (e.g., every semester)?")
    )
    # Link to dynamic form created via django-dynforms
    application_form = models.ForeignKey(
        "application_forms.FormType",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("Dynamic application form for this program"),
    )
    workflow_version = models.ForeignKey(
        "workflows.WorkflowVersion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="programs",
        help_text=_(
            "Published workflow version governing application behavior for this program."
        ),
    )
    coordinators = models.ManyToManyField(
        "accounts.User",
        blank=True,
        related_name="coordinated_programs",
        help_text=_("Coordinators responsible for this program."),
    )
    required_document_types = models.ManyToManyField(
        "documents.DocumentType",
        through="ProgramDocumentRequirement",
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
    eligibility_ruleset = models.ForeignKey(
        "exchange.EligibilityRuleSet",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="programs",
        help_text=_(
            "Optional: persisted eligibility rule set used for previews/validation when enabled. "
            "When unset, eligibility rules are derived from program fields."
        ),
    )

    class Meta:
        ordering = ["name"]

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

    def document_requirements(self):
        """Ordered program–document requirements (through model)."""
        return self.program_document_requirements.select_related("document_type").all()

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.end_date and self.start_date and self.end_date <= self.start_date:
            raise ValidationError({"end_date": "End date must be after start date."})

        if (
            self.application_open_date
            and self.application_deadline
            and self.application_deadline < self.application_open_date
        ):
            raise ValidationError(
                {
                    "application_deadline": "Application deadline must be on or after the application open date."
                }
            )

        if self.application_open_date and self.application_open_date > self.start_date:
            raise ValidationError(
                {
                    "application_open_date": "Application open date must be on or before the program start date."
                }
            )

        if self.application_deadline and self.application_deadline > self.start_date:
            raise ValidationError(
                {
                    "application_deadline": "Application deadline must be on or before the program start date."
                }
            )


class HostInstitution(UUIDModel, TimeStampedModel):
    """Host university belonging to a mobility scheme (Program)."""

    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name="host_institutions",
        help_text=_("Mobility scheme this host university belongs to."),
    )
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=120, blank=True, default="")
    is_active = models.BooleanField(default=True)
    grade_scale = models.ForeignKey(
        "grades.GradeScale",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="host_institutions",
        help_text=_(
            "Host university grading scale used for subject grade dropdowns "
            "and course-level translation."
        ),
    )

    class Meta:
        ordering = ["name"]
        verbose_name = _("Host institution")
        verbose_name_plural = _("Host institutions")
        constraints = [
            models.UniqueConstraint(
                fields=["program", "name"],
                name="uniq_host_institution_program_name",
            )
        ]

    def __str__(self):
        return self.name


class HostSchool(UUIDModel, TimeStampedModel):
    """Faculty / school under a host institution."""

    institution = models.ForeignKey(
        HostInstitution,
        on_delete=models.CASCADE,
        related_name="schools",
    )
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Host school")
        verbose_name_plural = _("Host schools")
        constraints = [
            models.UniqueConstraint(
                fields=["institution", "name"],
                name="uniq_host_school_institution_name",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.institution})"


class HostAcademicProgram(UUIDModel, TimeStampedModel):
    """Academic program under a host school."""

    school = models.ForeignKey(
        HostSchool,
        on_delete=models.CASCADE,
        related_name="academic_programs",
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=64, blank=True, default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Host academic program")
        verbose_name_plural = _("Host academic programs")
        constraints = [
            models.UniqueConstraint(
                fields=["school", "name"],
                name="uniq_host_academic_program_school_name",
            )
        ]

    def __str__(self):
        return self.name


class HostSubject(UUIDModel, TimeStampedModel):
    """Optional subject / course catalog entry hanging off a host university.

    School and academic program are optional: subjects may be institution-level,
    school-level, or program-level.
    """

    institution = models.ForeignKey(
        HostInstitution,
        on_delete=models.CASCADE,
        related_name="subjects",
        help_text=_("Host university this subject belongs to."),
    )
    school = models.ForeignKey(
        HostSchool,
        on_delete=models.CASCADE,
        related_name="subjects",
        null=True,
        blank=True,
        help_text=_("Optional faculty / school. Must belong to the institution."),
    )
    academic_program = models.ForeignKey(
        HostAcademicProgram,
        on_delete=models.CASCADE,
        related_name="subjects",
        null=True,
        blank=True,
        help_text=_("Optional academic program. Must belong to the school."),
    )
    code = models.CharField(max_length=64, blank=True, default="")
    name = models.CharField(max_length=255)
    credits = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Credit value at the host institution (optional)."),
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name", "code"]
        verbose_name = _("Host subject")
        verbose_name_plural = _("Host subjects")
        constraints = [
            models.UniqueConstraint(
                fields=["institution", "name", "code"],
                name="uniq_host_subject_institution_name_code",
            )
        ]

    def __str__(self):
        if self.code:
            return f"{self.code} — {self.name}"
        return self.name

    def clean(self):
        from django.core.exceptions import ValidationError

        errors = {}
        school = self.school if self.school_id else None
        academic = self.academic_program if self.academic_program_id else None

        if school is not None and self.institution_id:
            if school.institution_id != self.institution_id:
                errors["school"] = _(
                    "Host school must belong to the selected host institution."
                )

        if academic is not None:
            if self.school_id is None:
                self.school_id = academic.school_id
                school = academic.school
            elif academic.school_id != self.school_id:
                errors["academic_program"] = _(
                    "Host academic program must belong to the selected host school."
                )
            if self.institution_id and academic.school.institution_id != self.institution_id:
                errors["academic_program"] = _(
                    "Host academic program must belong to the selected host institution."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.academic_program_id:
            academic = self.academic_program
            if not self.school_id:
                self.school_id = academic.school_id
            if not self.institution_id:
                self.institution_id = academic.school.institution_id
        elif self.school_id and not self.institution_id:
            self.institution_id = self.school.institution_id
        super().save(*args, **kwargs)


class ProgramDocumentRequirement(models.Model):
    """Per-program document checklist configuration (through model for required_document_types)."""

    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name="program_document_requirements",
    )
    document_type = models.ForeignKey(
        "documents.DocumentType",
        on_delete=models.CASCADE,
        related_name="program_requirements",
    )
    is_required = models.BooleanField(
        default=True,
        help_text=_(
            "When false, shown on checklist but optional throughout. "
            "When true with required_from_status unset, required from submitted."
        ),
    )
    required_from_status = models.ForeignKey(
        "ApplicationStatus",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="gated_document_requirements",
        help_text=_(
            "Pipeline status from which this document is required for students. "
            "Ignored when is_required is false. Null with is_required means submitted."
        ),
    )
    deadline = models.DateField(
        null=True,
        blank=True,
        help_text=_("Absolute upload deadline for this document type."),
    )
    deadline_days_before_program_deadline = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_(
            "Relative deadline: N days before the program application_deadline."
        ),
    )
    deadline_days_after_program_start = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_(
            "Relative deadline: N days after the program start_date "
            "(e.g. arrival certificates due after mobility begins)."
        ),
    )
    instructions_override = models.TextField(
        blank=True,
        default="",
        help_text=_("Optional per-program override of DocumentType.instructions."),
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = _("Program document requirement")
        verbose_name_plural = _("Program document requirements")
        constraints = [
            models.UniqueConstraint(
                fields=["program", "document_type"],
                name="uniq_program_document_requirement",
            )
        ]

    def __str__(self):
        return f"{self.program} → {self.document_type}"

    def resolve_deadline(self):
        """Return effective deadline date, or None if unset.

        Precedence: absolute ``deadline``, then days after program start,
        then days before the program application deadline.
        """
        from datetime import timedelta

        if self.deadline:
            return self.deadline
        after_start = self.deadline_days_after_program_start
        if after_start is not None and self.program.start_date:
            return self.program.start_date + timedelta(days=after_start)
        days = self.deadline_days_before_program_deadline
        if days is not None and self.program.application_deadline:
            return self.program.application_deadline - timedelta(days=days)
        return None

    def is_overdue(self, on_date=None) -> bool:
        effective = self.resolve_deadline()
        if not effective:
            return False
        today = on_date or timezone.localdate()
        return today > effective

    def clean(self):
        from django.core.exceptions import ValidationError

        super().clean()
        if not self.is_required:
            return
        name = getattr(self.required_from_status, "name", None)
        if name == "draft":
            raise ValidationError(
                {
                    "required_from_status": _(
                        "Documents cannot be required at draft; the earliest gate is submitted."
                    )
                }
            )


class ProgramFieldRequirement(models.Model):
    """When a profile, application, or dynamic-form field becomes required."""

    class Source(models.TextChoices):
        PROFILE = "profile", _("Profile")
        APPLICATION = "application", _("Application")
        FORM = "form", _("Form")

    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name="field_requirements",
    )
    source = models.CharField(max_length=20, choices=Source.choices)
    field_key = models.CharField(max_length=100)
    required_from_status = models.ForeignKey(
        "ApplicationStatus",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="program_field_requirements",
        help_text=_(
            "Pipeline status from which this field is required. "
            "Null means optional throughout."
        ),
    )

    class Meta:
        ordering = ["source", "field_key", "id"]
        verbose_name = _("Program field requirement")
        verbose_name_plural = _("Program field requirements")
        constraints = [
            models.UniqueConstraint(
                fields=["program", "source", "field_key"],
                name="uniq_program_field_requirement",
            )
        ]

    def __str__(self):
        return f"{self.program} → {self.source}:{self.field_key}"

    def clean(self):
        from django.core.exceptions import ValidationError

        from exchange.lifecycle_requirements import allowed_field_keys

        super().clean()
        allowed = allowed_field_keys(self.source)
        key = (self.field_key or "").strip()
        if not key:
            raise ValidationError({"field_key": _("Field key is required.")})
        self.field_key = key
        if allowed is not None and key not in allowed:
            raise ValidationError(
                {"field_key": _("Unknown field key for this source.")}
            )
        if self.source == self.Source.FORM and not key:
            raise ValidationError({"field_key": _("Form field key is required.")})


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
    required_gpa = models.FloatField(
        null=True, blank=True, help_text=_("Minimum GPA required for the agreement.")
    )
    language_requirements = models.JSONField(
        default=list,
        blank=True,
        help_text=_(
            "List of required languages and levels, e.g., [{'lang': 'French', 'level': 'B2'}]"
        ),
    )
    custom_tags = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Custom tags restricted to 'Foreign Language' or 'Habla Hispana'."),
    )
    application_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Maximum number of applications permitted under this agreement."),
    )
    notify_on_limit_reached = models.BooleanField(
        default=True,
        help_text=_("If true, an alert is sent when the application limit is reached."),
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
        help_text=_(
            "Prior agreement this record continues when created as a renewal successor."
        ),
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
            models.Index(
                fields=["status", "end_date"], name="exagreement_status_end_idx"
            ),
        ]

    def __str__(self):
        return f"{self.title} — {self.partner_institution_name}"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError(
                {"end_date": _("End date must be on or after the start date.")}
            )

        if self.renewed_from_id and self.pk and self.renewed_from_id == self.pk:
            raise ValidationError(
                {
                    "renewed_from": _(
                        "An agreement cannot reference itself as predecessor."
                    )
                }
            )


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
    # Apply-time eligibility snapshot (profile edits must not rewrite history).
    semester_at_apply = models.PositiveIntegerField(null=True, blank=True)
    gpa_at_apply = models.FloatField(null=True, blank=True)
    grade_scale_at_apply = models.ForeignKey(
        "grades.GradeScale",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="applications_at_apply",
    )
    credits_percent_at_apply = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    language_at_apply = models.CharField(max_length=64, null=True, blank=True)
    language_level_at_apply = models.CharField(max_length=10, null=True, blank=True)
    additional_languages_at_apply = models.JSONField(default=list, blank=True)
    nomination_rank = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_(
            "Staff ranking for nomination matching (lower is higher priority)."
        ),
    )
    nomination_cycle = models.ForeignKey(
        "NominationCycle",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="applications",
        help_text=_("Nomination cycle that produced the current nominated/waitlist status."),
    )
    partner_nomination_acknowledged_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When a partner contact acknowledged this nomination."),
    )
    # Host destination hierarchy (required before submit).
    host_institution = models.ForeignKey(
        "HostInstitution",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="applications",
        help_text=_("Selected host university for this application."),
    )
    host_school = models.ForeignKey(
        "HostSchool",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="applications",
        help_text=_("Selected host school / faculty."),
    )
    host_academic_program = models.ForeignKey(
        "HostAcademicProgram",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="applications",
        help_text=_("Selected host academic program."),
    )

    class Meta:
        indexes = [
            models.Index(fields=["student", "status"], name="app_student_status_idx"),
            models.Index(fields=["program", "status"], name="app_program_status_idx"),
            models.Index(
                fields=["student", "withdrawn"], name="app_student_withdrawn_idx"
            ),
            models.Index(fields=["submitted_at"], name="app_submitted_idx"),
            models.Index(fields=["-created_at"], name="app_created_desc_idx"),
        ]
        ordering = ["-created_at"]
        verbose_name = _("Application")
        verbose_name_plural = _("Applications")

    def __str__(self):
        return f"{self.student} - {self.program}"

    def clean(self):
        from django.core.exceptions import ValidationError

        errors = validate_application_host_destination(self, require_complete=False)
        if errors:
            raise ValidationError(errors)

    @property
    def effective_coordinator(self):
        if self.assigned_coordinator_id:
            return self.assigned_coordinator

        if hasattr(self.program, "coordinators"):
            program_coordinators = list(self.program.coordinators.all()[:2])
            if len(program_coordinators) == 1:
                return program_coordinators[0]

        return None


class ApplicationSubjectSelection(UUIDModel, TimeStampedModel):
    """
    Optional mapping of a host subject (catalog or custom) to a home course.

    Not required for application submit. Students propose host grades after
    approval; coordinators confirm to lock a translated home grade.
    """

    class GradeStatus(models.TextChoices):
        NONE = "none", _("None")
        PROPOSED = "proposed", _("Proposed")
        CONFIRMED = "confirmed", _("Confirmed")
        REJECTED = "rejected", _("Rejected")

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="subject_selections",
    )
    host_subject = models.ForeignKey(
        HostSubject,
        on_delete=models.PROTECT,
        related_name="application_selections",
        null=True,
        blank=True,
        help_text=_("Catalog host subject. Mutually exclusive with custom course fields."),
    )
    custom_code = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text=_("Unlisted host course code (when not using the catalog)."),
    )
    custom_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=_("Unlisted host course name (required when not using the catalog)."),
    )
    custom_credits = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Unlisted host course credits."),
    )
    home_course_label = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=_("Optional label of the corresponding home institution course."),
    )
    home_course_code = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text=_("Optional code of the corresponding home institution course."),
    )
    credits = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_(
            "Credits used for homologación (defaults to host subject or custom credits)."
        ),
    )
    notes = models.TextField(blank=True, default="")
    proposed_host_grade = models.ForeignKey(
        "grades.GradeValue",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="proposed_subject_selections",
        help_text=_("Host grade proposed by the student."),
    )
    confirmed_host_grade = models.ForeignKey(
        "grades.GradeValue",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="confirmed_subject_selections",
        help_text=_("Host grade locked after coordinator confirmation."),
    )
    home_grade = models.ForeignKey(
        "grades.GradeValue",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="home_subject_selections",
        help_text=_("Translated home-scale grade written at confirmation."),
    )
    grade_status = models.CharField(
        max_length=16,
        choices=GradeStatus.choices,
        default=GradeStatus.NONE,
    )
    proposed_at = models.DateTimeField(null=True, blank=True)
    proposed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="proposed_subject_grades",
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)
    confirmed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="confirmed_subject_grades",
    )
    confirmation_notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("Application subject selection")
        verbose_name_plural = _("Application subject selections")
        constraints = [
            models.UniqueConstraint(
                fields=["application", "host_subject"],
                condition=models.Q(host_subject__isnull=False),
                name="uniq_application_host_subject_selection",
            ),
            models.CheckConstraint(
                condition=(
                    (
                        models.Q(host_subject__isnull=False)
                        & models.Q(custom_name="")
                        & models.Q(custom_code="")
                        & models.Q(custom_credits__isnull=True)
                    )
                    | (
                        models.Q(host_subject__isnull=True)
                        & ~models.Q(custom_name="")
                    )
                ),
                name="application_subject_catalog_xor_custom",
            ),
        ]

    def __str__(self):
        return f"{self.application_id}: {self.host_course_display}"

    @property
    def host_course_code(self):
        if self.host_subject_id:
            return self.host_subject.code
        return self.custom_code

    @property
    def host_course_name(self):
        if self.host_subject_id:
            return self.host_subject.name
        return self.custom_name

    @property
    def host_course_display(self):
        code = self.host_course_code
        name = self.host_course_name
        if code:
            return f"{code} — {name}"
        return name or "—"

    def clean(self):
        from django.core.exceptions import ValidationError

        errors = {}
        has_catalog = bool(self.host_subject_id)
        custom_name = (self.custom_name or "").strip()
        custom_code = (self.custom_code or "").strip()
        has_custom = bool(
            custom_name or custom_code or self.custom_credits is not None
        )

        if has_catalog and has_custom:
            errors["host_subject"] = _(
                "Choose a catalog subject or a custom host course, not both."
            )
        elif not has_catalog and not custom_name:
            errors["custom_name"] = _(
                "Provide a custom course name or select a catalog subject."
            )

        if has_catalog and self.application_id:
            app = self.application
            subj = self.host_subject
            if subj.institution_id != app.host_institution_id:
                errors["host_subject"] = _(
                    "Host subject must belong to the application's host institution."
                )
            elif subj.school_id and subj.school_id != app.host_school_id:
                errors["host_subject"] = _(
                    "Host subject is not available for this destination."
                )
            elif (
                subj.academic_program_id
                and subj.academic_program_id != app.host_academic_program_id
            ):
                errors["host_subject"] = _(
                    "Host subject is not available for this destination."
                )
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.credits is None:
            if self.host_subject_id:
                self.credits = self.host_subject.credits
            elif self.custom_credits is not None:
                self.credits = self.custom_credits
        super().save(*args, **kwargs)


class ApplicationSubjectPlanVersion(UUIDModel, TimeStampedModel):
    """
    Historic snapshot of an application's full subject selection set.

    Live study-plan rows stay on ``ApplicationSubjectSelection``. Each row
    here stores a JSON list of selection dicts (catalog or custom course,
    home mapping, credits, notes, and grade fields as of snapshot time).
    At most ``MAX_SUBJECT_PLAN_VERSIONS`` historic rows are kept per
    application; see ``exchange.subject_plan_versions``.
    """

    class Trigger(models.TextChoices):
        MAPPING_CHANGED = "mapping_changed", _("Mapping changed")
        GRADES_PROPOSED = "grades_proposed", _("Grades proposed")
        GRADES_CONFIRMED = "grades_confirmed", _("Grades confirmed")
        GRADES_REJECTED = "grades_rejected", _("Grades rejected")

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="subject_plan_versions",
    )
    version_number = models.PositiveIntegerField()
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subject_plan_versions_created",
    )
    trigger = models.CharField(
        max_length=32,
        choices=Trigger.choices,
        default=Trigger.MAPPING_CHANGED,
    )
    payload = models.JSONField(
        default=list,
        help_text=_(
            "JSON list of subject-selection dicts captured at snapshot time."
        ),
    )

    class Meta:
        ordering = ["-version_number"]
        verbose_name = _("Application subject plan version")
        verbose_name_plural = _("Application subject plan versions")
        constraints = [
            models.UniqueConstraint(
                fields=["application", "version_number"],
                name="uniq_application_subject_plan_version_number",
            ),
        ]
        indexes = [
            models.Index(
                fields=["application", "-version_number"],
                name="subj_plan_ver_app_num_idx",
            ),
        ]

    def __str__(self):
        return f"{self.application_id} v{self.version_number}"


def program_requires_host_destination(program) -> bool:
    """True when the mobility scheme has at least one active host university."""
    if program is None:
        return False
    cached = getattr(program, "_prefetched_objects_cache", None)
    if cached is not None and "host_institutions" in cached:
        return any(inst.is_active for inst in program.host_institutions.all())
    return program.host_institutions.filter(is_active=True).exists()


def _program_for_host_validation(application):
    program = getattr(application, "program", None)
    if program is not None:
        return program
    program_id = getattr(application, "program_id", None)
    if not program_id:
        return None
    return Program.objects.filter(pk=program_id).first()


def validate_application_host_destination(application, *, require_complete=False):
    """
    Validate host destination FK cascade consistency.

    Returns a dict of field -> error messages (empty if valid).
    When ``require_complete`` is True, require only the host levels that are
    configured on the scheme (no institutions → host destination is optional).
    """
    errors = {}
    institution = application.host_institution
    school = application.host_school
    academic = application.host_academic_program
    program_id = application.program_id

    if require_complete:
        program = _program_for_host_validation(application)
        if program_requires_host_destination(program):
            if not application.host_institution_id:
                errors["host_institution"] = _(
                    "Select a host university before submitting."
                )
            else:
                has_schools = HostSchool.objects.filter(
                    institution_id=application.host_institution_id,
                    is_active=True,
                ).exists()
                if has_schools:
                    if not application.host_school_id:
                        errors["host_school"] = _(
                            "Select a host school before submitting."
                        )
                    else:
                        has_programs = HostAcademicProgram.objects.filter(
                            school_id=application.host_school_id,
                            is_active=True,
                        ).exists()
                        if (
                            has_programs
                            and not application.host_academic_program_id
                        ):
                            errors["host_academic_program"] = _(
                                "Select a host academic program before submitting."
                            )

    if application.host_institution_id and institution is not None:
        if program_id and institution.program_id != program_id:
            errors["host_institution"] = _(
                "Host institution must belong to the selected mobility scheme."
            )

    if application.host_school_id:
        if not application.host_institution_id:
            errors["host_school"] = _(
                "Select a host institution before choosing a school."
            )
        elif (
            school is not None
            and school.institution_id != application.host_institution_id
        ):
            errors["host_school"] = _(
                "Host school must belong to the selected host institution."
            )

    if application.host_academic_program_id:
        if not application.host_school_id:
            errors["host_academic_program"] = _(
                "Select a host school before choosing an academic program."
            )
        elif academic is not None and academic.school_id != application.host_school_id:
            errors["host_academic_program"] = _(
                "Host academic program must belong to the selected host school."
            )

    return errors


def visible_host_subjects_queryset(
    *,
    institution_id,
    school_id=None,
    academic_program_id=None,
    include_inactive=False,
):
    """
    Subjects visible for a destination: institution-level always, plus
    school-level and program-level when those FKs are set.
    """
    if not institution_id:
        return HostSubject.objects.none()

    q = models.Q(
        institution_id=institution_id,
        school__isnull=True,
        academic_program__isnull=True,
    )
    if school_id:
        q |= models.Q(
            institution_id=institution_id,
            school_id=school_id,
            academic_program__isnull=True,
        )
    if academic_program_id:
        q |= models.Q(
            institution_id=institution_id,
            academic_program_id=academic_program_id,
        )
    qs = HostSubject.objects.filter(q)
    if not include_inactive:
        qs = qs.filter(is_active=True)
    return qs.select_related(
        "institution", "school", "academic_program"
    ).order_by("name", "code")


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

    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="saved_searches"
    )
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
            ("analytics_forecast", "Analytics forecasts"),
        ],
        help_text="Type of search (programs, applications, or staff list views)",
    )
    filters = models.JSONField(
        default=dict, help_text="JSON object containing filter parameters"
    )
    is_default = models.BooleanField(
        default=False, help_text="Use this search as default for this user"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Saved Search"
        verbose_name_plural = "Saved Searches"
        indexes = [
            models.Index(
                fields=["user", "search_type"], name="savedsearch_user_type_idx"
            ),
            models.Index(
                fields=["user", "is_default"], name="savedsearch_user_default_idx"
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.search_type}) - {self.user.username}"

    def save(self, *args, **kwargs):
        """Ensure only one default search per type per user."""
        if self.is_default:
            # Clear other defaults for this user and search type
            SavedSearch.objects.filter(
                user=self.user, search_type=self.search_type, is_default=True
            ).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)


class ScholarshipAward(UUIDModel, TimeStampedModel):
    """Staff scholarship award decision attached to one application."""

    class Status(models.TextChoices):
        NOMINATED = "nominated", _("Nominated")
        AWARDED = "awarded", _("Awarded")
        DECLINED = "declined", _("Declined")
        DISBURSING = "disbursing", _("Disbursing")
        DISBURSED = "disbursed", _("Disbursed")
        WITHDRAWN = "withdrawn", _("Withdrawn")

    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name="scholarship_award",
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.NOMINATED,
        db_index=True,
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=8, default="MXN")
    notes = models.TextField(blank=True, default="")
    decided_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scholarship_awards_decided",
    )
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = _("Scholarship award")
        verbose_name_plural = _("Scholarship awards")

    def __str__(self):
        return f"{self.application_id} — {self.status}"


class ScholarshipDisbursement(UUIDModel, TimeStampedModel):
    """A scheduled or completed disbursement milestone on a scholarship award."""

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        PAID = "paid", _("Paid")
        SKIPPED = "skipped", _("Skipped")

    award = models.ForeignKey(
        ScholarshipAward,
        on_delete=models.CASCADE,
        related_name="disbursements",
    )
    label = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "due_date", "created_at"]
        verbose_name = _("Scholarship disbursement")
        verbose_name_plural = _("Scholarship disbursements")

    def __str__(self):
        return f"{self.label} ({self.status})"


class PartnerContact(UUIDModel, TimeStampedModel):
    """Links a partner-institution user to an operational exchange agreement."""

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="partner_contacts",
    )
    agreement = models.ForeignKey(
        ExchangeAgreement,
        on_delete=models.CASCADE,
        related_name="partner_contacts",
    )
    title = models.CharField(max_length=120, blank=True, default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Partner contact")
        verbose_name_plural = _("Partner contacts")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "agreement"],
                name="uniq_partner_contact_user_agreement",
            )
        ]

    def __str__(self):
        return f"{self.user_id} @ {self.agreement_id}"


class AgreementComment(UUIDModel, TimeStampedModel):
    """Comments on an exchange agreement (staff notes or partner-visible thread)."""

    agreement = models.ForeignKey(
        ExchangeAgreement,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    text = models.TextField()
    is_private = models.BooleanField(
        default=False,
        help_text="Private staff notes are hidden from partner portal users.",
    )

    class Meta:
        ordering = ["created_at", "id"]
        indexes = [
            models.Index(
                fields=["agreement", "created_at"],
                name="agcomment_agr_created_idx",
            ),
        ]

    def __str__(self):
        return f"Comment by {self.author} on {self.agreement}"


class NominationCycle(UUIDModel, TimeStampedModel):
    """Named nomination window for a program (multi-cycle matching)."""

    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name="nomination_cycles",
    )
    name = models.CharField(max_length=120)
    opens_at = models.DateField(null=True, blank=True)
    closes_at = models.DateField(null=True, blank=True)
    seat_quota = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_(
            "Optional Match slot override for this cycle. When set, Match uses this "
            "quota instead of program.enrollment_capacity."
        ),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("At most one active cycle should be used for Match at a time."),
    )

    class Meta:
        ordering = ["-opens_at", "-created_at"]
        verbose_name = _("Nomination cycle")
        verbose_name_plural = _("Nomination cycles")
        constraints = [
            models.UniqueConstraint(
                fields=["program", "name"],
                name="uniq_nomination_cycle_program_name",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.program_id})"

    def is_open_on(self, on_date=None) -> bool:
        from django.utils import timezone as dj_tz

        day = on_date or dj_tz.localdate()
        if self.opens_at and day < self.opens_at:
            return False
        if self.closes_at and day > self.closes_at:
            return False
        return True


class NominationPartnerAllocation(UUIDModel, TimeStampedModel):
    """Per-partner seat allocation within a nomination cycle."""

    cycle = models.ForeignKey(
        NominationCycle,
        on_delete=models.CASCADE,
        related_name="partner_allocations",
    )
    agreement = models.ForeignKey(
        ExchangeAgreement,
        on_delete=models.CASCADE,
        related_name="nomination_allocations",
    )
    seat_quota = models.PositiveIntegerField(
        help_text=_("Seats reserved for this partner under the cycle."),
    )

    class Meta:
        ordering = ["agreement__partner_institution_name", "created_at"]
        verbose_name = _("Nomination partner allocation")
        verbose_name_plural = _("Nomination partner allocations")
        constraints = [
            models.UniqueConstraint(
                fields=["cycle", "agreement"],
                name="uniq_nomination_partner_alloc_cycle_agreement",
            )
        ]

    def __str__(self):
        return f"{self.agreement_id} @ {self.cycle_id}: {self.seat_quota}"
