"""
Fixed Exchange CRUD views for the exchange application.
Handles listing, creating, reading, updating exchange applications with proper error handling.
"""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..forms import ExchangeForm
from ..models import Comment, Exchange, WorkflowLog
from ..services.workflow import WorkflowService

logger = logging.getLogger(__name__)


@login_required
def exchange_list(request):
    """View function for listing exchanges with proper filtering"""
    user = request.user

    # Determine which exchanges to show based on user role
    if user.is_staff or (
        hasattr(user, "profile")
        and user.profile.role in ["COORDINATOR", "ADMINISTRATOR"]
    ):
        # Staff can see all exchanges
        exchanges = Exchange.objects.select_related("student").all()
    else:
        # Students see only their own exchanges
        exchanges = Exchange.objects.filter(student=user)

    # Apply filters if provided
    status_filter = request.GET.get("status")
    if status_filter and status_filter != "all":
        exchanges = exchanges.filter(status=status_filter)

    search_query = request.GET.get("q")
    if search_query:
        exchanges = exchanges.filter(
            Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(destination_university__icontains=search_query)
            | Q(destination_country__icontains=search_query)
        )

    # Order by updated_at by default
    order_by = request.GET.get("order_by", "-updated_at")
    exchanges = exchanges.order_by(order_by)

    return render(
        request,
        "exchange/exchange_list.html",
        {
            "exchanges": exchanges,
            "status_choices": Exchange.STATUS_CHOICES,
            "current_status": status_filter or "all",
            "search_query": search_query or "",
            "current_order": order_by,
        },
    )


@login_required
def exchange_detail(request, pk):
    """View function for exchange details with proper permission checking"""
    exchange = get_object_or_404(Exchange, id=pk)

    # Check permission
    if not (
        exchange.student == request.user
        or request.user.is_staff
        or (
            hasattr(request.user, "profile")
            and request.user.profile.role in ["COORDINATOR", "ADMINISTRATOR"]
        )
    ):
        messages.error(request, "You don't have permission to view this exchange.")
        return redirect("exchange:dashboard")

    # Get documents
    documents = exchange.documents.all()

    # Get workflow history
    workflow_history = WorkflowService.get_workflow_history(exchange)

    # Get available transitions for current user
    available_transitions = WorkflowService.get_available_transitions(
        exchange, request.user
    )

    # Get comments
    comments = exchange.comments.select_related("author").order_by("-created_at")

    return render(
        request,
        "exchange/exchange_detail.html",
        {
            "exchange": exchange,
            "documents": documents,
            "workflow_history": workflow_history,
            "available_transitions": available_transitions,
            "comments": comments,
        },
    )


