"""
Email notification service for exchange workflow transitions.
"""

import logging
from typing import Dict, List, Optional

from django.conf import settings
from django.contrib.auth.models import User

from ..models import Exchange
from .email_service import EmailService

logger = logging.getLogger(__name__)


class ExchangeEmailNotificationService:
    """
    Service for sending email notifications during exchange workflow transitions.
    """

    def __init__(self):
        self.email_service = EmailService()
        self.admin_emails = getattr(settings, "EXCHANGE_ADMIN_EMAILS", [])
        if isinstance(self.admin_emails, str):
            self.admin_emails = [
                email.strip() for email in self.admin_emails.split(",")
            ]

    def notify_submission(self, exchange: Exchange) -> bool:
        """
        Send notification when exchange is submitted.
        """
        # Notify student
        student_notified = self._notify_student_submission(exchange)

        # Notify administrators
        admin_notified = self._notify_admin_submission(exchange)

        return student_notified and admin_notified

    def notify_approval(self, exchange: Exchange) -> bool:
        """
        Send notification when exchange is approved.
        """
        context = {
            "exchange": exchange,
            "student_name": f"{exchange.first_name} {exchange.last_name}",
            "destination": exchange.destination_university,
            "start_date": exchange.start_date,
            "end_date": exchange.end_date,
        }

        return self.email_service.send_email(
            to_emails=[exchange.email],
            subject=f"Exchange Application Approved - {exchange.destination_university}",
            template_name="exchange_approved",
            context=context,
        )

    def notify_rejection(
        self, exchange: Exchange, reason: Optional[str] = None
    ) -> bool:
        """
        Send notification when exchange is rejected.
        """
        context = {
            "exchange": exchange,
            "student_name": f"{exchange.first_name} {exchange.last_name}",
            "destination": exchange.destination_university,
            "reason": reason or exchange.notes,
        }

        return self.email_service.send_email(
            to_emails=[exchange.email],
            subject=f"Exchange Application Update - {exchange.destination_university}",
            template_name="exchange_rejected",
            context=context,
        )

    def notify_review_assigned(self, exchange: Exchange, reviewer: User) -> bool:
        """
        Send notification when exchange is assigned to a reviewer.
        """
        context = {
            "exchange": exchange,
            "reviewer_name": reviewer.get_full_name() or reviewer.username,
            "student_name": f"{exchange.first_name} {exchange.last_name}",
            "destination": exchange.destination_university,
        }

        return self.email_service.send_email(
            to_emails=[reviewer.email],
            subject=f"New Exchange Application for Review - {exchange.student_id}",
            template_name="exchange_review_assigned",
            context=context,
        )

    def notify_document_uploaded(self, exchange: Exchange, document_name: str) -> bool:
        """
        Send notification when a new document is uploaded.
        """
        context = {
            "exchange": exchange,
            "student_name": f"{exchange.first_name} {exchange.last_name}",
            "document_name": document_name,
        }

        # Only notify admins if exchange is submitted
        if exchange.status != "DRAFT" and self.admin_emails:
            return self.email_service.send_email(
                to_emails=self.admin_emails,
                subject=f"New Document Uploaded - {exchange.student_id}",
                template_name="document_uploaded",
                context=context,
            )

        return True

    def notify_comment_added(
        self, exchange: Exchange, comment_author: User, comment_text: str
    ) -> bool:
        """
        Send notification when a comment is added to an exchange.
        """
        context = {
            "exchange": exchange,
            "student_name": f"{exchange.first_name} {exchange.last_name}",
            "comment_author": comment_author.get_full_name() or comment_author.username,
            "comment_text": (
                comment_text[:200] + "..." if len(comment_text) > 200 else comment_text
            ),
        }

        # Determine recipients
        recipients = set()

        # Add student if comment is visible to them
        if exchange.status != "DRAFT":
            recipients.add(exchange.email)

        # Add reviewer if assigned
        if exchange.reviewed_by:
            recipients.add(exchange.reviewed_by.email)

        # Add other staff who commented
        for comment in exchange.comments.all():
            if comment.author.email:
                recipients.add(comment.author.email)

        # Remove comment author from recipients
        if comment_author.email in recipients:
            recipients.remove(comment_author.email)

        if recipients:
            return self.email_service.send_email(
                to_emails=list(recipients),
                subject=f"New Comment on Exchange - {exchange.student_id}",
                template_name="comment_added",
                context=context,
            )

        return True

    def _notify_student_submission(self, exchange: Exchange) -> bool:
        """
        Notify student about successful submission.
        """
        context = {
            "exchange": exchange,
            "student_name": f"{exchange.first_name} {exchange.last_name}",
            "destination": exchange.destination_university,
            "submission_date": exchange.submission_date,
        }

        return self.email_service.send_email(
            to_emails=[exchange.email],
            subject=f"Exchange Application Submitted - {exchange.destination_university}",
            template_name="exchange_submitted",
            context=context,
        )

    def _notify_admin_submission(self, exchange: Exchange) -> bool:
        """
        Notify administrators about new submission.
        """
        if not self.admin_emails:
            return True

        context = {
            "exchange": exchange,
            "student_name": f"{exchange.first_name} {exchange.last_name}",
            "student_id": exchange.student_id,
            "destination": exchange.destination_university,
            "submission_date": exchange.submission_date,
            "gpa": exchange.gpa,
        }

        return self.email_service.send_email(
            to_emails=self.admin_emails,
            subject=f"New Exchange Application - {exchange.student_id}",
            template_name="exchange_submitted_admin",
            context=context,
        )
