from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel, UUIDModel


class FileTypeFamily(models.Model):
    """Umbrella upload group (Image, Word, PDF) mapped to concrete extensions."""

    slug = models.SlugField(max_length=40, unique=True)
    name = models.CharField(max_length=80)
    aliases = models.CharField(
        max_length=240,
        blank=True,
        default="",
        help_text=_("Search synonyms, comma-separated."),
    )
    extensions = models.CharField(
        max_length=240,
        help_text=_("Comma-separated extensions without dots (e.g. jpg,jpeg,png)."),
    )
    sort_order = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = _("File type family")
        verbose_name_plural = _("File type families")

    def __str__(self):
        return self.name

    def parsed_extensions(self) -> list[str]:
        return [
            ext.strip().lower().lstrip(".")
            for ext in (self.extensions or "").split(",")
            if ext.strip()
        ]

    def parsed_aliases(self) -> list[str]:
        return [
            alias.strip()
            for alias in (self.aliases or "").split(",")
            if alias.strip()
        ]


class DocumentType(models.Model):
    """Types of documents (e.g., transcript, ID, recommendation letter)."""

    class SubmissionMode(models.TextChoices):
        UPLOAD = "upload", _("Upload")
        TEMPLATE_DOWNLOAD = "template_download", _("Template download")
        SYSTEM_GENERATED = "system_generated", _("System generated")
        INSTRUCTIONS_ONLY = "instructions_only", _("Instructions only")

    class VersionHistoryVisibility(models.TextChoices):
        INHERIT = "inherit", _("Inherit institution defaults")
        HIDDEN = "hidden", _("Hidden for all roles")
        CUSTOM = "custom", _("Custom per-role overrides")

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(
        max_length=80,
        unique=True,
        null=True,
        blank=True,
        help_text=_("Stable key (e.g. solicitud_participacion)."),
    )
    description = models.TextField(blank=True)
    submission_mode = models.CharField(
        max_length=32,
        choices=SubmissionMode.choices,
        default=SubmissionMode.UPLOAD,
        db_index=True,
    )
    template_file = models.FileField(
        upload_to="document_templates/",
        blank=True,
        null=True,
        help_text=_("Downloadable blank template for students."),
    )
    instructions = models.TextField(
        blank=True,
        default="",
        help_text=_("Student-facing instructions / FAQ body."),
    )
    faq = models.TextField(
        blank=True,
        default="",
        help_text=_("Optional FAQ / tips shown alongside instructions."),
    )
    accepted_extensions = models.CharField(
        max_length=120,
        blank=True,
        default="",
        help_text=_(
            "Extra extensions beyond selected families, comma-separated without dots. "
            "Empty with no families = global defaults."
        ),
    )
    file_type_families = models.ManyToManyField(
        FileTypeFamily,
        blank=True,
        related_name="document_types",
        help_text=_("Umbrella file groups (Image, Word, PDF, …)."),
    )
    max_file_size_mb = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Per-type size cap in MB. Empty = global default."),
    )
    allows_multiple = models.BooleanField(
        default=False,
        help_text=_("Allow more than one upload of this type per application."),
    )
    version_history_visibility = models.CharField(
        max_length=16,
        choices=VersionHistoryVisibility.choices,
        default=VersionHistoryVisibility.INHERIT,
        help_text=_("Who may see prior file versions for this type."),
    )
    version_history_student = models.BooleanField(
        null=True,
        blank=True,
        help_text=_("Custom override for students when visibility is custom."),
    )
    version_history_coordinator = models.BooleanField(
        null=True,
        blank=True,
        help_text=_("Custom override for coordinators when visibility is custom."),
    )
    version_history_admin = models.BooleanField(
        null=True,
        blank=True,
        help_text=_("Custom override for admins when visibility is custom."),
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def parsed_accepted_extensions(self) -> list[str]:
        seen: list[str] = []
        families = self.file_type_families.all()
        if hasattr(families, "filter"):
            families = families.filter(is_active=True)
        for family in families:
            for ext in family.parsed_extensions():
                if ext not in seen:
                    seen.append(ext)
        extras = self.accepted_extensions or ""
        for ext in extras.split(","):
            cleaned = ext.strip().lower().lstrip(".")
            if cleaned and cleaned not in seen:
                seen.append(cleaned)
        return seen


class Document(UUIDModel, TimeStampedModel):
    """Uploaded document for an application."""

    application = models.ForeignKey("exchange.Application", on_delete=models.CASCADE)
    type = models.ForeignKey(DocumentType, on_delete=models.CASCADE)
    file = models.FileField(upload_to="documents/")
    uploaded_by = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="uploaded_documents"
    )
    is_valid = models.BooleanField(default=False)
    validated_at = models.DateTimeField(null=True, blank=True)
    supersedes = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="successors",
        help_text=_(
            "Prior upload this file replaces (keeps history). Same application and type."
        ),
    )

    class Meta:
        indexes = [
            models.Index(fields=["application", "type"], name="doc_app_type_idx"),
            models.Index(
                fields=["application", "type", "-created_at"],
                name="doc_app_type_crt_idx",
            ),
            models.Index(fields=["uploaded_by"], name="doc_uploaded_by_idx"),
            models.Index(fields=["is_valid"], name="doc_is_valid_idx"),
            models.Index(fields=["validated_at"], name="doc_validated_at_idx"),
            models.Index(fields=["-created_at"], name="doc_created_desc_idx"),
        ]
        ordering = ["-created_at"]
        verbose_name = "Document"
        verbose_name_plural = "Documents"

    @property
    def is_current(self) -> bool:
        """True when no newer upload supersedes this row."""
        return not self.successors.exists()


