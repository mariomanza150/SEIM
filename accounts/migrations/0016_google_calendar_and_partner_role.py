import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


def seed_partner_role(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    Role.objects.get_or_create(name="partner")


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0015_seed_schools_programs_banks"),
    ]

    operations = [
        migrations.CreateModel(
            name="GoogleCalendarConnection",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("google_email", models.EmailField(blank=True, default="", max_length=254)),
                ("access_token", models.TextField(blank=True, default="")),
                ("refresh_token", models.TextField(blank=True, default="")),
                ("token_expiry", models.DateTimeField(blank=True, null=True)),
                (
                    "google_calendar_id",
                    models.CharField(default="primary", max_length=255),
                ),
                ("last_synced_at", models.DateTimeField(blank=True, null=True)),
                ("last_sync_error", models.TextField(blank=True, default="")),
                ("event_map", models.JSONField(blank=True, default=dict)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="google_calendar",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Google Calendar connection",
                "verbose_name_plural": "Google Calendar connections",
            },
        ),
        migrations.RunPython(seed_partner_role, migrations.RunPython.noop),
    ]
