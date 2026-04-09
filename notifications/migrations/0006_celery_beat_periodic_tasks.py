from django.db import migrations


def forwards(apps, schema_editor):
    CrontabSchedule = apps.get_model("django_celery_beat", "CrontabSchedule")
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")

    every_15, _ = CrontabSchedule.objects.get_or_create(
        minute="*/15",
        hour="*",
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
    )
    PeriodicTask.objects.update_or_create(
        name="send-deadline-reminders",
        defaults={
            "task": "notifications.tasks.send_deadline_reminders",
            "crontab": every_15,
            "interval": None,
            "solar": None,
            "clocked": None,
            "enabled": True,
        },
    )

    daily_0715, _ = CrontabSchedule.objects.get_or_create(
        minute="15",
        hour="7",
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
    )
    PeriodicTask.objects.update_or_create(
        name="send-agreement-expiration-reminders",
        defaults={
            "task": "notifications.tasks.send_agreement_expiration_reminders",
            "crontab": daily_0715,
            "interval": None,
            "solar": None,
            "clocked": None,
            "enabled": True,
        },
    )


def backwards(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    PeriodicTask.objects.filter(
        name__in=(
            "send-deadline-reminders",
            "send-agreement-expiration-reminders",
        )
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0005_reminder_notification_category_and_more"),
        ("django_celery_beat", "0019_alter_periodictasks_options"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
