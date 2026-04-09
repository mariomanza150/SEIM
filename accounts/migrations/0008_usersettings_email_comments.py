# Generated manually for SEIM — separate comment email channel from document email.

from django.db import migrations, models


def sync_email_comments_from_documents(apps, schema_editor):
    UserSettings = apps.get_model("accounts", "UserSettings")
    for row in UserSettings.objects.iterator():
        row.email_comments = row.email_documents
        row.save(update_fields=["email_comments"])


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0007_profile_additional_languages"),
    ]

    operations = [
        migrations.AddField(
            model_name="usersettings",
            name="email_comments",
            field=models.BooleanField(
                default=True,
                help_text="Email notifications for comments (application/document threads)",
            ),
        ),
        migrations.RunPython(sync_email_comments_from_documents, migrations.RunPython.noop),
    ]
