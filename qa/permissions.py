from django.http import Http404
from rest_framework.permissions import BasePermission

from .gating import get_tester, get_triager, is_impersonating, tester_tools_enabled


class ToolsEnabled(BasePermission):
    """404 (not 403) when the environment gate is closed, so prod reveals nothing."""

    def has_permission(self, request, view):
        if not tester_tools_enabled():
            raise Http404
        return True


class IsTester(BasePermission):
    def has_permission(self, request, view):
        if not tester_tools_enabled():
            raise Http404
        if get_tester(request) is None:
            raise Http404
        return True


class IsTriager(BasePermission):
    def has_permission(self, request, view):
        if not tester_tools_enabled():
            raise Http404
        if get_triager(request) is None:
            raise Http404
        return True


class NotImpersonating(BasePermission):
    """Block sensitive endpoints while a switched/impersonation token is in use."""

    message = "Not allowed while testing as another user."

    def has_permission(self, request, view):
        return not is_impersonating(request)
