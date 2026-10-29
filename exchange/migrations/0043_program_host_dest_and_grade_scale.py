# Generated manually for host destination + outgoing grade scale settings.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exchange", "0042_program_mobility_direction"),
        ("grades", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="host_academic_program_text",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Free-text host academic program name when not using the catalog.",
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name="application",
            name="host_institution_text",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Free-text host university name when not using the catalog.",
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name="application",
            name="host_school_text",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Free-text host school / faculty when not using the catalog.",
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name="program",
            name="default_grade_scale",
            field=models.ForeignKey(
                blank=True,
                help_text="For outgoing programs: preferred grade scale for applicants. Overrides the AllowedEmailDomain default when set.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="programs_default",
                to="grades.gradescale",
            ),
        ),
        migrations.AddField(
            model_name="program",
            name="host_destination_mode",
            field=models.CharField(
                choices=[
                    ("catalog", "Catalog only"),
                    ("free_text", "Free text only"),
                    ("either", "Catalog or free text"),
                ],
                default="catalog",
                help_text="How applicants enter host university / school / academic program: catalog selects, free-text fields, or either (catalog with a 'not listed' typed option).",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="program",
            name="host_destination_required",
            field=models.BooleanField(
                default=True,
                help_text="When enabled, applicants must provide a host destination before submit (catalog and/or free text, depending on host destination mode).",
            ),
        ),
        migrations.AddField(
            model_name="program",
            name="lock_grade_scale",
            field=models.BooleanField(
                default=False,
                help_text="For outgoing programs: when set (with a default scale), applicants cannot change the grade scale on the apply form.",
            ),
        ),
    ]
