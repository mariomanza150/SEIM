# Generated manually — decouple program in-app notifications from application in-app.

from django.db import migrations, models


def sync_inapp_programs_from_applications(apps, schema_editor):
    UserSettings = apps.get_model("accounts", "UserSettings")
    for row in UserSettings.objects.iterator():
        row.inapp_programs = row.inapp_applications
        row.save(update_fields=["inapp_programs"])


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0008_usersettings_email_comments"),
    ]

    operations = [
        migrations.AddField(
            model_name="usersettings",
            name="inapp_programs",
            field=models.BooleanField(
                default=True,
                help_text="In-app notifications for new programs and program announcements",
            ),
        ),
        migrations.RunPython(sync_inapp_programs_from_applications, migrations.RunPython.noop),
    ]
