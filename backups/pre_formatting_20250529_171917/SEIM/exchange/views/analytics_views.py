import csv
from datetime import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import render

from ..services.analytics import AnalyticsService


@login_required
@permission_required("exchange.can_view_analytics", raise_exception=True)
def analytics_view(request):
    """View function for analytics dashboard"""
    # Collect all stats
    stats = {
        "status_summary": AnalyticsService.get_exchange_status_summary(),
        "monthly_applications": AnalyticsService.get_monthly_applications(),
        "universities": AnalyticsService.get_applications_by_university(),
        "countries": AnalyticsService.get_applications_by_country(),
        "processing_time": AnalyticsService.get_processing_time_metrics(),
        "approval_rate": AnalyticsService.get_approval_rate(period_days=30),
        "documents": AnalyticsService.get_document_statistics(),
        "activity": AnalyticsService.generate_activity_report(days=30),
    }

    return render(request, "exchange/analytics.html", {"stats": stats})


@login_required
@permission_required("exchange.can_export_reports", raise_exception=True)
def export_report_view(request):
    """View function for exporting analytics reports as CSV"""
    # Get filter parameters
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    status = request.GET.get("status")

    # Parse date strings if provided
    if start_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    # Get data from service
    exchanges = AnalyticsService.export_exchange_data(
        start_date=start_date, end_date=end_date, status=status
    )

    # Create CSV response
    response = HttpResponse(content_type="text/csv")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    response["Content-Disposition"] = (
        f'attachment; filename="exchange_report_{timestamp}.csv"'
    )

    writer = csv.writer(response)

    # Write header row
    writer.writerow(
        [
            "ID",
            "Student",
            "Email",
            "Current University",
            "Destination University",
            "Destination Country",
            "Start Date",
            "End Date",
            "Status",
            "Created At",
            "Submitted At",
            "Decision Date",
            "Reviewed By",
            "Has Required Documents",
        ]
    )

    # Write data rows
    for exchange in exchanges:
        writer.writerow(
            [
                exchange.id,
                f"{exchange.first_name} {exchange.last_name}",
                exchange.email,
                exchange.current_university,
                exchange.destination_university,
                exchange.destination_country,
                exchange.start_date,
                exchange.end_date,
                exchange.get_status_display(),
                exchange.created_at.strftime("%Y-%m-%d"),
                (
                    exchange.submission_date.strftime("%Y-%m-%d")
                    if exchange.submission_date
                    else ""
                ),
                (
                    exchange.decision_date.strftime("%Y-%m-%d")
                    if exchange.decision_date
                    else ""
                ),
                exchange.reviewed_by.username if exchange.reviewed_by else "",
                "Yes" if exchange.has_required_documents() else "No",
            ]
        )

    return response
