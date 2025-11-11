"""
SEIM Celery Configuration
Enhanced configuration for background task processing and performance optimization
"""

import os

from celery import Celery
from celery.schedules import crontab
from django.utils import timezone

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seim.settings.development")

# Create the Celery app
app = Celery("seim")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Performance and optimization settings
app.conf.update(
    # Task routing and queues
    task_routes={
        "analytics.tasks.*": {"queue": "analytics"},
        "notifications.tasks.*": {"queue": "notifications"},
        "documents.tasks.*": {"queue": "documents"},
        "exchange.tasks.*": {"queue": "exchange"},
        "core.tasks.*": {"queue": "default"},
    },
    # Task execution settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Performance optimizations
    worker_prefetch_multiplier=1,  # Prevent worker from prefetching too many tasks
    task_acks_late=True,  # Acknowledge task only after completion
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
    worker_max_memory_per_child=200000,  # Restart worker after 200MB memory usage
    # Result backend settings
    result_backend="django-db",  # Use database for result storage
    result_expires=3600,  # Results expire after 1 hour
    # Task execution timeouts
    task_soft_time_limit=300,  # 5 minutes soft timeout
    task_time_limit=600,  # 10 minutes hard timeout
    # Rate limiting
    task_annotations={
        "*": {
            "rate_limit": "100/m",  # 100 tasks per minute per worker
        },
        "analytics.tasks.generate_report": {
            "rate_limit": "10/m",  # 10 reports per minute
        },
        "notifications.tasks.send_email": {
            "rate_limit": "50/m",  # 50 emails per minute
        },
    },
    # Monitoring and logging
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s",
    # Error handling
    task_reject_on_worker_lost=True,  # Reject tasks if worker is lost
    task_remote_tracebacks=True,  # Include tracebacks in results
)


