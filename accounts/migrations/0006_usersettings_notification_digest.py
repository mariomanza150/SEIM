from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_usersettings_high_contrast_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="usersettings",
            name="email_notification_digest",
            field=models.BooleanField(
                default=False,
                help_text="Also email the digest when system email is enabled.",
            ),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="notification_digest_frequency",
            field=models.CharField(
                choices=[
                    ("off", "Off"),
                    ("daily", "Daily"),
                    ("weekly", "Weekly"),
                ],
                default="off",
                help_text="Summarize unread in-app notifications on a schedule.",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="usersettings",
            name="notification_digest_last_sent_at",
            field=models.DateTimeField(
                blank=True,
                editable=False,
                help_text="Last digest sent (managed by the digest task).",
                null=True,
            ),
        ),
    ]