@login_required
def create_exchange(request):
    """Fixed and simplified exchange creation view with robust error handling"""
    logger.info(f"Exchange creation started by user {request.user.username}")

    if request.method == "POST":
        form = ExchangeForm(request.POST, user=request.user)
        action = request.POST.get("action", "submit")

        if form.is_valid():
            try:
                with transaction.atomic():
                    exchange = form.save(commit=False)
                    exchange.student = request.user

                    # Set status based on action
                    if action == "draft":
                        exchange.status = "DRAFT"
                        logger.info(
                            f"Saving exchange as draft for user {request.user.username}"
                        )
                    elif action == "submit":
                        # Validate before submission
                        exchange.status = (
                            "DRAFT"  # Temporarily set to draft for validation
                        )
                        exchange.save()  # Save first so we can validate with ID

                        can_submit, reason = WorkflowService.can_submit(exchange)
                        if not can_submit:
                            messages.error(
                                request, f"Cannot submit application: {reason}"
                            )
                            logger.warning(
                                f"Submission validation failed for user {request.user.username}: {reason}"
                            )
                            return render(
                                request,
                                "exchange/exchange_form.html",
                                {"form": form, "action": "create"},
                            )

                        exchange.status = "SUBMITTED"
                        exchange.submission_date = timezone.now()
                        logger.info(
                            f"Submitting exchange for user {request.user.username}"
                        )
                    else:
                        exchange.status = "DRAFT"  # Default to draft

                    exchange.save()

                    # Log the action
                    WorkflowLog.objects.create(
                        exchange=exchange,
                        user=request.user,
                        from_status="NEW",
                        to_status=exchange.status,
                        comment=f"Application {'submitted' if action == 'submit' else 'saved as draft'}",
                    )

                    # Send notifications for submission
                    if action == "submit":
                        try:
                            from ..services.notification import \
                                NotificationService

                            NotificationService.send_submission_confirmation(exchange)
                        except Exception as e:
                            logger.error(
                                f"Failed to send submission notification: {str(e)}"
                            )
                            # Don't fail the entire process for notification issues

                    success_message = f"Application {'submitted' if action == 'submit' else 'saved as draft'} successfully!"
                    messages.success(request, success_message)
                    logger.info(
                        f"Exchange {exchange.id} created successfully by {request.user.username}"
                    )

                    # Handle AJAX vs regular form submission
                    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                        return JsonResponse(
                            {
                                "success": True,
                                "exchange_id": exchange.id,
                                "message": success_message,
                                "status": exchange.status,
                                "redirect_url": f"/exchanges/{exchange.id}/",
                            }
                        )
                    else:
                        return redirect("exchange:exchange-detail", pk=exchange.id)

            except Exception as e:
                logger.error(
                    f"Exchange creation failed for user {request.user.username}: {str(e)}"
                )
                error_message = f"Error creating application: {str(e)}"

                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return JsonResponse(
                        {"success": False, "error": error_message}, status=400
                    )
                else:
                    messages.error(request, error_message)
        else:
            # Form validation failed
            logger.warning(
                f"Form validation failed for user {request.user.username}: {form.errors}"
            )
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {"success": False, "errors": form.errors}, status=400
                )
            else:
                messages.error(request, "Please correct the errors below.")
    else:
        # GET request - show empty form
        form = ExchangeForm(user=request.user)

    return render(
        request,
        "exchange/exchange_form.html",
        {
            "form": form,
            "action": "create",
        },
    )


