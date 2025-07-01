"""
Fixed Workflow transition views for the exchange application.
Handles status transitions like submit, review, approve, reject, complete with proper error handling.
"""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from ..models import Exchange
from ..services.workflow import WorkflowService

logger = logging.getLogger(__name__)


def user_can_approve_exchange(user):
    """Check if user can approve exchange applications"""
    return (
        user.is_staff
        or user.has_perm("exchange.can_approve_exchange")
        or (hasattr(user, "profile") and user.profile.role in ["COORDINATOR", "ADMINISTRATOR"])
    )


def user_can_review_exchange(user):
    """Check if user can review exchange applications"""
    return (
        user.is_staff
        or user.has_perm("exchange.can_review_exchange")
        or (hasattr(user, "profile") and user.profile.role in ["COORDINATOR", "ADMINISTRATOR"])
    )


@login_required
@require_POST
def submit_exchange(request, pk):
    """Fixed view function for submitting an exchange application"""
    exchange = get_object_or_404(Exchange, id=pk)

    # Check permission
    if exchange.student != request.user:
        messages.error(request, "You don't have permission to submit this exchange.")
        logger.warning(f"User {request.user.username} attempted to submit exchange {pk} without permission")
        return redirect("exchange:dashboard")

    try:
        with transaction.atomic():
            # Check if can submit
            can_submit, reason = WorkflowService.can_submit(exchange)
            if not can_submit:
                messages.error(request, f"Cannot submit application: {reason}")
                logger.warning(f"Submission validation failed for exchange {pk}: {reason}")
                return redirect("exchange:exchange-detail", pk=exchange.id)

            # Transition to submitted status
            success, message = WorkflowService.transition(
                exchange=exchange,
                new_status="SUBMITTED",
                user=request.user,
                comment="Application submitted by student",
            )

            if success:
                messages.success(request, "Application submitted successfully.")
                logger.info(f"Exchange {pk} submitted successfully by user {request.user.username}")
            else:
                messages.error(request, f"Failed to submit application: {message}")
                logger.error(f"Failed to submit exchange {pk}: {message}")

    except Exception as e:
        logger.error(f"Error submitting exchange {pk}: {str(e)}")
        messages.error(
            request,
            "An error occurred while submitting the application. Please try again.",
        )

    return redirect("exchange:exchange-detail", pk=exchange.id)


@login_required
@require_POST
def review_exchange(request, pk):
    """Fixed view function for marking an exchange as under review"""
    exchange = get_object_or_404(Exchange, id=pk)

    # Enhanced permission check
    if not user_can_review_exchange(request.user):
        messages.error(request, "You don't have permission to review applications.")
        logger.warning(f"User {request.user.username} attempted to review exchange {pk} without permission")
        return redirect("exchange:exchange-detail", pk=exchange.id)

    # Check if review is allowed
    if not exchange.can_transition_to("UNDER_REVIEW"):
        messages.error(
            request,
            f"Cannot review application in {exchange.get_status_display()} status.",
        )
        return redirect("exchange:exchange-detail", pk=exchange.id)

    try:
        with transaction.atomic():
            comment = request.POST.get("comment", "Application marked for review")

            # Transition to under review status
            success, message = WorkflowService.transition(
                exchange=exchange,
                new_status="UNDER_REVIEW",
                user=request.user,
                comment=comment,
            )

            if success:
                messages.success(request, "Application marked as under review.")
                logger.info(f"Exchange {pk} marked under review by user {request.user.username}")
            else:
                messages.error(request, f"Failed to update status: {message}")
                logger.error(f"Failed to mark exchange {pk} under review: {message}")

    except Exception as e:
        logger.error(f"Error reviewing exchange {pk}: {str(e)}")
        messages.error(request, "An error occurred while updating the application status.")

    return redirect("exchange:exchange-detail", pk=exchange.id)