# Periodic tasks (beat schedule)
app.conf.beat_schedule = {
    # Analytics tasks
    "generate-daily-analytics": {
        "task": "analytics.tasks.generate_daily_report",
        "schedule": crontab(hour=1, minute=0),  # Daily at 1 AM
        "options": {"queue": "analytics"},
    },
    "generate-weekly-analytics": {
        "task": "analytics.tasks.generate_weekly_report",
        "schedule": crontab(
            day_of_week=1, hour=2, minute=0
        ),  # Weekly on Monday at 2 AM
        "options": {"queue": "analytics"},
    },
    "generate-monthly-analytics": {
        "task": "analytics.tasks.generate_monthly_report",
        "schedule": crontab(day=1, hour=3, minute=0),  # Monthly on 1st at 3 AM
        "options": {"queue": "analytics"},
    },
    # Notification tasks
    "send-daily-notifications": {
        "task": "notifications.tasks.send_daily_digest",
        "schedule": crontab(hour=8, minute=0),  # Daily at 8 AM
        "options": {"queue": "notifications"},
    },
    "send-reminder-notifications": {
        "task": "notifications.tasks.send_reminders",
        "schedule": crontab(hour=9, minute=0),  # Daily at 9 AM
        "options": {"queue": "notifications"},
    },
    # Document tasks
    "process-document-validations": {
        "task": "documents.tasks.process_pending_validations",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
        "options": {"queue": "documents"},
    },
    "cleanup-expired-documents": {
        "task": "documents.tasks.cleanup_expired_documents",
        "schedule": crontab(hour=4, minute=0),  # Daily at 4 AM
        "options": {"queue": "documents"},
    },
    # Exchange tasks
    "update-application-statuses": {
        "task": "exchange.tasks.update_application_statuses",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
        "options": {"queue": "exchange"},
    },
    "process-bulk-actions": {
        "task": "exchange.tasks.process_bulk_actions",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
        "options": {"queue": "exchange"},
    },
    # System maintenance tasks
    "cleanup-old-tasks": {
        "task": "core.tasks.cleanup_old_tasks",
        "schedule": crontab(hour=5, minute=0),  # Daily at 5 AM
        "options": {"queue": "default"},
    },
    "update-cache-statistics": {
        "task": "core.tasks.update_cache_statistics",
        "schedule": crontab(minute="*/10"),  # Every 10 minutes
        "options": {"queue": "default"},
    },
    "health-check": {
        "task": "core.tasks.health_check",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
        "options": {"queue": "default"},
    },
}


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery configuration"""
    print(f"Request: {self.request!r}")


# Task monitoring and error handling
@app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
def retry_task(self, task_name, *args, **kwargs):
    """Generic retry task wrapper"""
    try:
        # Import and execute the actual task
        module_name, func_name = task_name.rsplit(".", 1)
        module = __import__(module_name, fromlist=[func_name])
        task_func = getattr(module, func_name)

        return task_func(*args, **kwargs)
    except Exception as exc:
        # Log the error and retry
        self.retry(exc=exc, countdown=60)  # Retry after 1 minute


# Performance monitoring tasks
@app.task
def monitor_task_performance():
    """Monitor task performance and log statistics"""
    from celery.task.control import inspect

    i = inspect()

    # Get active tasks
    active = i.active()
    if active:
        print(f"Active tasks: {len(active)}")
        for worker, tasks in active.items():
            print(f"  {worker}: {len(tasks)} tasks")

    # Get reserved tasks
    reserved = i.reserved()
    if reserved:
        print(f"Reserved tasks: {len(reserved)}")
        for worker, tasks in reserved.items():
            print(f"  {worker}: {len(tasks)} tasks")

    # Get registered tasks
    registered = i.registered()
    if registered:
        print(f"Registered tasks: {len(registered)}")
        for worker, tasks in registered.items():
            print(f"  {worker}: {len(tasks)} tasks")


@app.task
def cleanup_failed_tasks():
    """Clean up failed tasks older than 24 hours"""
    from datetime import timedelta

    from django.utils import timezone
    from django_celery_results.models import TaskResult

    cutoff_time = timezone.now() - timedelta(hours=24)

    # Delete failed tasks older than 24 hours
    deleted_count = TaskResult.objects.filter(
        status="FAILURE", date_done__lt=cutoff_time
    ).delete()[0]

    print(f"Cleaned up {deleted_count} failed tasks")


# Queue management tasks
@app.task
def monitor_queue_sizes():
    """Monitor queue sizes and log statistics"""
    from celery.task.control import inspect

    i = inspect()

    # Get queue statistics
    stats = i.stats()
    if stats:
        for worker, worker_stats in stats.items():
            print(f"Worker {worker}:")
            print(
                f"  Pool: {worker_stats.get('pool', {}).get('max-concurrency', 'N/A')}"
            )
            print(
                f"  Processed: {worker_stats.get('total', {}).get('processed', 'N/A')}"
            )
            print(f"  Memory: {worker_stats.get('total', {}).get('memory', 'N/A')}")


@app.task
def purge_queues():
    """Purge all queues (use with caution)"""
    from celery.task.control import discard_all

    result = discard_all()
    print(f"Purged all queues: {result}")


# Health check task
@app.task
def health_check():
    """Perform system health check"""

    import psutil

    # Check system resources
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    health_status = {
        "timestamp": timezone.now().isoformat(),
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
        "disk_percent": disk.percent,
        "status": "healthy" if cpu_percent < 90 and memory.percent < 90 else "warning",
    }

    # Log health status
    print(f"Health check: {health_status}")

    return health_status


# Task result monitoring
@app.task
def monitor_task_results():
    """Monitor task results and performance"""
    from datetime import timedelta

    from django.utils import timezone
    from django_celery_results.models import TaskResult

    # Get statistics for the last hour
    one_hour_ago = timezone.now() - timedelta(hours=1)

    stats = {
        "total": TaskResult.objects.filter(date_done__gte=one_hour_ago).count(),
        "success": TaskResult.objects.filter(
            date_done__gte=one_hour_ago, status="SUCCESS"
        ).count(),
        "failure": TaskResult.objects.filter(
            date_done__gte=one_hour_ago, status="FAILURE"
        ).count(),
        "pending": TaskResult.objects.filter(
            date_done__gte=one_hour_ago, status="PENDING"
        ).count(),
    }

    # Calculate success rate
    if stats["total"] > 0:
        stats["success_rate"] = (stats["success"] / stats["total"]) * 100
    else:
        stats["success_rate"] = 0

    print(f"Task results (last hour): {stats}")
    return stats
