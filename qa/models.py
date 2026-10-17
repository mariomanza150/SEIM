import os
import uuid

from django.conf import settings
from django.db import IntegrityError, models, transaction
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel, UUIDModel


def attachment_upload_to(instance, filename):
    ext = os.path.splitext(filename or "")[1].lower()[:10]
    return f"qa_issues/{uuid.uuid4().hex}{ext}"


class Issue(UUIDModel, TimeStampedModel):
    class Severity(models.TextChoices):
        BLOCKER = "blocker", _("Blocker")
        MAJOR = "major", _("Major")
        MINOR = "minor", _("Minor")
        COSMETIC = "cosmetic", _("Cosmetic")

    class Kind(models.TextChoices):
        BUG = "bug", _("Bug")
        UX = "ux", _("UX / usability")
        CONTENT = "content", _("Content / translation")
        SUGGESTION = "suggestion", _("Suggestion")

    class Status(models.TextChoices):
        NEW = "new", _("New")
        TRIAGED = "triaged", _("Triaged")
        IN_PROGRESS = "in_progress", _("In progress")
        NEEDS_INFO = "needs_info", _("Needs info")
        FIXED = "fixed", _("Fixed")
        VERIFIED = "verified", _("Verified")
        CLOSED = "closed", _("Closed")
        WONT_FIX = "wont_fix", _("Won't fix")
        DUPLICATE = "duplicate", _("Duplicate")

    OPEN_STATUSES = ("new", "triaged", "in_progress", "needs_info")

    number = models.PositiveIntegerField(unique=True, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    steps = models.TextField(blank=True, default="")
    severity = models.CharField(
        max_length=20, choices=Severity.choices, default=Severity.MINOR
    )
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.BUG)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.NEW, db_index=True
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="qa_issues_reported",
    )
    acting_as = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="qa_issues_acting_as",
        help_text=_("Demo/impersonated account the tester was using."),
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="qa_issues_assigned",
    )
    duplicate_of = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )
    # Auto-captured context
    page_url = models.CharField(max_length=1000, blank=True, default="")
    route_name = models.CharField(max_length=200, blank=True, default="")
    reporter_role = models.CharField(max_length=50, blank=True, default="")
    user_agent = models.CharField(max_length=500, blank=True, default="")
    viewport = models.CharField(max_length=50, blank=True, default="")
    locale = models.CharField(max_length=20, blank=True, default="")
    app_version = models.CharField(max_length=100, blank=True, default="")
    build_commit = models.CharField(max_length=40, blank=True, default="")
    deploy_tier = models.CharField(max_length=20, blank=True, default="")
    diagnostics = models.JSONField(default=dict, blank=True)
    resolved_in_commit = models.CharField(max_length=40, blank=True, default="")
    github_issue_url = models.URLField(blank=True, default="")

    class Meta:
        ordering = ["-number"]

    def __str__(self):
        return f"{self.reference}: {self.title}"

    @property
    def reference(self):
        return f"QA-{self.number}"

    def save(self, *args, **kwargs):
        if self.number:
            return super().save(*args, **kwargs)
        # Sequential human-friendly numbers; retry on the (rare) concurrent clash.
        for attempt in range(5):
            last = (
                Issue.objects.order_by("-number")
                .values_list("number", flat=True)
                .first()
            )
            self.number = (last or 0) + 1
            try:
                with transaction.atomic():
                    return super().save(*args, **kwargs)
            except IntegrityError:
                self.number = None
                if attempt == 4:
                    raise


class IssueAttachment(UUIDModel, TimeStampedModel):
    class Kind(models.TextChoices):
        SCREENSHOT = "screenshot", _("Screenshot")
        RECORDING = "recording", _("Recording")
        LOG = "log", _("Log / text")
        OTHER = "other", _("Other")

    issue = models.ForeignKey(
        Issue, on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.FileField(upload_to=attachment_upload_to)
    original_name = models.CharField(max_length=255, blank=True, default="")
    content_type = models.CharField(max_length=100, blank=True, default="")
    size = models.PositiveIntegerField(default=0)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.OTHER)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.original_name or self.file.name


class IssueComment(UUIDModel, TimeStampedModel):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    body = models.TextField()
    is_internal = models.BooleanField(
        default=False, help_text=_("Visible to triagers only.")
    )
    is_system = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment on {self.issue.reference}"


class QAAuditEvent(UUIDModel, TimeStampedModel):
    """Audit trail for demo-account switches and staff impersonation."""

    class Action(models.TextChoices):
        DEMO_SWITCH = "demo_switch", _("Switched into demo account")
        DEMO_RETURN = "demo_return", _("Returned from demo account")
        IMPERSONATE_START = "impersonate_start", _("Impersonation started")
        IMPERSONATE_STOP = "impersonate_stop", _("Impersonation stopped")
        RESET_DEMO = "reset_demo", _("Demo data reset requested")

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="qa_audit_events",
    )
    target = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="qa_audit_targets",
    )
    action = models.CharField(max_length=30, choices=Action.choices)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True, default="")
    note = models.CharField(max_length=500, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_action_display()} by {self.actor_id} → {self.target_id}"


class CapturedEmail(UUIDModel, TimeStampedModel):
    """Outgoing email captured on test servers instead of being delivered."""

    subject = models.CharField(max_length=998, blank=True, default="")
    from_email = models.CharField(max_length=320, blank=True, default="")
    to = models.JSONField(default=list, blank=True)
    cc = models.JSONField(default=list, blank=True)
    bcc = models.JSONField(default=list, blank=True)
    body_text = models.TextField(blank=True, default="")
    body_html = models.TextField(blank=True, default="")
    recipients_index = models.TextField(
        blank=True, default="", help_text=_("Lower-cased recipients, for filtering.")
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.subject or "(no subject)"


class TestScenario(UUIDModel, TimeStampedModel):
    """A manual test case testers run against each build (seeded from qa/scenarios.py)."""

    __test__ = False  # not a pytest class

    code = models.CharField(max_length=40, unique=True)
    area = models.CharField(max_length=60)
    role = models.CharField(max_length=20, blank=True, default="")
    title = models.CharField(max_length=200)
    title_es = models.CharField(max_length=200, blank=True, default="")
    steps = models.TextField(blank=True, default="")
    steps_es = models.TextField(blank=True, default="")
    expected = models.TextField(blank=True, default="")
    expected_es = models.TextField(blank=True, default="")
    route_name = models.CharField(max_length=100, blank=True, default="")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "code"]

    def __str__(self):
        return f"{self.code}: {self.title}"


class ScenarioResult(UUIDModel, TimeStampedModel):
    class Outcome(models.TextChoices):
        PASS = "pass", _("Pass")
        FAIL = "fail", _("Fail")
        BLOCKED = "blocked", _("Blocked")
        SKIPPED = "skipped", _("Skipped")

    scenario = models.ForeignKey(
        TestScenario, on_delete=models.CASCADE, related_name="results"
    )
    tester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="qa_scenario_results",
    )
    build_commit = models.CharField(max_length=40, blank=True, default="")
    outcome = models.CharField(max_length=10, choices=Outcome.choices)
    note = models.TextField(blank=True, default="")
    issue = models.ForeignKey(
        Issue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scenario_results",
    )

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["scenario", "tester", "build_commit"],
                name="qa_one_result_per_build",
            )
        ]

    def __str__(self):
        return f"{self.scenario.code} {self.outcome} ({self.build_commit[:7]})"