@login_required
@require_POST
def approve_exchange(request, pk):
    """Fixed view function for approving an exchange application"""
    exchange = get_object_or_404(Exchange, id=pk)

    # Enhanced permission check
    if not user_can_approve_exchange(request.user):
        messages.error(request, "You don't have permission to approve applications.")
        logger.warning(f"User {request.user.username} attempted to approve exchange {pk} without permission")
        return redirect("exchange:exchange-detail", pk=exchange.id)

    # Check if approval is allowed
    if not exchange.can_transition_to("APPROVED"):
        messages.error(
            request,
            f"Cannot approve application in {exchange.get_status_display()} status.",
        )
        logger.warning(f"Invalid approval attempt for exchange {pk} in status {exchange.status}")
        return redirect("exchange:exchange-detail", pk=exchange.id)

    try:
        with transaction.atomic():
            comment = request.POST.get("comment", "Application approved")

            # Transition to approved status
            success, message = WorkflowService.transition(
                exchange=exchange,
                new_status="APPROVED",
                user=request.user,
                comment=comment,
            )

            if success:
                messages.success(request, "Application approved successfully.")
                logger.info(f"Exchange {pk} approved by user {request.user.username}")

                # Send approval notification
                try:
                    from ..services.notification import NotificationService

                    NotificationService.send_approval_notification(exchange)
                except Exception as e:
                    logger.error(f"Failed to send approval notification for exchange {pk}: {str(e)}")
                    # Don't fail the approval for notification issues

            else:
                messages.error(request, f"Failed to approve application: {message}")
                logger.error(f"Failed to approve exchange {pk}: {message}")

    except Exception as e:
        logger.error(f"Error approving exchange {pk}: {str(e)}")
        messages.error(request, "An error occurred while approving the application.")

    return redirect("exchange:exchange-detail", pk=exchange.id)


@login_required
@require_POST
def reject_exchange(request, pk):
    """Fixed view function for rejecting an exchange application"""
    exchange = get_object_or_404(Exchange, id=pk)

    # Enhanced permission check
    if not user_can_approve_exchange(request.user):
        messages.error(request, "You don't have permission to reject applications.")
        logger.warning(f"User {request.user.username} attempted to reject exchange {pk} without permission")
        return redirect("exchange:exchange-detail", pk=exchange.id)

    # Check if rejection is allowed
    if not exchange.can_transition_to("REJECTED"):
        messages.error(
            request,
            f"Cannot reject application in {exchange.get_status_display()} status.",
        )
        logger.warning(f"Invalid rejection attempt for exchange {pk} in status {exchange.status}")
        return redirect("exchange:exchange-detail", pk=exchange.id)

    # Require rejection reason
    reason = request.POST.get("comment", "").strip()
    if not reason:
        messages.error(request, "Rejection reason is required.")
        logger.warning(f"Rejection attempt for exchange {pk} without reason")
        return redirect("exchange:exchange-detail", pk=exchange.id)

    try:
        with transaction.atomic():
            # Transition to rejected status
            success, message = WorkflowService.transition(
                exchange=exchange,
                new_status="REJECTED",
                user=request.user,
                comment=reason,
            )

            if success:
                messages.success(request, "Application rejected.")
                logger.info(f"Exchange {pk} rejected by user {request.user.username}")

                # Send rejection notification
                try:
                    from ..services.notification import NotificationService

                    NotificationService.send_rejection_notification(exchange)
                except Exception as e:
                    logger.error(f"Failed to send rejection notification for exchange {pk}: {str(e)}")
                    # Don't fail the rejection for notification issues

            else:
                messages.error(request, f"Failed to reject application: {message}")
                logger.error(f"Failed to reject exchange {pk}: {message}")

    except Exception as e:
        logger.error(f"Error rejecting exchange {pk}: {str(e)}")
        messages.error(request, "An error occurred while rejecting the application.")

    return redirect("exchange:exchange-detail", pk=exchange.id)


@login_required
@require_POST
def complete_exchange(request, pk):
    """Fixed view function for marking an exchange as completed"""
    exchange = get_object_or_404(Exchange, id=pk)

    # Enhanced permission check
    if not user_can_approve_exchange(request.user):
        messages.error(request, "You don't have permission to complete applications.")
        logger.warning(f"User {request.user.username} attempted to complete exchange {pk} without permission")
        return redirect("exchange:exchange-detail", pk=exchange.id)

    # Check if completion is allowed
    if not exchange.can_transition_to("COMPLETED"):
        messages.error(
            request,
            f"Cannot complete application in {exchange.get_status_display()} status.",
        )
        logger.warning(f"Invalid completion attempt for exchange {pk} in status {exchange.status}")
        return redirect("exchange:exchange-detail", pk=exchange.id)

    try:
        with transaction.atomic():
            comment = request.POST.get("comment", "Exchange program completed")

            # Transition to completed status
            success, message = WorkflowService.transition(
                exchange=exchange,
                new_status="COMPLETED",
                user=request.user,
                comment=comment,
            )

            if success:
                messages.success(request, "Exchange marked as completed.")
                logger.info(f"Exchange {pk} completed by user {request.user.username}")
            else:
                messages.error(request, f"Failed to complete exchange: {message}")
                logger.error(f"Failed to complete exchange {pk}: {message}")

    except Exception as e:
        logger.error(f"Error completing exchange {pk}: {str(e)}")
        messages.error(request, "An error occurred while completing the exchange.")

    return redirect("exchange:exchange-detail", pk=exchange.id)
