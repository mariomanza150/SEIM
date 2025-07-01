"""
Views for batch processing functionality.
"""

from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.text import slugify
from django.views.decorators.http import require_POST

from ..models import Document, Exchange
from ..services.batch_processor import BatchProcessor


@login_required
@permission_required("exchange.can_approve_exchange", raise_exception=True)
def batch_processing(request):
    """View for batch processing dashboard"""
    context = {
        "status_choices": Exchange.STATUS_CHOICES,
        "document_types": Document.DOCUMENT_TYPES,
    }

    # Add results if available in session
    if "batch_results" in request.session:
        context["results"] = request.session["batch_results"]
        del request.session["batch_results"]

    return render(request, "exchange/batch_processing.html", context)


@login_required
@permission_required("exchange.can_approve_exchange", raise_exception=True)
@require_POST
def batch_status_update(request):
    """View for updating status of multiple exchanges"""
    # Get parameters
    status_filter = request.POST.get("status_filter")
    new_status = request.POST.get("new_status")
    comment = request.POST.get("comment", "")
    confirmation = request.POST.get("confirmation") == "on"

    # Validate input
    if not status_filter or not new_status:
        messages.error(request, "Status filter and new status are required.")
        return redirect("exchange:batch-processing")

    if not confirmation:
        messages.error(request, "Please confirm the batch action.")
        return redirect("exchange:batch-processing")

    # Get matching exchanges
    exchanges = Exchange.objects.filter(status=status_filter)

    if not exchanges.exists():
        messages.warning(request, f"No exchanges found with status: {status_filter}")
        return redirect("exchange:batch-processing")

    # Process batch
    results = BatchProcessor.bulk_status_update(
        exchanges=exchanges, new_status=new_status, user=request.user, comment=comment
    )

    # Store results in session for display
    request.session["batch_results"] = results

    # Generate message
    if results["success_count"] > 0:
        messages.success(
            request,
            f"Status updated for {results['success_count']} out of {results['total']} exchanges.",
        )
    if results["failure_count"] > 0:
        messages.warning(
            request,
            f"Failed to update {results['failure_count']} exchanges. See details below.",
        )

    return redirect("exchange:batch-processing")


@login_required
@permission_required("exchange.can_verify_documents", raise_exception=True)
@require_POST
def batch_document_verification(request):
    """View for verifying multiple documents at once"""
    # Get parameters
    document_category = request.POST.get("document_category")
    verification_action = request.POST.get("verification_action")
    notes = request.POST.get("notes", "")
    confirmation = request.POST.get("doc_confirmation") == "on"

    # Validate input
    if not document_category or not verification_action:
        messages.error(request, "Document category and action are required.")
        return redirect("exchange:batch-processing")

    if not confirmation:
        messages.error(request, "Please confirm the batch action.")
        return redirect("exchange:batch-processing")

    # Get matching documents
    documents = Document.objects.filter(category=document_category, status="PENDING")

    if not documents.exists():
        messages.warning(request, f"No pending documents found in category: {document_category}")
        return redirect("exchange:batch-processing")

    # Process batch
    is_verified = verification_action == "verify"
    results = BatchProcessor.bulk_document_verification(
        documents=documents, is_verified=is_verified, user=request.user, notes=notes
    )

    # Store results in session for display
    request.session["batch_results"] = results

    # Generate message
    action_text = "verified" if is_verified else "rejected"
    if results["success_count"] > 0:
        messages.success(
            request,
            f"{results['success_count']} out of {results['total']} documents {action_text}.",
        )
    if results["failure_count"] > 0:
        messages.warning(
            request,
            f"Failed to process {results['failure_count']} documents. See details below.",
        )

    return redirect("exchange:batch-processing")


