"""
Dashboard API views for user statistics and recent activity.
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from exchange.models import Application
from documents.models import Document
from notifications.models import Notification


class DashboardStatsView(APIView):
    """
    Get dashboard statistics for the current user.
    
    Returns counts for:
    - Applications
    - Documents
    - Unread notifications
    - Pending tasks
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get counts based on user role
        stats = {
            "applications": Application.objects.filter(user=user).count(),
            "documents": Document.objects.filter(uploaded_by=user).count(),
            "notifications": Notification.objects.filter(
                recipient=user, is_read=False
            ).count(),
            "pending": Application.objects.filter(
                user=user, status__name__in=["draft", "under_review"]
            ).count(),
        }

        return Response(stats, status=status.HTTP_200_OK)
