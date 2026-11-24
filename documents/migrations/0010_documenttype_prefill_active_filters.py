# Additive: persist prefill active filters + manual exclusion list on DocumentType.
# Reversible via reverse migration (drops the fields).

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("documents", "0009_documenttype_download_only_mode"),
    ]

    operations = [
        migrations.AddField(
            model_name="documenttype",
            name="prefill_active_filters",
            field=models.JSONField(
                blank=True,
                default=None,
                help_text=(
                    "When set, students who match these filters (domain / unidad / school) "
                    "are auto-added to the prefill allow-list. Null turns auto-inclusion off."
                ),
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="documenttype",
            name="prefill_filter_exclusions",
            field=models.ManyToManyField(
                blank=True,
                help_text=(
                    "Students manually removed while active filters are on; "
                    "they are not auto-re-added until filters change or they are added again."
                ),
                related_name="prefill_document_type_exclusions",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
