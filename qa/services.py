import logging

from django.contrib.auth import get_user_model
from django.db.models import Q

logger = logging.getLogger(__name__)


def triager_queryset():
    User = get_user_model()
    return (
        User.objects.filter(is_active=True, is_demo_account=False, is_tester=True)
        .filter(Q(is_superuser=True) | Q(roles__name="admin"))
        .distinct()
    )


def triage_url(issue) -> str:
    # Vue report page; triagers get the triage panel there (Django admin still works).
    return f"/seim/tester/reports/{issue.pk}"


def reporter_url(issue) -> str:
    return f"/seim/tester/reports/{issue.pk}"


def notify_new_issue(issue) -> None:
    """In-app notification to every triager (best effort; never blocks reporting)."""
    try:
        from notifications.services import NotificationService

        for user in triager_queryset():
            if issue.reporter_id and user.pk == issue.reporter_id:
                continue
            NotificationService.send_notification(
                recipient=user,
                title=f"{issue.reference}: {issue.title}"[:255],
                message=f"New {issue.get_severity_display().lower()} QA report",
                notification_type="in_app",
                action_url=triage_url(issue),
                action_text="Triage",
                category="warning"
                if issue.severity in ("blocker", "major")
                else "info",
                data={"qa_issue": str(issue.pk)},
            )
    except Exception:  # pragma: no cover - notifications must not break reporting
        logger.exception("Could not notify triagers about %s", issue.reference)


def notify_status_change(issue, old_status, actor) -> None:
    if not issue.reporter_id or (actor and actor.pk == issue.reporter_id):
        return
    try:
        from notifications.services import NotificationService

        NotificationService.send_notification(
            recipient=issue.reporter,
            title=f"{issue.reference}: {issue.get_status_display()}"[:255],
            message=issue.title[:500],
            notification_type="in_app",
            action_url=reporter_url(issue),
            action_text="View report",
            category="success" if issue.status in ("fixed", "verified") else "info",
            data={"qa_issue": str(issue.pk), "from": old_status, "to": issue.status},
        )
    except Exception:  # pragma: no cover
        logger.exception("Could not notify reporter about %s", issue.reference)


def notify_reopened(issue, actor) -> None:
    """Tell the assignee (or every triager) that a fixed report was reopened."""
    try:
        from notifications.services import NotificationService

        recipients = [issue.assignee] if issue.assignee_id else list(triager_queryset())
        for user in recipients:
            if actor and user.pk == actor.pk:
                continue
            NotificationService.send_notification(
                recipient=user,
                title=f"{issue.reference} reopened"[:255],
                message=issue.title[:500],
                notification_type="in_app",
                action_url=triage_url(issue),
                action_text="Triage",
                category="warning",
                data={"qa_issue": str(issue.pk), "to": issue.status},
            )
    except Exception:  # pragma: no cover
        logger.exception("Could not notify about reopened %s", issue.reference)
