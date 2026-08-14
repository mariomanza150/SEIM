import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("exchange", "0028_savedsearch_analytics_forecast"),
    ]

    operations = [
        migrations.CreateModel(
            name="AgreementComment",
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
                ("text", models.TextField()),
                (
                    "is_private",
                    models.BooleanField(
                        default=False,
                        help_text="Private staff notes are hidden from partner portal users.",
                    ),
                ),
                (
                    "agreement",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="exchange.exchangeagreement",
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["created_at", "id"],
                "indexes": [
                    models.Index(
                        fields=["agreement", "created_at"],
                        name="agcomment_agr_created_idx",
                    )
                ],
            },
        ),
    ]
