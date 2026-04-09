from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_usersettings_notification_digest"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="additional_languages",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='Other languages and CEFR levels, e.g. [{"name": "German", "level": "B2"}].',
            ),
        ),
    ]
