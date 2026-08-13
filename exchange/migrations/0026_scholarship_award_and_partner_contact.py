import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("exchange", "0025_host_subjects_phase3"),
    ]

    operations = [
        migrations.CreateModel(
            name="ScholarshipAward",
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
                    "status",
                    models.CharField(
                        choices=[
                            ("nominated", "Nominated"),
                            ("awarded", "Awarded"),
                            ("declined", "Declined"),
                            ("disbursing", "Disbursing"),
                            ("disbursed", "Disbursed"),
                            ("withdrawn", "Withdrawn"),
                        ],
                        db_index=True,
                        default="nominated",
                        max_length=32,
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=12, null=True
                    ),
                ),
                ("currency", models.CharField(default="MXN", max_length=8)),
                ("notes", models.TextField(blank=True, default="")),
                ("decided_at", models.DateTimeField(blank=True, null=True)),
                (
                    "application",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="scholarship_award",
                        to="exchange.application",
                    ),
                ),
                (
                    "decided_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="scholarship_awards_decided",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Scholarship award",
                "verbose_name_plural": "Scholarship awards",
                "ordering": ["-updated_at"],
            },
        ),
        migrations.CreateModel(
            name="ScholarshipDisbursement",
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
                ("label", models.CharField(max_length=255)),
                (
                    "amount",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=12, null=True
                    ),
                ),
                ("due_date", models.DateField(blank=True, null=True)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("notes", models.TextField(blank=True, default="")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("paid", "Paid"),
                            ("skipped", "Skipped"),
                        ],
                        db_index=True,
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("sort_order", models.PositiveIntegerField(default=0)),
                (
                    "award",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="disbursements",
                        to="exchange.scholarshipaward",
                    ),
                ),
            ],
            options={
                "verbose_name": "Scholarship disbursement",
                "verbose_name_plural": "Scholarship disbursements",
                "ordering": ["sort_order", "due_date", "created_at"],
            },
        ),
        migrations.CreateModel(
            name="PartnerContact",
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
                ("title", models.CharField(blank=True, default="", max_length=120)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "agreement",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="partner_contacts",
                        to="exchange.exchangeagreement",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="partner_contacts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Partner contact",
                "verbose_name_plural": "Partner contacts",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="partnercontact",
            constraint=models.UniqueConstraint(
                fields=("user", "agreement"),
                name="uniq_partner_contact_user_agreement",
            ),
        ),
    ]
