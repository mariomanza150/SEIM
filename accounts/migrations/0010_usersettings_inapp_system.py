# Generated manually — in-app toggle for system-category notifications.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0009_usersettings_inapp_programs"),
    ]

    operations = [
        migrations.AddField(
            model_name="usersettings",
            name="inapp_system",
            field=models.BooleanField(
                default=True,
                help_text="In-app notifications for system messages (e.g. agreement reminders)",
            ),
        ),
    ]
