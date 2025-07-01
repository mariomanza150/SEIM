"""
Celery configuration for the SEIM project.
"""

import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seim.settings")

app = Celery("seim")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    "check-document-expiration": {
        "task": "exchange.tasks.check_document_expiration",
        "schedule": crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
    "generate-integrity-report": {
        "task": "exchange.tasks.generate_integrity_report",
        "schedule": crontab(day_of_week=1, hour=9, minute=0),  # Run weekly on Monday at 9 AM
    },
    "cleanup-orphaned-files": {
        "task": "exchange.tasks.cleanup_orphaned_files",
        "schedule": crontab(day_of_week=0, hour=3, minute=0),  # Run weekly on Sunday at 3 AM
    },
}

# Celery configuration
app.conf.update(
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_max_tasks_per_child=100,
    result_expires=3600,
)


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f"Request: {self.request!r}")