class DocumentValidation(UUIDModel, TimeStampedModel):
    """Validation record for a document (virus scan, integrity check, etc.)."""

    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    validator = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    result = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    validated_at = models.DateTimeField(auto_now_add=True)


class DocumentResubmissionRequest(UUIDModel, TimeStampedModel):
    """Request for a student to resubmit a document."""

    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    requested_by = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    reason = models.TextField()
    resolved = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)


class DocumentComment(UUIDModel, TimeStampedModel):
    """Comments on documents, can be internal or visible to students."""

    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    author = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    text = models.TextField()
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class ExchangeAgreementDocument(UUIDModel, TimeStampedModel):
    """File stored against an operational exchange agreement (not student application uploads)."""

    class Category(models.TextChoices):
        SIGNED_COPY = "signed_copy", _("Signed copy")
        AMENDMENT = "amendment", _("Amendment / addendum")
        MOU = "mou", _("Memorandum of understanding")
        ANNEX = "annex", _("Annex / schedule")
        CORRESPONDENCE = "correspondence", _("Correspondence")
        OTHER = "other", _("Other")

    agreement = models.ForeignKey(
        "exchange.ExchangeAgreement",
        on_delete=models.CASCADE,
        related_name="repository_documents",
    )
    category = models.CharField(
        max_length=32,
        choices=Category.choices,
        default=Category.OTHER,
        db_index=True,
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=_("Optional label shown in lists (defaults to filename if empty)."),
    )
    file = models.FileField(upload_to="agreement_repository/%Y/%m/")
    notes = models.TextField(blank=True, default="")
    uploaded_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    supersedes = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="successors",
        help_text=_(
            "Prior upload this file replaces (keeps history). Same agreement and category."
        ),
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Agreement repository document")
        verbose_name_plural = _("Agreement repository documents")
        indexes = [
            models.Index(
                fields=["agreement", "category", "-created_at"],
                name="agrdoc_agr_cat_crt_idx",
            ),
        ]

    def __str__(self):
        label = self.title.strip() or self.file.name
        return f"{label} ({self.get_category_display()})"
