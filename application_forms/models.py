"""
Application Forms Models

This module provides custom form type and submission tracking models
that work alongside the official django-dynforms package.

Note: This app is separate from the 'dynforms' package to avoid namespace conflicts.
The official django-dynforms package provides the form builder UI, while this app
provides custom models for tracking form definitions and submissions specific to
SEIM's exchange program workflow.
"""

import json

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


class FormType(models.Model):
    """
    Defines the structure and configuration of a dynamic form.

    This model stores custom form schemas for exchange program applications,
    surveys, feedback forms, etc. It works alongside the official django-dynforms
    package by providing additional metadata and program-specific features.
    """
    FORM_TYPE_CHOICES = [
        ('application', 'Exchange Application'),
        ('survey', 'Survey'),
        ('feedback', 'Feedback'),
        ('custom', 'Custom Form'),
    ]

    name = models.CharField(
        max_length=200,
        help_text="Display name for the form"
    )
    form_type = models.CharField(
        max_length=50,
        choices=FORM_TYPE_CHOICES,
        default='application',
        help_text="The purpose/type of this form"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of the form"
    )
    schema = models.JSONField(
        help_text="JSON schema defining field structure",
        default=dict,
        blank=True
    )
    ui_schema = models.JSONField(
        help_text="UI schema for form rendering (optional)",
        default=dict,
        blank=True
    )
    step_definitions = models.JSONField(
        default=list,
        blank=True,
        help_text='Multi-step layout: list of {"key", "title", "field_names": [...], '
        '"required_document_type_ids": [optional DocumentType PKs], '
        '"visible_when": {optional same shape as x-seim-visibleWhen}}. '
        "IDs must exist and are enforced (with program required types) before advancing past that step. "
        "Empty = single-step form.",
    )

    # Meta fields
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_application_forms'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Application Form Type'
        verbose_name_plural = 'Application Form Types'
        app_label = 'application_forms'

    def __str__(self):
        return f"{self.name} ({self.get_form_type_display()})"

    def clean(self):
        """Validate the form schema"""
        if self.schema:
            try:
                # Basic validation to ensure it's valid JSON
                json.dumps(self.schema)
            except (TypeError, ValueError) as e:
                raise ValidationError(f'Invalid JSON schema: {str(e)}')

        if self.step_definitions:
            if not isinstance(self.step_definitions, list):
                raise ValidationError({'step_definitions': 'Must be a list of step objects.'})
            props = set((self.schema or {}).get('properties', {}).keys())
            seen_keys = set()
            for i, step in enumerate(self.step_definitions):
                if not isinstance(step, dict):
                    raise ValidationError({'step_definitions': f'Item {i} must be an object.'})
                key = step.get('key')
                if not key or not str(key).strip():
                    raise ValidationError({'step_definitions': f'Item {i} must include a non-empty key.'})
                key = str(key)
                if key in seen_keys:
                    raise ValidationError({'step_definitions': f'Duplicate step key: {key}'})
                seen_keys.add(key)
                field_names = step.get('field_names')
                if not isinstance(field_names, list) or not field_names:
                    raise ValidationError({'step_definitions': f'Step "{key}" needs a non-empty field_names list.'})
                for fname in field_names:
                    if fname not in props:
                        raise ValidationError(
                            {'step_definitions': f'Step "{key}" references unknown field "{fname}".'}
                        )
                raw_doc_ids = step.get("required_document_type_ids", None)
                if raw_doc_ids is not None:
                    if not isinstance(raw_doc_ids, list):
                        raise ValidationError(
                            {
                                "step_definitions": (
                                    f'Step "{key}" required_document_type_ids must be a list of integers.'
                                )
                            }
                        )
                    normalized_doc_ids = []
                    for j, did in enumerate(raw_doc_ids):
                        try:
                            normalized_doc_ids.append(int(did))
                        except (TypeError, ValueError) as exc:
                            raise ValidationError(
                                {
                                    "step_definitions": (
                                        f'Step "{key}" required_document_type_ids[{j}] must be an integer.'
                                    )
                                }
                            ) from exc
                    if normalized_doc_ids:
                        from documents.models import DocumentType

                        existing = set(
                            DocumentType.objects.filter(pk__in=normalized_doc_ids).values_list(
                                "pk", flat=True
                            )
                        )
                        missing = [pk for pk in normalized_doc_ids if pk not in existing]
                        if missing:
                            raise ValidationError(
                                {
                                    "step_definitions": (
                                        f'Step "{key}" references unknown document type id(s): {missing}.'
                                    )
                                }
                            )
                raw_vw = step.get("visible_when") or step.get("visibleWhen")
                if raw_vw is not None:
                    if not isinstance(raw_vw, dict):
                        raise ValidationError(
                            {
                                "step_definitions": (
                                    f'Step "{key}" visible_when must be an object when set.'
                                )
                            }
                        )
                    if raw_vw:
                        has_field = bool(raw_vw.get("field")) and isinstance(
                            raw_vw.get("field"), str
                        )
                        has_ctx = any(
                            k in raw_vw
                            for k in (
                                "program_id",
                                "program_id_in",
                                "has_assigned_coordinator",
                                "staff_only",
                                "roles_any",
                            )
                        )
                        if not has_field and not has_ctx:
                            raise ValidationError(
                                {
                                    "step_definitions": (
                                        f'Step "{key}" visible_when needs a string "field" and/or '
                                        f"program / coordinator / viewer role keys."
                                    )
                                }
                            )
                        if "program_id" in raw_vw:
                            try:
                                int(raw_vw["program_id"])
                            except (TypeError, ValueError) as exc:
                                raise ValidationError(
                                    {
                                        "step_definitions": (
                                            f'Step "{key}" visible_when program_id must be an integer.'
                                        )
                                    }
                                ) from exc
                        if "program_id_in" in raw_vw:
                            pin = raw_vw["program_id_in"]
                            if not isinstance(pin, list) or not pin:
                                raise ValidationError(
                                    {
                                        "step_definitions": (
                                            f'Step "{key}" visible_when program_id_in must be a non-empty list.'
                                        )
                                    }
                                )
                            for j, p in enumerate(pin):
                                try:
                                    int(p)
                                except (TypeError, ValueError) as exc:
                                    raise ValidationError(
                                        {
                                            "step_definitions": (
                                                f'Step "{key}" visible_when program_id_in[{j}] '
                                                f"must be an integer."
                                            )
                                        }
                                    ) from exc
                        if "has_assigned_coordinator" in raw_vw and raw_vw[
                            "has_assigned_coordinator"
                        ] is not None:
                            if not isinstance(raw_vw["has_assigned_coordinator"], bool):
                                raise ValidationError(
                                    {
                                        "step_definitions": (
                                            f'Step "{key}" visible_when has_assigned_coordinator '
                                            f"must be true or false."
                                        )
                                    }
                                )
                        if "staff_only" in raw_vw and raw_vw["staff_only"] is not None:
                            if not isinstance(raw_vw["staff_only"], bool):
                                raise ValidationError(
                                    {
                                        "step_definitions": (
                                            f'Step "{key}" visible_when staff_only must be true or false.'
                                        )
                                    }
                                )
                        if "roles_any" in raw_vw:
                            ra = raw_vw["roles_any"]
                            if not isinstance(ra, list) or not ra:
                                raise ValidationError(
                                    {
                                        "step_definitions": (
                                            f'Step "{key}" visible_when roles_any must be a non-empty list.'
                                        )
                                    }
                                )
                            for j, rn in enumerate(ra):
                                if not isinstance(rn, str) or not rn.strip():
                                    raise ValidationError(
                                        {
                                            "step_definitions": (
                                                f'Step "{key}" visible_when roles_any[{j}] '
                                                f"must be a non-empty string."
                                            )
                                        }
                                    )

    def is_multi_step(self):
        return bool(self.step_definitions)

    def get_multi_step_layout(self):
        """Return normalized steps for API consumers."""
        layout = []
        for step in self.step_definitions or []:
            raw_doc_ids = step.get("required_document_type_ids") or []
            doc_ids = []
            if isinstance(raw_doc_ids, list):
                for x in raw_doc_ids:
                    try:
                        doc_ids.append(int(x))
                    except (TypeError, ValueError):
                        continue
            row = {
                'key': str(step.get('key', '') or ''),
                'title': step.get('title') or step.get('key') or '',
                'field_names': list(step.get('field_names') or []),
                'required_document_type_ids': doc_ids,
            }
            vw = step.get("visible_when") or step.get("visibleWhen")
            if vw is not None:
                row["visible_when"] = vw
            layout.append(row)
        return layout

    def get_step_field_names(self, step_key: str):
        """Return field_names for step_key, or None if unknown."""
        for step in self.step_definitions or []:
            if str(step.get('key', '')) == str(step_key):
                return list(step.get('field_names') or [])
        return None

    def get_field_count(self):
        """Return the number of fields in the form schema"""
        if not self.schema:
            return 0
        properties = self.schema.get('properties', {})
        return len(properties)

    def get_required_fields(self):
        """Return list of required field names"""
        if not self.schema:
            return []
        return self.schema.get('required', [])


