# Generated manually for DocumentType.prefill_students

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("documents", "0007_document_version_history"),
    ]

    operations = [
        migrations.AddField(
            model_name="documenttype",
            name="prefill_students",
            field=models.ManyToManyField(
                blank=True,
                help_text=(
                    "Students allowed to download this type's template prefilled "
                    "with their profile data (no application required)."
                ),
                related_name="prefill_document_types",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
