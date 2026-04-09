import os

from celery import Celery
from celery.schedules import crontab

# Match manage.py so workers/beat load full settings when DJANGO_SETTINGS_MODULE is unset.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seim.settings.development")

app = Celery("seim")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Used by the default Celery beat scheduler (e.g. docker-compose dev). Production uses
# django_celery_beat DatabaseScheduler; see notifications migration that seeds PeriodicTask rows.
app.conf.beat_schedule = {
    "send-deadline-reminders": {
        "task": "notifications.tasks.send_deadline_reminders",
        "schedule": crontab(minute="*/15"),
        "options": {"expires": 600},
    },
    "send-agreement-expiration-reminders": {
        "task": "notifications.tasks.send_agreement_expiration_reminders",
        "schedule": crontab(hour=7, minute=15),
        "options": {"expires": 3600},
    },
    "send-notification-digests": {
        "task": "notifications.tasks.send_notification_digests",
        "schedule": crontab(hour=8, minute=30),
        "options": {"expires": 3600},
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery functionality."""
    import logging

    logger = logging.getLogger(__name__)
    logger.debug("Request: %r", self.request)
