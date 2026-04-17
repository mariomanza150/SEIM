from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.text import slugify

from core.models import TimeStampedModel, UUIDModel


class WorkflowDefinition(UUIDModel, TimeStampedModel):
    """
    A named workflow template (logical workflow). Each definition has versioned BPMN sources.
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=80, unique=True, blank=True)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:80]
        super().save(*args, **kwargs)


class WorkflowVersion(UUIDModel, TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    definition = models.ForeignKey(
        WorkflowDefinition,
        on_delete=models.CASCADE,
        related_name="versions",
    )
    version = models.PositiveIntegerField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    bpmn_xml = models.TextField(help_text="BPMN 2.0 XML source for this version.")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_workflow_versions",
    )
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["definition__name", "-version"]
        constraints = [
            models.UniqueConstraint(
                fields=["definition", "version"],
                name="uniq_workflow_definition_version",
            )
        ]

    def __str__(self) -> str:
        return f"{self.definition.name} v{self.version}"


class WorkflowInstance(UUIDModel, TimeStampedModel):
    """
    Runtime workflow instance bound to one Application.
    """

    workflow_version = models.ForeignKey(
        WorkflowVersion,
        on_delete=models.PROTECT,
        related_name="instances",
    )
    application = models.OneToOneField(
        "exchange.Application",
        on_delete=models.CASCADE,
        related_name="workflow_instance",
    )
    engine_state = models.JSONField(default=dict, blank=True)
    current_tasks = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=32, blank=True, default="")
    last_event_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"WorkflowInstance({self.application_id})"


class WorkflowEvent(UUIDModel, TimeStampedModel):
    """
    Append-only audit log for workflow execution.
    """

    instance = models.ForeignKey(
        WorkflowInstance,
        on_delete=models.CASCADE,
        related_name="events",
    )
    event_type = models.CharField(max_length=64)
    payload = models.JSONField(default=dict, blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workflow_events",
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.event_type} @ {self.created_at:%Y-%m-%d %H:%M:%S}"