class FormStepTemplate(models.Model):
    """
    Reusable bundle of JSON-schema fields + optional UI fragment + step metadata.

    Admins apply templates to a FormType via API or copy workflow; fields merge into
    schema.properties and a new step is appended to step_definitions.
    """

    name = models.CharField(max_length=200, help_text="Admin label for this template")
    slug = models.SlugField(
        max_length=80,
        unique=True,
        blank=True,
        help_text="Unique id (auto-filled from name if left blank on save)",
    )
    description = models.TextField(blank=True)
    step_title = models.CharField(
        max_length=200,
        help_text="Default title for the step when applied to a form",
    )
    default_step_key = models.CharField(
        max_length=80,
        help_text="Default step key (e.g. academics); must be unique on the target form when applied",
    )
    schema_properties = models.JSONField(
        default=dict,
        help_text='JSON Schema property map merged into FormType.schema["properties"]',
    )
    required_field_names = models.JSONField(
        default=list,
        blank=True,
        help_text="Keys from schema_properties to add to the form-level required list",
    )
    ui_schema_fragment = models.JSONField(
        default=dict,
        blank=True,
        help_text="Fragment merged into FormType.ui_schema",
    )
    required_document_type_ids = models.JSONField(
        default=list,
        blank=True,
        help_text="Optional DocumentType PKs attached to the generated step",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Form step template"
        verbose_name_plural = "Form step templates"
        app_label = "application_forms"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not (self.slug and str(self.slug).strip()):
            base = slugify(self.name)[:80] or "step-template"
            candidate = base
            n = 2
            while FormStepTemplate.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                suffix = f"-{n}"
                candidate = f"{base[: 80 - len(suffix)]}{suffix}" if len(base) + len(suffix) > 80 else f"{base}-{n}"
                n += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def clean(self):
        props = self.schema_properties or {}
        if not isinstance(props, dict):
            raise ValidationError({"schema_properties": "Must be a JSON object."})
        if not props:
            raise ValidationError({"schema_properties": "Define at least one property."})
        keys = set(props.keys())
        req_names = self.required_field_names or []
        if not isinstance(req_names, list):
            raise ValidationError({"required_field_names": "Must be a list of field names."})
        for r in req_names:
            if r not in keys:
                raise ValidationError(
                    {"required_field_names": f'"{r}" is not a key in schema_properties.'}
                )
        raw_docs = self.required_document_type_ids
        if raw_docs is not None and not isinstance(raw_docs, list):
            raise ValidationError(
                {"required_document_type_ids": "Must be a list of integers."}
            )
        doc_ids = []
        for j, did in enumerate(raw_docs or []):
            try:
                doc_ids.append(int(did))
            except (TypeError, ValueError) as exc:
                raise ValidationError(
                    {"required_document_type_ids": f"Item {j} must be an integer."}
                ) from exc
        if doc_ids:
            from documents.models import DocumentType

            existing = set(
                DocumentType.objects.filter(pk__in=doc_ids).values_list("pk", flat=True)
            )
            missing = [pk for pk in doc_ids if pk not in existing]
            if missing:
                raise ValidationError(
                    {
                        "required_document_type_ids": (
                            f"Unknown document type id(s): {missing}."
                        )
                    }
                )
        key = (self.default_step_key or "").strip()
        if not key:
            raise ValidationError({"default_step_key": "Provide a non-empty default step key."})


class FormSubmission(models.Model):
    """
    Stores individual form submissions with responses.

    This model captures user responses to custom forms and links them
    to exchange programs and applications for tracking and analysis.
    """
    form_type = models.ForeignKey(
        FormType,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    submitted_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='application_form_submissions'
    )

    # Store responses as JSON
    responses = models.JSONField(
        help_text="JSON object containing the form responses",
        default=dict
    )

    # Meta fields
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional: link to exchange programs and applications
    program = models.ForeignKey(
        'exchange.Program',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='form_submissions'
    )
    application = models.ForeignKey(
        'exchange.Application',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='form_submissions',
        help_text="Link to the exchange application this form is part of"
    )

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Form Submission'
        verbose_name_plural = 'Form Submissions'
        app_label = 'application_forms'

    def __str__(self):
        return f"{self.form_type.name} - {self.submitted_by} ({self.submitted_at.date()})"

    def clean(self):
        """Validate the responses against the form schema"""
        if self.responses:
            try:
                json.dumps(self.responses)
            except (TypeError, ValueError) as e:
                raise ValidationError(f'Invalid JSON responses: {str(e)}')

        # Completeness of required fields is enforced in FormSubmissionService / application submit flow,
        # so draft submissions may be partial (e.g. multi-step saves).

    def get_response_count(self):
        """Return the number of fields with responses"""
        if not self.responses:
            return 0
        return len(self.responses)


# Utility validators for reuse
def validate_json_schema(value):
    """Validator for JSON schema fields"""
    try:
        if isinstance(value, str):
            json.loads(value)
        elif isinstance(value, dict):
            json.dumps(value)
        else:
            raise ValidationError('Schema must be a valid JSON object or string')
    except (TypeError, ValueError) as e:
        raise ValidationError(f'Invalid JSON: {str(e)}')


def validate_form_response(value):
    """Validator for form response data"""
    try:
        if isinstance(value, str):
            data = json.loads(value)
        elif isinstance(value, dict):
            data = value
        else:
            raise ValidationError('Response must be a valid JSON object or string')

        if not isinstance(data, dict):
            raise ValidationError('Form response must be a JSON object')
    except (TypeError, ValueError) as e:
        raise ValidationError(f'Invalid JSON response: {str(e)}')

