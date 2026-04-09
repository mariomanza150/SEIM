from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_usersettings_high_contrast_and_more"),
        ("exchange", "0007_program_application_window"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="assigned_coordinator",
            field=models.ForeignKey(
                blank=True,
                help_text="Coordinator explicitly assigned to review this application.",
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name="assigned_applications",
                to="accounts.user",
            ),
        ),
        migrations.AddField(
            model_name="program",
            name="coordinators",
            field=models.ManyToManyField(
                blank=True,
                help_text="Coordinators responsible for this program.",
                related_name="coordinated_programs",
                to="accounts.user",
            ),
        ),
    ]
