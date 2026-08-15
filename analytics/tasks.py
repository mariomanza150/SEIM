from celery import shared_task
from django.utils import timezone

from analytics.models import Metric, Report
from core.celery_utils import log_celery_failure, retryable_task_kwargs
from exchange.models import Application


@shared_task(on_failure=log_celery_failure, **retryable_task_kwargs())
def generate_report(self, report_id):
    report = Report.objects.get(id=report_id)
    for status in ["submitted", "approved", "rejected"]:
        count = Application.objects.filter(status__name=status).count()
        Metric.objects.create(
            report=report,
            name=f"applications_{status}",
            value=count,
            calculated_at=timezone.now(),
        )
    report.generated_at = timezone.now()
    report.save()
