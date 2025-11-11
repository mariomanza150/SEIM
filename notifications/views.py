
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.cache import cache_api_response

from .models import Notification, NotificationPreference, NotificationType
from .serializers import (
    NotificationPreferenceSerializer,
    NotificationSerializer,
    NotificationTypeSerializer,
)
from .services import NotificationService

# Create your views here.


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
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    @action(detail=False, methods=["post"])
    def batch_send(self, request):
        users = request.data.get("users", [])
        type_name = request.data.get("type_name")
        message = request.data.get("message")
        sent = NotificationService.batch_send_notifications(users, type_name, message)
        return Response({"sent": len(sent)})


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    queryset = NotificationPreference.objects.all()
    serializer_class = NotificationPreferenceSerializer
