from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel, UUIDModel

# Statuses that count toward program seat capacity (excludes draft, rejected, cancelled, waitlist).
SEAT_HOLDING_APPLICATION_STATUS_NAMES = frozenset(
    {"submitted", "under_review", "approved", "completed", "nominated"}
)


class EligibilityRuleSet(UUIDModel, TimeStampedModel):
    """
    Persisted eligibility ruleset.

    When a program links an active ruleset, ``ApplicationService.check_eligibility``
    applies ``rules_json.program_overrides`` on top of program scalar fields.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    schema_version = models.PositiveIntegerField(default=1)
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
    """Optional subject / course catalog entry under a host academic program."""

    academic_program = models.ForeignKey(
        HostAcademicProgram,
        on_delete=models.CASCADE,
        related_name="subjects",
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
                fields=["academic_program", "name", "code"],
                name="uniq_host_subject_program_name_code",
            )
        ]

    def __str__(self):
        if self.code:
            return f"{self.code} — {self.name}"
        return self.name


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
        help_text=_("When false, shown on checklist but not required for submit."),
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
        """Return effective deadline date, or None if unset."""
        if self.deadline:
            return self.deadline
        days = self.deadline_days_before_program_deadline
        if days is not None and self.program.application_deadline:
            from datetime import timedelta

            return self.program.application_deadline - timedelta(days=days)
        return None

    def is_overdue(self, on_date=None) -> bool:
        effective = self.resolve_deadline()
        if not effective:
            return False
        today = on_date or timezone.localdate()
        return today > effective


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
    Optional mapping of a host subject to a home course for homologación.

    Not required for application submit.
    """

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="subject_selections",
    )
    host_subject = models.ForeignKey(
        HostSubject,
        on_delete=models.PROTECT,
        related_name="application_selections",
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
            "Credits used for homologación (defaults to host subject credits)."
        ),
    )
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("Application subject selection")
        verbose_name_plural = _("Application subject selections")
        constraints = [
            models.UniqueConstraint(
                fields=["application", "host_subject"],
                name="uniq_application_host_subject_selection",
            )
        ]

    def __str__(self):
        return f"{self.application_id}: {self.host_subject}"

    def clean(self):
        from django.core.exceptions import ValidationError

        errors = {}
        if self.host_subject_id and self.application_id:
            app_prog_id = self.application.host_academic_program_id
            subj_prog_id = self.host_subject.academic_program_id
            if app_prog_id and subj_prog_id != app_prog_id:
                errors["host_subject"] = _(
                    "Host subject must belong to the application's host academic program."
                )
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.credits is None and self.host_subject_id:
            self.credits = self.host_subject.credits
        super().save(*args, **kwargs)


def validate_application_host_destination(application, *, require_complete=False):
    """
    Validate host destination FK cascade consistency.

    Returns a dict of field -> error messages (empty if valid).
    When ``require_complete`` is True, all three host FKs must be set.
    """
    errors = {}
    institution = application.host_institution
    school = application.host_school
    academic = application.host_academic_program
    program_id = application.program_id

    if require_complete:
        if not application.host_institution_id:
            errors["host_institution"] = _(
                "Select a host university before submitting."
            )
        if not application.host_school_id:
            errors["host_school"] = _("Select a host school before submitting.")
        if not application.host_academic_program_id:
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
