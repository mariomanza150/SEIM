from celery import shared_task
from django.core.mail import send_mail


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
