"""
Dashboard API views for user statistics and recent activity.
"""
from django.db.models import Exists, OuterRef, Q

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from documents.models import Document, DocumentResubmissionRequest
from exchange.models import Application
from notifications.models import Notification


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
