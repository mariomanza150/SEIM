# Generated manually for nomination cycles + partner allocations

import django.db.models.deletion
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("exchange", "0035_eligibilityruleset_content_revision"),
    ]

    operations = [
        migrations.CreateModel(
            name="NominationCycle",
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
                ("name", models.CharField(max_length=120)),
                ("opens_at", models.DateField(blank=True, null=True)),
                ("closes_at", models.DateField(blank=True, null=True)),
                (
                    "seat_quota",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text=(
                            "Optional Match slot override for this cycle. When set, Match uses this "
                            "quota instead of program.enrollment_capacity."
                        ),
                        null=True,
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="At most one active cycle should be used for Match at a time.",
                    ),
                ),
                (
                    "program",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="nomination_cycles",
                        to="exchange.program",
                    ),
                ),
            ],
            options={
                "verbose_name": "Nomination cycle",
                "verbose_name_plural": "Nomination cycles",
                "ordering": ["-opens_at", "-created_at"],
            },
        ),
        migrations.CreateModel(
            name="NominationPartnerAllocation",
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
                    "seat_quota",
                    models.PositiveIntegerField(
                        help_text="Seats reserved for this partner under the cycle.",
                    ),
                ),
                (
                    "agreement",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="nomination_allocations",
                        to="exchange.exchangeagreement",
                    ),
                ),
                (
                    "cycle",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="partner_allocations",
                        to="exchange.nominationcycle",
                    ),
                ),
            ],
            options={
                "verbose_name": "Nomination partner allocation",
                "verbose_name_plural": "Nomination partner allocations",
                "ordering": ["agreement__partner_institution_name", "created_at"],
            },
        ),
        migrations.AddField(
            model_name="application",
            name="nomination_cycle",
            field=models.ForeignKey(
                blank=True,
                help_text="Nomination cycle that produced the current nominated/waitlist status.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="applications",
                to="exchange.nominationcycle",
            ),
        ),
        migrations.AddField(
            model_name="application",
            name="partner_nomination_acknowledged_at",
            field=models.DateTimeField(
                blank=True,
                help_text="When a partner contact acknowledged this nomination.",
                null=True,
            ),
        ),
        migrations.AddConstraint(
            model_name="nominationcycle",
            constraint=models.UniqueConstraint(
                fields=("program", "name"),
                name="uniq_nomination_cycle_program_name",
            ),
        ),
        migrations.AddConstraint(
            model_name="nominationpartnerallocation",
            constraint=models.UniqueConstraint(
                fields=("cycle", "agreement"),
                name="uniq_nomination_partner_alloc_cycle_agreement",
            ),
        ),
    ]
