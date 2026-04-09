from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.cache import cache_api_response

from .models import Notification, NotificationPreference, NotificationType, Reminder
from .routing_reference import build_notification_routing_reference
from .serializers import (
    NotificationPreferenceSerializer,
    NotificationRoutingReferenceSerializer,
    NotificationSerializer,
    NotificationTypeSerializer,
    ReminderSerializer,
)
from .services import NotificationService

# Create your views here.


@extend_schema(
    summary="Notification routing reference",
    description=(
        "Read-only map of notification ``settings_category`` values, a catalog of main "
        "transactional sends (with per-route recipient summaries), digest routing, and deadline "
        "reminder event types to ``UserSettings`` field names. Coordinators, admins, and superusers only."
    ),
    responses={
        200: NotificationRoutingReferenceSerializer,
        403: OpenApiResponse(description="Students and other roles without staff access."),
    },
)
class NotificationRoutingReferenceView(APIView):
    """
    Read-only map of ``settings_category`` / digest / reminder routing to UserSettings fields.

    Coordinators and admins only (for internal docs and future settings UI).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        staff_ok = (
            getattr(user, "is_superuser", False)
            or user.has_role("coordinator")
            or user.has_role("admin")
        )
        if not staff_ok:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(build_notification_routing_reference())


class NotificationTypeViewSet(viewsets.ModelViewSet):
    queryset = NotificationType.objects.all()
    serializer_class = NotificationTypeSerializer

    @cache_api_response(timeout=600)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=600)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for notifications with filtering and bulk operations."""
    
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_read', 'notification_type', 'category']
    ordering_fields = ['sent_at', 'created_at']
    ordering = ['-sent_at']
    
    def get_queryset(self):
        """Filter notifications to only show user's own notifications."""
        user = self.request.user
        qs = Notification.objects.filter(recipient=user)
        
        # Filter by unread if requested
        unread_only = self.request.query_params.get('unread')
        if unread_only and unread_only.lower() == 'true':
            qs = qs.filter(is_read=False)
        
        return qs.select_related('recipient')
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a single notification as read."""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read for the current user."""
        count = NotificationService.mark_all_notifications_as_read(request.user)
        return Response({'status': 'all notifications marked as read', 'count': count})
    
    @action(detail=True, methods=['delete'])
    def delete_notification(self, request, pk=None):
        """Delete a notification."""
        notification = self.get_object()
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        return Response({'count': count})

    @action(detail=False, methods=["post"])
    def batch_send(self, request):
        """Send notifications to multiple users."""
        users = request.data.get("users", [])
        type_name = request.data.get("type_name")
        message = request.data.get("message")
        sent = NotificationService.batch_send_notifications(users, type_name, message)
        return Response({"sent": len(sent)})


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    queryset = NotificationPreference.objects.all()
    serializer_class = NotificationPreferenceSerializer


class ReminderViewSet(viewsets.ModelViewSet):
    """ViewSet for user reminders."""
    
    queryset = Reminder.objects.all()
    serializer_class = ReminderSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['sent', 'event_type']
    ordering_fields = ['remind_at', 'created_at']
    ordering = ['remind_at']
    
    def get_queryset(self):
        """Users can only see their own reminders."""
        return Reminder.objects.filter(user=self.request.user).select_related('notification')
    
    def perform_create(self, serializer):
        """Set user from request."""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming reminders (not sent yet)."""
        reminders = self.get_queryset().filter(sent=False).order_by('remind_at')[:10]
        serializer = self.get_serializer(reminders, many=True)
        return Response(serializer.data)