@login_required
@permission_required("exchange.can_approve_exchange", raise_exception=True)
@require_POST
def import_csv(request):
    """View for importing exchanges from CSV"""
    if "csv_file" not in request.FILES:
        messages.error(request, "CSV file is required.")
        return redirect("exchange:batch-processing")

    csv_file = request.FILES["csv_file"]

    # Check file type
    if not csv_file.name.endswith(".csv"):
        messages.error(request, "File must be a CSV file.")
        return redirect("exchange:batch-processing")

    # Process import
    results = BatchProcessor.import_exchanges_from_csv(csv_file=csv_file, user=request.user)

    # Store results in session for display
    request.session["batch_results"] = results

    # Generate message
    if results["created_count"] > 0:
        messages.success(
            request,
            f"Successfully imported {results['created_count']} out of {results['total']} exchanges.",
        )
    if results["failed_count"] > 0:
        messages.warning(
            request,
            f"Failed to import {results['failed_count']} rows. See details below.",
        )

    return redirect("exchange:batch-processing")


@login_required
@permission_required("exchange.can_approve_exchange", raise_exception=True)
def download_csv_template(request):
    """View for downloading CSV import template"""
    # Create a simple CSV template with header row
    csv_header = (
        "first_name,last_name,email,phone,current_university,current_program,"
        "student_number,destination_university,destination_country,exchange_program,"
        "start_date,end_date,gpa,motivation_letter"
    )

    # Create template response
    timestamp = datetime.now().strftime("%Y%m%d")
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="exchange_import_template_{timestamp}.csv"'

    # Write header and a sample row
    response.write(csv_header + "\n")
    response.write(
        "John,Doe,john.doe@example.com,+1234567890,Home University,Computer Science,"
        "S12345,Host University,Country,Semester Exchange,"
        "2024-09-01,2025-01-31,3.5,I am excited about this opportunity..."
    )

    return response


@login_required
@permission_required("exchange.can_approve_exchange", raise_exception=True)
def export_csv(request):
    """View for exporting exchanges to CSV"""
    # Get parameters
    status_filter = request.GET.get("status")

    # Get exchanges
    exchanges = Exchange.objects.all()
    if status_filter and status_filter != "all":
        exchanges = exchanges.filter(status=status_filter)

    # Process export
    csv_data = BatchProcessor.export_exchanges_to_csv(exchanges)

    # Create response
    timestamp = datetime.now().strftime("%Y%m%d")
    status_slug = slugify(status_filter) if status_filter else "all"
    filename = f"exchanges_{status_slug}_{timestamp}.csv"

    response = HttpResponse(csv_data, content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response


@login_required
@permission_required("exchange.can_approve_exchange", raise_exception=True)
@require_POST
def batch_notifications(request):
    """View for sending batch notifications"""
    # Get parameters
    notification_status = request.POST.get("notification_status")
    notification_type = request.POST.get("notification_type")
    confirmation = request.POST.get("notification_confirmation") == "on"

    # Validate input
    if not notification_status or not notification_type:
        messages.error(request, "Status and notification type are required.")
        return redirect("exchange:batch-processing")

    if not confirmation:
        messages.error(request, "Please confirm sending notifications.")
        return redirect("exchange:batch-processing")

    # Get matching exchanges
    exchanges = Exchange.objects.filter(status=notification_status)

    if not exchanges.exists():
        messages.warning(request, f"No exchanges found with status: {notification_status}")
        return redirect("exchange:batch-processing")

    # Map notification types
    notification_map = {
        "reminder": "submission",
        "document_request": "submission",
        "deadline": "submission",
    }

    # Process batch
    results = BatchProcessor.send_batch_notifications(
        exchanges=exchanges,
        notification_type=notification_map.get(notification_type, "submission"),
    )

    # Store results in session for display
    request.session["batch_results"] = results

    # Generate message
    if results["success_count"] > 0:
        messages.success(
            request,
            f"Notifications sent to {results['success_count']} out of {results['total']} recipients.",
        )
    if results["failure_count"] > 0:
        messages.warning(
            request,
            f"Failed to send {results['failure_count']} notifications. See details below.",
        )

    return redirect("exchange:batch-processing")
