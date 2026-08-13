from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0016_google_calendar_and_partner_role"),
    ]

    operations = [
        migrations.AddField(
            model_name="googlecalendarconnection",
            name="imported_events",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="Cached Google-only events from the last two-way sync (read-only overlay).",
            ),
        ),
    ]
