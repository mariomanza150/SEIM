"""JWT API for the SPA data-management console."""

from django.http import Http404
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DataOperationLog
from .operations import (
    DataManagementError,
    data_management_catalog,
    execute_section,
    list_section_items,
    serialize_log,
)


class IsSeimAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return bool(
            user.is_staff or user.is_superuser or getattr(user, "is_admin", False)
        )


def _error_response(exc):
    return Response({"detail": exc.message}, status=exc.code)


class DataManagementCatalogView(APIView):
    permission_classes = [IsAuthenticated, IsSeimAdmin]

    def get(self, request):
        return Response({"sections": data_management_catalog(request.user)})


class DataManagementLogsView(APIView):
    permission_classes = [IsAuthenticated, IsSeimAdmin]

    def get(self, request):
        logs = DataOperationLog.objects.select_related("user")[:20]
        return Response({"results": [serialize_log(log) for log in logs]})


class DataManagementResourcesView(APIView):
    permission_classes = [IsAuthenticated, IsSeimAdmin]

    def get(self, request):
        section = request.query_params.get("section")
        try:
            items = list_section_items(request.user, section)
        except DataManagementError as exc:
            return _error_response(exc)
        return Response({"section": section, "results": items})


class DataManagementExecuteView(APIView):
    permission_classes = [IsAuthenticated, IsSeimAdmin]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request):
        section = request.data.get("section")
        cleanup = request.data.get("cleanup_options")
        if isinstance(cleanup, str):
            cleanup = None
        if cleanup is None:
            cleanup = {
                "clean_orphaned": request.data.get("clean_orphaned"),
                "clean_duplicates": request.data.get("clean_duplicates"),
                "clean_invalid": request.data.get("clean_invalid"),
            }
        try:
            result = execute_section(
                request.user,
                section,
                item_id=request.data.get("item_id"),
                confirm=request.data.get("confirm"),
                cleanup_options=cleanup,
                uploaded_file=request.FILES.get("file"),
                source="spa",
            )
        except Http404:
            return Response({"detail": "Not found."}, status=404)
        except DataManagementError as exc:
            return _error_response(exc)
        return Response(
            {"message": result["message"], "log": serialize_log(result["log"])}
        )
