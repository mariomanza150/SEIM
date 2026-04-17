import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0007_notification_digest_periodic_task"),
    ]

    operations = [
        migrations.CreateModel(
            name="NotificationRoutingOverride",
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
                    "kind",
                    models.CharField(
                        choices=[
                            ("reminder_event_type", "Reminder event type"),
                            ("transactional_route_key", "Transactional route key"),
                        ],
                        max_length=64,
                    ),
                ),
                (
                    "key",
                    models.CharField(
                        help_text="For reminder routing: the Reminder.event_type string.",
                        max_length=128,
                    ),
                ),
                (
                    "settings_category",
                    models.CharField(
                        choices=[
                            ("applications", "Applications"),
                            ("documents", "Documents"),
                            ("comments", "Comments"),
                            ("programs", "Programs"),
                            ("system", "System"),
                            ("ungated", "Ungated (ignore UserSettings groups)"),
                        ],
                        help_text=(
                            "Which UserSettings notification group gates delivery for this key. "
                            "Use Ungated to bypass group toggles (settings_category=None)."
                        ),
                        max_length=32,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={},
        ),
        migrations.AddConstraint(
            model_name="notificationroutingoverride",
            constraint=models.UniqueConstraint(
                fields=("kind", "key"),
                name="uniq_notification_routing_override_kind_key",
            ),
        ),
        migrations.AddIndex(
            model_name="notificationroutingoverride",
            index=models.Index(fields=["kind", "key"], name="notif_route_override_kind_key"),
        ),
        migrations.AddIndex(
            model_name="notificationroutingoverride",
            index=models.Index(
                fields=["kind", "is_active"],
                name="notif_route_ovr_kind_act",
            ),
        ),
    ]
