from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.cache import CacheManager, cache_api_response
from core.permissions import IsAdminOrReadOnly, IsCoordinatorOrAdmin

from .models import (
    Notification,
    NotificationPreference,
    NotificationRoutingOverride,
    NotificationType,
    Reminder,
)
from .routing_reference import build_notification_routing_reference
from .serializers import (
    NotificationPreferenceSerializer,
    NotificationRoutingOverrideSerializer,
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
        "transactional sends (with per-route recipient summaries and a grouped route-key index), "
        "digest routing, and deadline reminder event types (per-type recipient summaries plus a "
        "grouped event-type-by-category index) to ``UserSettings`` field names. Coordinators, admins, "
        "and superusers only."
    ),
    responses={
        200: NotificationRoutingReferenceSerializer,
        403: OpenApiResponse(
            description="Students and other roles without staff access."
        ),
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


_NOTIFICATION_TYPE_CACHE_GEN_KEY = "api_cache_gen:NotificationTypeViewSet"


def _notification_type_cache_generation() -> str:
    value = cache.get(_NOTIFICATION_TYPE_CACHE_GEN_KEY)
    return str(value if value is not None else 0)


def _notification_type_list_cache_key(*args, **kwargs):
    request = args[1]
    user_key = str(request.user.pk) if request.user.is_authenticated else "anon"
    gen = _notification_type_cache_generation()
    return CacheManager.get_cache_key(
        "api_response", f"NotificationTypeViewSet.list:{gen}:{user_key}"
    )


def _notification_type_retrieve_cache_key(*args, **kwargs):
    request = args[1]
    user_key = str(request.user.pk) if request.user.is_authenticated else "anon"
    pk = kwargs.get("pk", "")
    gen = _notification_type_cache_generation()
    return CacheManager.get_cache_key(
        "api_response", f"NotificationTypeViewSet.retrieve:{gen}:{user_key}:{pk}"
    )


def _invalidate_notification_type_api_caches() -> None:
    try:
        cache.incr(_NOTIFICATION_TYPE_CACHE_GEN_KEY)
    except ValueError:
        cache.set(_NOTIFICATION_TYPE_CACHE_GEN_KEY, 1, timeout=None)
    CacheManager.clear_pattern("api_resp:v1:api_middleware:/api/notification-types*")
    CacheManager.clear_pattern("api_resp:v1:NotificationTypeViewSet*")


class NotificationTypeViewSet(viewsets.ModelViewSet):
    queryset = NotificationType.objects.all().order_by("name")
    serializer_class = NotificationTypeSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None

    @cache_api_response(timeout=600, key_func=_notification_type_list_cache_key)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_api_response(timeout=600, key_func=_notification_type_retrieve_cache_key)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()
        _invalidate_notification_type_api_caches()

    def perform_update(self, serializer):
        serializer.save()
        _invalidate_notification_type_api_caches()

    def perform_destroy(self, instance):
        instance.delete()
        _invalidate_notification_type_api_caches()


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for notifications with filtering and bulk operations."""

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["is_read", "notification_type", "category"]
    ordering_fields = ["sent_at", "created_at"]
    ordering = ["-sent_at"]
    # Inbox is read/mark-read/delete-own; staff bulk send is the dedicated action.
    http_method_names = ["get", "head", "options", "post", "delete"]

    def get_permissions(self):
        if getattr(self, "action", None) == "batch_send":
            return [IsAuthenticated(), IsCoordinatorOrAdmin()]
        if getattr(self, "action", None) in ("create", "update", "partial_update"):
            return [IsAuthenticated(), IsCoordinatorOrAdmin()]
        return super().get_permissions()

    def get_queryset(self):
        """Filter notifications to only show user's own notifications."""
        user = self.request.user
        qs = Notification.objects.filter(recipient=user)

        # Filter by unread if requested
        unread_only = self.request.query_params.get("unread")
        if unread_only and unread_only.lower() == "true":
            qs = qs.filter(is_read=False)

        return qs.select_related("recipient")

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """Mark a single notification as read."""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"status": "notification marked as read"})

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """Mark all notifications as read for the current user."""
        count = NotificationService.mark_all_notifications_as_read(request.user)
        return Response({"status": "all notifications marked as read", "count": count})

    @action(detail=True, methods=["delete"])
    def delete_notification(self, request, pk=None):
        """Delete a notification."""
        notification = self.get_object()
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        return Response({"count": count})

    @action(detail=False, methods=["post"])
    def batch_send(self, request):
        """Staff-only: send notifications to multiple users."""
        from accounts.models import User

        users = request.data.get("users", [])
        title = request.data.get("title") or request.data.get("type_name") or "Notice"
        message = request.data.get("message") or ""
        if not isinstance(users, (list, tuple)) or not users:
            raise ValidationError({"users": "Provide a non-empty list of user ids."})
        if not str(message).strip():
            raise ValidationError({"message": "Message is required."})
        recipients = list(User.objects.filter(pk__in=users))
        sent = NotificationService.send_bulk_notifications(
            recipients,
            title=str(title),
            message=str(message),
            notification_type=request.data.get("notification_type", "in_app"),
        )
        return Response({"sent": len(sent)})


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """Per-user notification type toggles. Users manage their own rows only."""

    queryset = NotificationPreference.objects.all()
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["type", "enabled"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["type_id", "id"]

    def _is_staff_manager(self, user) -> bool:
        return bool(
            user.is_staff
            or user.is_superuser
            or (
                hasattr(user, "has_any_role")
                and user.has_any_role(["coordinator", "admin"])
            )
        )

    def get_queryset(self):
        qs = NotificationPreference.objects.select_related("user", "type").order_by(
            "type_id", "id"
        )
        user = self.request.user
        if self._is_staff_manager(user):
            return qs
        return qs.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        if self._is_staff_manager(user):
            serializer.save()
            return
        target = serializer.validated_data.get("user", user)
        if target != user:
            raise PermissionDenied("You can only create preferences for yourself.")
        serializer.save(user=user)

    def perform_update(self, serializer):
        user = self.request.user
        if not self._is_staff_manager(user) and serializer.instance.user_id != user.id:
            raise PermissionDenied("You can only update your own preferences.")
        if not self._is_staff_manager(user):
            serializer.save(user=user)
            return
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if not self._is_staff_manager(user) and instance.user_id != user.id:
            raise PermissionDenied("You can only delete your own preferences.")
        instance.delete()


@extend_schema_view(
    list=extend_schema(
        tags=["notifications"],
        summary="List notification routing overrides",
        description=(
            "Staff-only. Paginated list of admin-configurable routing overrides (reminder event types "
            "and transactional route keys). Affects live reminder dispatch and the routing-reference API. "
            "**Filters:** ``kind``, ``key``, ``settings_category``, ``is_active``. **Search:** ``key``. "
            "**Ordering:** ``updated_at``, ``created_at``, ``kind``, ``key`` (default: ``kind``, ``key``)."
        ),
    ),
    create=extend_schema(
        tags=["notifications"],
        summary="Create notification routing override",
        description=(
            "Create an override. **Unique** on (``kind``, ``key``). "
            "``settings_category`` may be ``ungated`` so matching reminders bypass user preference gating."
        ),
        responses={
            201: NotificationRoutingOverrideSerializer,
            400: OpenApiResponse(description="Validation error."),
            403: OpenApiResponse(
                description="Forbidden without coordinator or admin role."
            ),
        },
    ),
    retrieve=extend_schema(
        tags=["notifications"],
        summary="Retrieve notification routing override",
        responses={
            200: NotificationRoutingOverrideSerializer,
            403: OpenApiResponse(
                description="Forbidden without coordinator or admin role."
            ),
        },
    ),
    update=extend_schema(
        tags=["notifications"],
        summary="Replace notification routing override",
        responses={
            200: NotificationRoutingOverrideSerializer,
            400: OpenApiResponse(description="Validation error."),
            403: OpenApiResponse(
                description="Forbidden without coordinator or admin role."
            ),
        },
    ),
    partial_update=extend_schema(
        tags=["notifications"],
        summary="Update notification routing override",
        responses={
            200: NotificationRoutingOverrideSerializer,
            400: OpenApiResponse(description="Validation error."),
            403: OpenApiResponse(
                description="Forbidden without coordinator or admin role."
            ),
        },
    ),
    destroy=extend_schema(
        tags=["notifications"],
        summary="Delete notification routing override",
        responses={
            204: OpenApiResponse(description="No content."),
            403: OpenApiResponse(
                description="Forbidden without coordinator or admin role."
            ),
        },
    ),
)
class NotificationRoutingOverrideViewSet(viewsets.ModelViewSet):
    """
    Staff-only CRUD for admin-configurable notification routing overrides.

    These overrides affect reminder event-type routing and staff documentation indices.
    """

    queryset = NotificationRoutingOverride.objects.all()
    serializer_class = NotificationRoutingOverrideSerializer
    permission_classes = [IsAuthenticated, IsCoordinatorOrAdmin]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["kind", "key", "settings_category", "is_active"]
    search_fields = ["key"]
    ordering_fields = ["updated_at", "created_at", "kind", "key"]
    ordering = ["kind", "key"]


class ReminderViewSet(viewsets.ModelViewSet):
    """ViewSet for user reminders. Admins can list and assign any user."""

    queryset = Reminder.objects.all()
    serializer_class = ReminderSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["sent", "event_type", "user"]
    search_fields = ["event_title", "user__email", "user__username"]
    ordering_fields = ["remind_at", "created_at"]
    ordering = ["remind_at"]

    def get_queryset(self):
        queryset = Reminder.objects.select_related("user", "notification")
        user = self.request.user
        if user.is_staff or getattr(user, "is_admin", False):
            return queryset
        return queryset.filter(user=user)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        """Get upcoming reminders (not sent yet)."""
        reminders = self.get_queryset().filter(sent=False).order_by("remind_at")[:10]
        serializer = self.get_serializer(reminders, many=True)
        return Response(serializer.data)
