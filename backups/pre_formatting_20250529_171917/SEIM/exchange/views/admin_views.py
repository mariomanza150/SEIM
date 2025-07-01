"""
Administrative views for the exchange application.
Handles administrative tasks like pending approvals and staff-specific functionality.
"""

from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.shortcuts import render

from ..models import Exchange


@login_required
@permission_required("exchange.can_review_exchange", raise_exception=True)
def pending_approvals(request):
    """View function for listing pending exchange applications"""
    pending_exchanges = Exchange.objects.filter(
        status__in=["SUBMITTED", "UNDER_REVIEW"]
    )

    # Apply filters if provided
    status_filter = request.GET.get("status")
    if status_filter and status_filter != "all":
        pending_exchanges = pending_exchanges.filter(status=status_filter)

    search_query = request.GET.get("q")
    if search_query:
        pending_exchanges = pending_exchanges.filter(
            Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(destination_university__icontains=search_query)
            | Q(destination_country__icontains=search_query)
        )

    # Order by submission date by default
    order_by = request.GET.get("order_by", "submission_date")
    pending_exchanges = pending_exchanges.order_by(order_by)

    return render(
        request,
        "exchange/pending_approvals.html",
        {
            "exchanges": pending_exchanges,
            "current_status": status_filter or "all",
            "search_query": search_query or "",
            "current_order": order_by,
        },
    )
