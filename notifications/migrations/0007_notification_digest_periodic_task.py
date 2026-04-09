from django.db import migrations


def forwards(apps, schema_editor):
    CrontabSchedule = apps.get_model("django_celery_beat", "CrontabSchedule")
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")

    daily_0830, _ = CrontabSchedule.objects.get_or_create(
        minute="30",
        hour="8",
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
    )
    PeriodicTask.objects.update_or_create(
        name="send-notification-digests",
        defaults={
            "task": "notifications.tasks.send_notification_digests",
            "crontab": daily_0830,
            "interval": None,
            "solar": None,
            "clocked": None,
            "enabled": True,
        },
    )


def backwards(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    PeriodicTask.objects.filter(name="send-notification-digests").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0006_celery_beat_periodic_tasks"),
        ("django_celery_beat", "0019_alter_periodictasks_options"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
