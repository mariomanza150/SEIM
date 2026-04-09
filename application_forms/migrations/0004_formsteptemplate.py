# Generated manually for reusable form step templates

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("application_forms", "0003_alter_formtype_step_definitions"),
    ]

    operations = [
        migrations.CreateModel(
            name="FormStepTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(help_text="Admin label for this template", max_length=200)),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        help_text="Unique id for API references",
                        max_length=80,
                        unique=True,
                    ),
                ),
                ("description", models.TextField(blank=True)),
                (
                    "step_title",
                    models.CharField(
                        help_text="Default title shown for the step when applied to a form",
                        max_length=200,
                    ),
                ),
                (
                    "default_step_key",
                    models.CharField(
                        help_text="Default step key (e.g. academics); must not collide on target form",
                        max_length=80,
                    ),
                ),
                (
                    "schema_properties",
                    models.JSONField(
                        default=dict,
                        help_text='JSON Schema "properties" entries to merge, e.g. {"gpa_statement": {"type":"string","title":"GPA"}}',
                    ),
                ),
                (
                    "required_field_names",
                    models.JSONField(
                        blank=True,
                        default=list,
                        help_text="Field names (keys in schema_properties) appended to form schema required[]",
                    ),
                ),
                (
                    "ui_schema_fragment",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="Optional react-jsonschema-form ui_schema fragment for these fields",
                    ),
                ),
                (
                    "required_document_type_ids",
                    models.JSONField(
                        blank=True,
                        default=list,
                        help_text="Optional DocumentType PKs for the generated step (same as step_definitions)",
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["name"],
                "verbose_name": "Form step template",
                "verbose_name_plural": "Form step templates",
            },
        ),
    ]
