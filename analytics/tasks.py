from celery import shared_task
from django.utils import timezone

from analytics.models import Metric, Report
from exchange.models import Application


@shared_task
def generate_report(report_id):
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
