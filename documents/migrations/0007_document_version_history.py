# Generated manually for Document.supersedes and DocumentType history visibility

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0006_file_type_family"),
    ]

    operations = [
        migrations.AddField(
            model_name="documenttype",
            name="version_history_visibility",
            field=models.CharField(
                choices=[
                    ("inherit", "Inherit institution defaults"),
                    ("hidden", "Hidden for all roles"),
                    ("custom", "Custom per-role overrides"),
                ],
                default="inherit",
                help_text="Who may see prior file versions for this type.",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="documenttype",
            name="version_history_student",
            field=models.BooleanField(
                blank=True,
                help_text="Custom override for students when visibility is custom.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="documenttype",
            name="version_history_coordinator",
            field=models.BooleanField(
                blank=True,
                help_text="Custom override for coordinators when visibility is custom.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="documenttype",
            name="version_history_admin",
            field=models.BooleanField(
                blank=True,
                help_text="Custom override for admins when visibility is custom.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="document",
            name="supersedes",
            field=models.ForeignKey(
                blank=True,
                help_text=(
                    "Prior upload this file replaces (keeps history). "
                    "Same application and type."
                ),
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="successors",
                to="documents.document",
            ),
        ),
        migrations.AddIndex(
            model_name="document",
            index=models.Index(
                fields=["application", "type", "-created_at"],
                name="doc_app_type_crt_idx",
            ),
        ),
    ]
