import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exchange", "0009_exchange_agreement"),
    ]

    operations = [
        migrations.CreateModel(
            name="AgreementExpirationReminderLog",
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
                ("days_before", models.PositiveIntegerField()),
                ("agreement_end_date", models.DateField()),
                (
                    "agreement",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="expiration_reminder_logs",
                        to="exchange.exchangeagreement",
                    ),
                ),
            ],
            options={
                "verbose_name": "Agreement expiration reminder log",
                "verbose_name_plural": "Agreement expiration reminder logs",
            },
        ),
        migrations.AddConstraint(
            model_name="agreementexpirationreminderlog",
            constraint=models.UniqueConstraint(
                fields=("agreement", "days_before", "agreement_end_date"),
                name="uniq_agreement_expiry_reminder_milestone",
            ),
        ),
    ]
