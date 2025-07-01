"""
Dashboard views for the exchange application.
Provides overview and summary functionality for users.
"""

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

from ..models import Exchange, WorkflowLog
from ..services.analytics import AnalyticsService


@login_required
def dashboard(request):
    """View function for the dashboard page"""
    user = request.user

    # Get user's exchanges or all exchanges for staff/coordinators
    if user.is_staff or hasattr(user, "profile") and user.profile.role in ["COORDINATOR", "ADMINISTRATOR"]:
        # For staff, show recent exchanges
        exchanges = Exchange.objects.all().order_by("-updated_at")[:10]
        total_exchanges = Exchange.objects.count()
        active_exchanges = Exchange.objects.filter(status__in=["SUBMITTED", "UNDER_REVIEW", "APPROVED"]).count()
        pending_exchanges = Exchange.objects.filter(status__in=["SUBMITTED", "UNDER_REVIEW"]).count()
        completed_exchanges = Exchange.objects.filter(status="COMPLETED").count()
    else:
        # For students, show only their exchanges
        exchanges = Exchange.objects.filter(student=user).order_by("-updated_at")
        total_exchanges = exchanges.count()
        active_exchanges = exchanges.filter(status__in=["SUBMITTED", "UNDER_REVIEW", "APPROVED"]).count()
        pending_exchanges = exchanges.filter(status__in=["SUBMITTED", "UNDER_REVIEW"]).count()
        completed_exchanges = exchanges.filter(status="COMPLETED").count()

    context = {
        "recent_exchanges": exchanges,
        "total_exchanges": total_exchanges,
        "active_exchanges": active_exchanges,
        "pending_exchanges": pending_exchanges,
        "completed_exchanges": completed_exchanges,
    }

    # For staff, add some quick stats
    if user.is_staff or hasattr(user, "profile") and user.profile.role in ["COORDINATOR", "ADMINISTRATOR"]:
        context["recent_activity"] = WorkflowLog.objects.all().order_by("-timestamp")[:5]
        context["status_summary"] = AnalyticsService.get_exchange_status_summary()

    return render(request, "exchange/dashboard.html", context)
