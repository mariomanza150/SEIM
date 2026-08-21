# Lifecycle requirement schedule: document required_from_status + ProgramFieldRequirement

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("exchange", "0033_program_min_toefl_score"),
    ]

    operations = [
        migrations.AddField(
            model_name="programdocumentrequirement",
            name="required_from_status",
            field=models.ForeignKey(
                blank=True,
                help_text=(
                    "Pipeline status from which this document is required for students. "
                    "Ignored when is_required is false. Null with is_required means submitted."
                ),
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="gated_document_requirements",
                to="exchange.applicationstatus",
            ),
        ),
        migrations.CreateModel(
            name="ProgramFieldRequirement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "source",
                    models.CharField(
                        choices=[
                            ("profile", "Profile"),
                            ("application", "Application"),
                            ("form", "Form"),
                        ],
                        max_length=20,
                    ),
                ),
                ("field_key", models.CharField(max_length=100)),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="field_requirements",
                        to="exchange.program",
                    ),
                ),
                (
                    "required_from_status",
                    models.ForeignKey(
                        blank=True,
                        help_text=(
                            "Pipeline status from which this field is required. "
                            "Null means optional throughout."
                        ),
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="program_field_requirements",
                        to="exchange.applicationstatus",
                    ),
                ),
            ],
            options={
                "verbose_name": "Program field requirement",
                "verbose_name_plural": "Program field requirements",
                "ordering": ["source", "field_key", "id"],
            },
        ),
        migrations.AddConstraint(
            model_name="programfieldrequirement",
            constraint=models.UniqueConstraint(
                fields=("program", "source", "field_key"),
                name="uniq_program_field_requirement",
            ),
        ),
        migrations.AlterField(
            model_name="programdocumentrequirement",
            name="is_required",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "When false, shown on checklist but optional throughout. "
                    "When true with required_from_status unset, required from submitted."
                ),
            ),
        ),
    ]
