from celery import shared_task
from django.core.mail import send_mail


REMINDER_EVENT_TYPE_TO_SETTINGS_CATEGORY = {
    "application_deadline": "applications",
    "document_deadline": "documents",
    "program_start": "programs",
    "program_end": "programs",
    "custom": "programs",
    # Legacy / shorthand values seen in older data or tests
    "application": "applications",
    "document": "documents",
    "program": "programs",
}


def settings_category_for_reminder_event(event_type: str) -> str:
    """
    Map Reminder.event_type to NotificationService settings_category.

    Uses the same UserSettings groups as other transactional sends so deadline
    reminders honor application vs document vs program toggles.
    """
    return REMINDER_EVENT_TYPE_TO_SETTINGS_CATEGORY.get(event_type, "programs")


def get_user_email(user):
    # Replace with actual logic to get user email
    return user.email


@shared_task
def send_notification_email(user_id, subject, message):
    from accounts.models import User

    user = User.objects.get(id=user_id)
    email = get_user_email(user)
    send_mail(
        subject,
        message,
        "noreply@seim.local",
        [email],
        fail_silently=False,
    )


@shared_task
def send_email_notification(user_id, subject, message):
    """Alias for send_notification_email to match test expectations."""
    return send_notification_email(user_id, subject, message)


@shared_task
def send_notification_by_id(notification_id):
    """Send email notification based on notification ID."""
    from .models import Notification

    try:
        notification = Notification.objects.get(id=notification_id)
        email = get_user_email(notification.recipient)
        send_mail(
            notification.title,
            notification.message,
            "noreply@seim.local",
            [email],
            fail_silently=False,
        )
        return True
    except Notification.DoesNotExist:
        return False


@shared_task
def send_deadline_reminders():
    """
    Send reminder notifications for upcoming deadlines.
    
    This task should be run periodically (e.g., every 15 minutes) via Celery Beat.
    It finds all reminders that are due and haven't been sent yet, then creates
    notifications for them.
    """
    from django.utils import timezone
    from .models import Reminder
    from .services import NotificationService
    
    now = timezone.now()
    
    # Get all unsent reminders that are due
    due_reminders = Reminder.objects.filter(
        remind_at__lte=now,
        sent=False
    ).select_related('user')
    
    sent_count = 0
    
    for reminder in due_reminders:
        try:
            # Create notification for this reminder
            notification = NotificationService.send_notification(
                recipient=reminder.user,
                title=f"Reminder: {reminder.event_title}",
                message=f"This is a reminder about {reminder.event_title}",
                notification_type="both",  # Send both email and in-app
                category="warning",  # Reminders are warnings
                data={
                    'event_type': reminder.event_type,
                    'event_id': str(reminder.event_id),
                },
                settings_category=settings_category_for_reminder_event(
                    reminder.event_type
                ),
            )
            
            # Mark reminder as sent
            reminder.sent = True
            reminder.notification = notification
            reminder.save()
            
            sent_count += 1
            
        except Exception as e:
            # Log error but continue with other reminders
            print(f"Error sending reminder {reminder.id}: {e}")
    
    return sent_count


@shared_task
def send_notification_digests():
    """
    Daily Celery Beat job: send unread summary notifications per user settings.
    """
    from .digest import process_notification_digests

    return process_notification_digests()


@shared_task
def send_agreement_expiration_reminders():
    """
    Notify admins/coordinators on configured days before agreement end_date.
    Scheduled daily via Celery Beat (seim.celery beat_schedule + django_celery_beat migration).
    """
    from exchange.agreement_expiration import process_agreement_expiration_reminders

    return process_agreement_expiration_reminders()