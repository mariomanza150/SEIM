# Additive: extend DocumentType.submission_mode choices with download_only.

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("documents", "0008_documenttype_prefill_students"),
    ]

    operations = [
        migrations.AlterField(
            model_name="documenttype",
            name="submission_mode",
            field=models.CharField(
                choices=[
                    ("upload", "Upload"),
                    ("template_download", "Template download"),
                    ("system_generated", "System generated"),
                    ("instructions_only", "Instructions only"),
                    ("download_only", "Download only"),
                ],
                db_index=True,
                default="upload",
                max_length=32,
            ),
        ),
    ]
