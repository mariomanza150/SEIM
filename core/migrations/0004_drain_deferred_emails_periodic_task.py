from django.db import migrations


def forwards(apps, schema_editor):
    CrontabSchedule = apps.get_model("django_celery_beat", "CrontabSchedule")
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")

    every_5, _ = CrontabSchedule.objects.get_or_create(
        minute="*/5",
        hour="*",
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
    )
    PeriodicTask.objects.update_or_create(
        name="drain-deferred-emails",
        defaults={
            "task": "core.tasks.drain_deferred_emails",
            "crontab": every_5,
            "interval": None,
            "solar": None,
            "clocked": None,
            "enabled": True,
        },
    )


def backwards(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    PeriodicTask.objects.filter(name="drain-deferred-emails").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_email_quota_and_deferred_outbox"),
        ("django_celery_beat", "0019_alter_periodictasks_options"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
