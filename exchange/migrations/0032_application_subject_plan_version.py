# Historic subject-plan snapshots (max 3 per application).

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("exchange", "0031_programdocumentrequirement_days_after_start"),
    ]

    operations = [
        migrations.CreateModel(
            name="ApplicationSubjectPlanVersion",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("version_number", models.PositiveIntegerField()),
                (
                    "trigger",
                    models.CharField(
                        choices=[
                            ("mapping_changed", "Mapping changed"),
                            ("grades_proposed", "Grades proposed"),
                            ("grades_confirmed", "Grades confirmed"),
                            ("grades_rejected", "Grades rejected"),
                        ],
                        default="mapping_changed",
                        max_length=32,
                    ),
                ),
                (
                    "payload",
                    models.JSONField(
                        default=list,
                        help_text="JSON list of subject-selection dicts captured at snapshot time.",
                    ),
                ),
                (
                    "application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subject_plan_versions",
                        to="exchange.application",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="subject_plan_versions_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Application subject plan version",
                "verbose_name_plural": "Application subject plan versions",
                "ordering": ["-version_number"],
            },
        ),
        migrations.AddIndex(
            model_name="applicationsubjectplanversion",
            index=models.Index(
                fields=["application", "-version_number"],
                name="subj_plan_ver_app_num_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="applicationsubjectplanversion",
            constraint=models.UniqueConstraint(
                fields=("application", "version_number"),
                name="uniq_application_subject_plan_version_number",
            ),
        ),
    ]
