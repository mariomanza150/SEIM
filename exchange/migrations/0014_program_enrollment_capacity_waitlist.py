from django.db import migrations, models


def ensure_waitlist_status(apps, schema_editor):
    ApplicationStatus = apps.get_model("exchange", "ApplicationStatus")
    ApplicationStatus.objects.get_or_create(
        name="waitlist",
        defaults={"order": 15},
    )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("exchange", "0013_alter_application_dynamic_form_current_step"),
    ]

    operations = [
        migrations.AddField(
            model_name="program",
            name="enrollment_capacity",
            field=models.PositiveIntegerField(
                blank=True,
                help_text=(
                    "Maximum number of seat-holding applications (submitted / under review / "
                    "approved / completed). Leave blank for no limit."
                ),
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="program",
            name="waitlist_when_full",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "When capacity is full, new submissions are placed on the waitlist instead "
                    "of being rejected."
                ),
            ),
        ),
        migrations.RunPython(ensure_waitlist_status, noop_reverse),
    ]
