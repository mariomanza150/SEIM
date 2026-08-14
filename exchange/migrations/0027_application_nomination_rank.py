from django.db import migrations, models


def ensure_nominated_status(apps, schema_editor):
    ApplicationStatus = apps.get_model("exchange", "ApplicationStatus")
    ApplicationStatus.objects.get_or_create(
        name="nominated",
        defaults={"order": 16},
    )


def noop(apps, schema_editor):
    return None


class Migration(migrations.Migration):
    dependencies = [
        ("exchange", "0026_scholarship_award_and_partner_contact"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="nomination_rank",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Staff ranking for nomination matching (lower is higher priority).",
                null=True,
            ),
        ),
        migrations.RunPython(ensure_nominated_status, noop),
    ]
