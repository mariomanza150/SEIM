"""JWT API for the SPA data-management console."""

from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DataOperationLog
from .views import data_management_catalog


class IsSeimAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return bool(
            user.is_staff or user.is_superuser or getattr(user, "is_admin", False)
        )


class DataManagementCatalogView(APIView):
    permission_classes = [IsAuthenticated, IsSeimAdmin]

    def get(self, request):
        return Response({"sections": data_management_catalog(request.user)})


class DataManagementLogsView(APIView):
    permission_classes = [IsAuthenticated, IsSeimAdmin]

    def get(self, request):
        logs = DataOperationLog.objects.select_related("user")[:20]
        return Response(
            {
                "results": [
                    {
                        "id": str(log.id),
                        "operation_type": log.operation_type,
                        "model_name": log.model_name,
                        "status": log.status,
                        "record_count": log.record_count,
                        "created_at": log.created_at,
                        "user": getattr(log.user, "email", None) if log.user else None,
                    }
                    for log in logs
                ]
            }
        )
