"""
Dashboard API views for user statistics and recent activity.
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Exists, OuterRef, Q
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from documents.models import Document, DocumentResubmissionRequest
from exchange.models import Application
from notifications.models import Notification

User = get_user_model()

PENDING_REVIEW_STATUSES = ("submitted", "under_review")


def _is_coordinator_or_admin(user):
    has_role = getattr(user, "has_role", None)
    if not callable(has_role):
        return False
    return has_role("coordinator") or has_role("admin")


class DashboardStatsView(APIView):
    """
    Get dashboard statistics for the current user.

    Returns counts for:
    - Applications (student: own; coordinator/admin: all visible)
    - Documents (student: on own applications or uploaded by self; staff: all)
    - Unread notifications
    - Pending tasks (student: draft + under_review; staff: submitted/under_review or open resubmissions)
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        staff = _is_coordinator_or_admin(user)

        unread = Notification.objects.filter(recipient=user, is_read=False).count()

        if staff:
            open_resub = DocumentResubmissionRequest.objects.filter(
                document__application=OuterRef("pk"),
                resolved=False,
            )
            pending = (
                Application.objects.filter(withdrawn=False)
                .filter(
                    Q(status__name__in=["submitted", "under_review"])
                    | Q(Exists(open_resub))
                )
                .distinct()
                .count()
            )
            stats = {
                "applications": Application.objects.count(),
                "documents": Document.objects.count(),
                "notifications": unread,
                "pending": pending,
            }
        else:
            stats = {
                "applications": Application.objects.filter(student=user).count(),
                "documents": Document.objects.filter(
                    Q(uploaded_by=user) | Q(application__student=user)
                ).count(),
                "notifications": unread,
                "pending": Application.objects.filter(
                    student=user, status__name__in=["draft", "under_review"]
                ).count(),
            }

        return Response(stats, status=status.HTTP_200_OK)


def _pending_review_q():
    return Q(withdrawn=False) & Q(status__name__in=PENDING_REVIEW_STATUSES)


def _avg_days_since_submission(queryset):
    """Mean age in days for applications with submitted_at set (queue-time proxy)."""
    qs = queryset.filter(submitted_at__isnull=False).only("submitted_at")
    if not qs.exists():
        return None
    now = timezone.now()
    total = 0.0
    n = 0
    for app in qs.iterator(chunk_size=500):
        total += (now - app.submitted_at).total_seconds()
        n += 1
    if not n:
        return None
    return round(total / n / 86400, 2)


class CoordinatorWorkloadView(APIView):
    """
    Review workload and simple SLA-style signals for coordinators and admins.

    Coordinators see counts for applications assigned to them and for programs
    they coordinate. Admins additionally see institution-wide pending totals,
    stale under_review items, and per-coordinator assigned queue depth.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not _is_coordinator_or_admin(user):
            return Response(
                {"detail": "Coordinator or admin access required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        pending = Application.objects.filter(_pending_review_q())
        my_assigned = pending.filter(assigned_coordinator=user)
        program_ids = user.coordinated_programs.values_list("id", flat=True)
        my_program_queue = pending.filter(program_id__in=program_ids)

        open_resub = DocumentResubmissionRequest.objects.filter(
            document__application=OuterRef("pk"),
            resolved=False,
        )
        my_assigned_open_resubmit = my_assigned.filter(Exists(open_resub)).count()

        payload = {
            "you": {
                "assigned_pending_review": my_assigned.count(),
                "coordinated_programs_pending": my_program_queue.count(),
                "assigned_with_open_resubmit": my_assigned_open_resubmit,
                "avg_days_in_queue_assigned": _avg_days_since_submission(my_assigned),
            },
            "global": None,
            "distribution": None,
        }

        if user.has_role("admin") or user.is_superuser:
            stale_cutoff = timezone.now() - timedelta(days=14)
            payload["global"] = {
                "pending_review_total": pending.count(),
                "unassigned_pending_review": pending.filter(
                    assigned_coordinator__isnull=True
                ).count(),
                "stale_under_review_14d": Application.objects.filter(
                    withdrawn=False,
                    status__name="under_review",
                    updated_at__lt=stale_cutoff,
                ).count(),
            }
            coordinators = (
                User.objects.filter(roles__name="coordinator")
                .distinct()
                .annotate(
                    assigned_pending_review=Count(
                        "assigned_applications",
                        filter=Q(
                            assigned_applications__withdrawn=False,
                            assigned_applications__status__name__in=PENDING_REVIEW_STATUSES,
                        ),
                    )
                )
                .order_by("-assigned_pending_review", "username")[:40]
            )
            payload["distribution"] = [
                {
                    "coordinator_id": str(c.id),
                    "display_name": (c.get_full_name() or "").strip() or c.username,
                    "assigned_pending_review": c.assigned_pending_review,
                }
                for c in coordinators
            ]

        return Response(payload, status=status.HTTP_200_OK)
