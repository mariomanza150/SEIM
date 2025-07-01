"""
Celery tasks for the exchange application.
"""

import logging

from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Exchange
from .services.email_notifications import ExchangeEmailNotificationService

logger = logging.getLogger(__name__)


@shared_task
def send_exchange_notification(exchange_id, notification_type, user_id=None, extra_context=None):
    """
    Send email notifications for exchange workflow events.

    Args:
        exchange_id: ID of the exchange
        notification_type: Type of notification to send
        user_id: Optional user ID for specific notifications
        extra_context: Additional context for the notification
    """
    try:
        exchange = Exchange.objects.get(id=exchange_id)
        notification_service = ExchangeEmailNotificationService()

        if notification_type == "submission":
            result = notification_service.notify_submission(exchange)

        elif notification_type == "approval":
            result = notification_service.notify_approval(exchange)

        elif notification_type == "rejection":
            reason = extra_context.get("reason") if extra_context else None
            result = notification_service.notify_rejection(exchange, reason)

        elif notification_type == "review_assigned" and user_id:
            reviewer = User.objects.get(id=user_id)
            result = notification_service.notify_review_assigned(exchange, reviewer)

        elif notification_type == "document_uploaded" and extra_context:
            document_name = extra_context.get("document_name")
            result = notification_service.notify_document_uploaded(exchange, document_name)

        elif notification_type == "comment_added" and user_id and extra_context:
            comment_author = User.objects.get(id=user_id)
            comment_text = extra_context.get("comment_text")
            result = notification_service.notify_comment_added(exchange, comment_author, comment_text)

        else:
            logger.warning(f"Unknown notification type: {notification_type}")
            return False

        if result:
            logger.info(f"Successfully sent {notification_type} notification for exchange {exchange_id}")
        else:
            logger.error(f"Failed to send {notification_type} notification for exchange {exchange_id}")

        return result

    except Exchange.DoesNotExist:
        logger.error(f"Exchange {exchange_id} not found")
        return False
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return False


@shared_task
def check_exchange_deadlines():
    """
    Periodic task to check for exchange deadlines and send reminders.
    """
    try:
        notification_service = ExchangeEmailNotificationService()

        # Check for exchanges starting soon (30 days)
        start_soon_date = timezone.now().date() + timezone.timedelta(days=30)
        exchanges_starting_soon = Exchange.objects.filter(status="APPROVED", start_date=start_soon_date)

        for exchange in exchanges_starting_soon:
            context = {
                "exchange": exchange,
                "days_until_start": 30,
                "student_name": f"{exchange.first_name} {exchange.last_name}",
            }

            notification_service.email_service.send_email(
                to_emails=[exchange.email],
                subject=f"Reminder: Exchange to {exchange.destination_university} starts in 30 days",
                template_name="exchange_reminder",
                context=context,
            )

        # Check for incomplete applications (deadline in 7 days)
        deadline_date = timezone.now().date() + timezone.timedelta(days=7)
        incomplete_exchanges = Exchange.objects.filter(status="DRAFT", created_at__lte=deadline_date)

        for exchange in incomplete_exchanges:
            context = {
                "exchange": exchange,
                "student_name": f"{exchange.first_name} {exchange.last_name}",
                "days_until_deadline": 7,
            }

            notification_service.email_service.send_email(
                to_emails=[exchange.email],
                subject="Reminder: Complete your exchange application",
                template_name="application_deadline_reminder",
                context=context,
            )

        logger.info(f"Processed {exchanges_starting_soon.count()} exchanges starting soon")
        logger.info(f"Sent {incomplete_exchanges.count()} application deadline reminders")

    except Exception as e:
        logger.error(f"Error checking exchange deadlines: {str(e)}")
        raise


@shared_task
def cleanup_expired_documents():
    """
    Periodic task to clean up expired documents.
    """
    from .models import Document

    try:
        expired_count = 0

        # Get all expired documents
        expired_documents = Document.objects.filter(expiry_date__lt=timezone.now())

        for document in expired_documents:
            # Check if document is still needed
            if document.exchange.status in ["COMPLETED", "REJECTED"]:
                # Safe to delete
                document.delete()
                expired_count += 1
            else:
                # Mark as expired but don't delete
                document.is_expired = True
                document.save()

        logger.info(f"Cleaned up {expired_count} expired documents")

    except Exception as e:
        logger.error(f"Error cleaning up expired documents: {str(e)}")
        raise


@shared_task
def generate_exchange_report(start_date=None, end_date=None):
    """
    Generate a report of exchange applications for a given period.
    """
    from .services.report_generator import ExchangeReportGenerator

    try:
        generator = ExchangeReportGenerator()
        report = generator.generate_report(start_date, end_date)

        # Send report to admins
        notification_service = ExchangeEmailNotificationService()

        if notification_service.admin_emails:
            notification_service.email_service.send_email(
                to_emails=notification_service.admin_emails,
                subject=f"Exchange Report - {report['period']}",
                template_name="admin_report",
                context={"report": report},
                attachments=[("exchange_report.pdf", report["pdf_content"], "application/pdf")],
            )

        logger.info(f"Generated and sent exchange report for period {report['period']}")
        return True

    except Exception as e:
        logger.error(f"Error generating exchange report: {str(e)}")
        return False