@login_required
def edit_exchange(request, pk):
    """Fixed exchange editing view with proper validation"""
    exchange = get_object_or_404(Exchange, id=pk)

    # Check permission
    if not (exchange.student == request.user or request.user.is_staff):
        messages.error(request, "You don't have permission to edit this exchange.")
        return redirect("exchange:dashboard")

    # Only draft exchanges can be edited
    if exchange.status != "DRAFT":
        messages.error(request, "Only draft applications can be edited.")
        return redirect("exchange:exchange-detail", pk=exchange.id)

    if request.method == "POST":
        form = ExchangeForm(request.POST, instance=exchange, user=request.user)
        action = request.POST.get("action", "save")

        if form.is_valid():
            try:
                with transaction.atomic():
                    exchange = form.save(commit=False)
                    exchange.student = request.user

                    # Set status based on action
                    if action == "submit":
                        # Validate before submission
                        exchange.save()  # Save first for validation

                        can_submit, reason = WorkflowService.can_submit(exchange)
                        if not can_submit:
                            messages.error(
                                request, f"Cannot submit application: {reason}"
                            )
                            return render(
                                request,
                                "exchange/exchange_form.html",
                                {"form": form, "action": "edit", "exchange": exchange},
                            )

                        exchange.status = "SUBMITTED"
                        exchange.submission_date = timezone.now()
                    else:
                        exchange.status = "DRAFT"

                    exchange.save()

                    # Log the update
                    WorkflowLog.objects.create(
                        exchange=exchange,
                        user=request.user,
                        from_status="DRAFT",
                        to_status=exchange.status,
                        comment=f"Application {'submitted' if action == 'submit' else 'updated'}",
                    )

                    # Send notifications for submission
                    if action == "submit":
                        try:
                            from ..services.notification import \
                                NotificationService

                            NotificationService.send_submission_confirmation(exchange)
                        except Exception as e:
                            logger.error(
                                f"Failed to send submission notification: {str(e)}"
                            )

                    if action == "submit":
                        messages.success(
                            request, "Exchange application submitted successfully!"
                        )
                    else:
                        messages.success(
                            request, "Exchange application updated successfully."
                        )

                    return redirect("exchange:exchange-detail", pk=exchange.id)

            except Exception as e:
                logger.error(
                    f"Exchange update failed for user {request.user.username}: {str(e)}"
                )
                messages.error(request, f"Error updating application: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # GET request - show form with existing data
        form = ExchangeForm(instance=exchange, user=request.user)

    return render(
        request,
        "exchange/exchange_form.html",
        {
            "form": form,
            "action": "edit",
            "exchange": exchange,
        },
    )


@login_required
def add_comment(request, pk):
    """Fixed comment addition with proper validation"""
    exchange = get_object_or_404(Exchange, id=pk)

    # Check permission - user must have access to view the exchange
    if not (
        exchange.student == request.user
        or request.user.is_staff
        or (
            hasattr(request.user, "profile")
            and request.user.profile.role in ["COORDINATOR", "ADMINISTRATOR"]
        )
    ):
        messages.error(
            request, "You don't have permission to comment on this exchange."
        )
        return redirect("exchange:dashboard")

    if request.method == "POST":
        content = request.POST.get("content", "").strip()

        if content:
            try:
                # Determine comment type based on user role
                if request.user.is_staff or (
                    hasattr(request.user, "profile")
                    and request.user.profile.role in ["COORDINATOR", "ADMINISTRATOR"]
                ):
                    comment_type = "INTERNAL"  # Staff comments are internal by default
                else:
                    comment_type = "STUDENT"  # Student comments are visible

                # Create the comment
                comment = Comment.objects.create(
                    exchange=exchange,
                    author=request.user,
                    text=content,
                    comment_type=comment_type,
                )

                # Log the comment in workflow
                WorkflowLog.objects.create(
                    exchange=exchange,
                    user=request.user,
                    from_status=exchange.status,
                    to_status=exchange.status,
                    comment=f"Added comment: {content[:50]}{'...' if len(content) > 50 else ''}",
                )

                messages.success(request, "Comment added successfully.")
                logger.info(
                    f"Comment added to exchange {exchange.id} by user {request.user.username}"
                )

            except Exception as e:
                logger.error(
                    f"Failed to add comment to exchange {exchange.id}: {str(e)}"
                )
                messages.error(request, "Error adding comment. Please try again.")
        else:
            messages.error(request, "Comment cannot be empty.")

    return redirect("exchange:exchange-detail", pk=exchange.id)


@login_required
def exchange_list_api(request):
    """API view for getting exchanges as JSON with proper filtering"""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    try:
        # Determine which exchanges to show based on user role
        if request.user.is_staff or (
            hasattr(request.user, "profile")
            and request.user.profile.role in ["COORDINATOR", "ADMINISTRATOR"]
        ):
            exchanges = Exchange.objects.select_related("student").all()
        else:
            exchanges = Exchange.objects.filter(student=request.user)

        # Apply filters if provided
        status_filter = request.GET.get("status")
        if status_filter and status_filter != "all":
            exchanges = exchanges.filter(status=status_filter)

        search_query = request.GET.get("q")
        if search_query:
            exchanges = exchanges.filter(
                Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
                | Q(destination_university__icontains=search_query)
                | Q(destination_country__icontains=search_query)
            )

        # Create JSON response
        data = []
        for exchange in exchanges:
            data.append(
                {
                    "id": exchange.id,
                    "student_name": f"{exchange.first_name} {exchange.last_name}",
                    "destination": exchange.destination_university,
                    "country": exchange.destination_country,
                    "program": exchange.exchange_program,
                    "start_date": (
                        exchange.start_date.isoformat() if exchange.start_date else None
                    ),
                    "end_date": (
                        exchange.end_date.isoformat() if exchange.end_date else None
                    ),
                    "status": exchange.status,
                    "status_display": dict(Exchange.STATUS_CHOICES).get(
                        exchange.status, exchange.status
                    ),
                    "created_at": (
                        exchange.created_at.isoformat() if exchange.created_at else None
                    ),
                    "url": f"/exchanges/{exchange.id}/",
                }
            )

        return JsonResponse({"exchanges": data})

    except Exception as e:
        logger.error(f"Exchange list API error: {str(e)}")
        return JsonResponse({"error": "Internal server error"}, status=500)


@login_required
def profile_view(request):
    """
    View function for user profile page
    """
    from ..forms import UserProfileForm

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("exchange:profile")
        else:
            messages.error(request, f"Issue while saving profile! {form.errors}")
            return redirect("exchange:profile")
    else:
        form = UserProfileForm(
            instance=request.user.profile if hasattr(request.user, "profile") else None
        )

    return render(request, "authentication/profile.html", {"personal_form": form})
