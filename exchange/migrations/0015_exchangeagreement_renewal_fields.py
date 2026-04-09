import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exchange", "0014_program_enrollment_capacity_waitlist"),
    ]

    operations = [
        migrations.AddField(
            model_name="exchangeagreement",
            name="renewal_follow_up_due",
            field=models.DateField(
                blank=True,
                help_text="Optional staff deadline for renewal follow-up.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="exchangeagreement",
            name="renewed_from",
            field=models.ForeignKey(
                blank=True,
                help_text="Prior agreement this record continues when created as a renewal successor.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="renewal_successors",
                to="exchange.exchangeagreement",
            ),
        ),
    ]
