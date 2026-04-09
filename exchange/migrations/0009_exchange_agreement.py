import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exchange", "0008_program_coordinators_application_assigned_coordinator"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExchangeAgreement",
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
                (
                    "title",
                    models.CharField(
                        help_text="Short title for staff (e.g. framework agreement name).",
                        max_length=255,
                    ),
                ),
                ("partner_institution_name", models.CharField(max_length=255)),
                (
                    "partner_country",
                    models.CharField(blank=True, default="", max_length=120),
                ),
                (
                    "partner_reference_id",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Partner’s own agreement or contract reference, if any.",
                        max_length=120,
                    ),
                ),
                (
                    "internal_reference",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        default="",
                        help_text="Optional internal tracking code.",
                        max_length=64,
                    ),
                ),
                (
                    "agreement_type",
                    models.CharField(
                        choices=[
                            ("bilateral", "Bilateral"),
                            ("multilateral", "Multilateral"),
                            ("erasmus", "Erasmus+"),
                            ("specific", "Specific program"),
                            ("other", "Other"),
                        ],
                        default="bilateral",
                        max_length=32,
                    ),
                ),
                ("start_date", models.DateField(blank=True, null=True)),
                (
                    "end_date",
                    models.DateField(
                        blank=True,
                        help_text="Leave blank if no fixed end date.",
                        null=True,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("active", "Active"),
                            ("suspended", "Suspended"),
                            ("expired", "Expired"),
                            ("terminated", "Terminated"),
                            ("renewal_pending", "Renewal pending"),
                        ],
                        db_index=True,
                        default="draft",
                        max_length=32,
                    ),
                ),
                ("notes", models.TextField(blank=True, default="")),
                (
                    "programs",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Exchange programs governed or covered by this agreement.",
                        related_name="exchange_agreements",
                        to="exchange.program",
                    ),
                ),
            ],
            options={
                "verbose_name": "Exchange agreement",
                "verbose_name_plural": "Exchange agreements",
                "ordering": ["-start_date", "partner_institution_name", "title"],
            },
        ),
        migrations.AddIndex(
            model_name="exchangeagreement",
            index=models.Index(
                fields=["status", "end_date"],
                name="exagreement_status_end_idx",
            ),
        ),
    ]
