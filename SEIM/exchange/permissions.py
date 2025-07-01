"""
Custom permissions for the exchange application.
"""

from rest_framework import permissions


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object or staff to access it.
    """

    def has_object_permission(self, request, view, obj):
        # Staff have all permissions
        if request.user.is_staff:
            return True

        # Check if the user is the owner
        if hasattr(obj, "student"):
            return obj.student == request.user
        elif hasattr(obj, "uploaded_by"):
            return obj.uploaded_by == request.user

        return False


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Permission to allow staff full access and others read-only access.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff


class CanVerifyDocuments(permissions.BasePermission):
    """
    Permission to verify documents.
    """

    def has_permission(self, request, view):
        return request.user.has_perm("exchange.can_verify_document")

    def has_object_permission(self, request, view, obj):
        return request.user.has_perm("exchange.can_verify_document")


class CanReviewExchange(permissions.BasePermission):
    """
    Permission to review exchange applications.
    """

    def has_permission(self, request, view):
        return request.user.has_perm("exchange.can_review_exchange")

    def has_object_permission(self, request, view, obj):
        return request.user.has_perm("exchange.can_review_exchange")


class CanApproveExchange(permissions.BasePermission):
    """
    Permission to approve exchange applications.
    """

    def has_permission(self, request, view):
        return request.user.has_perm("exchange.can_approve_exchange")

    def has_object_permission(self, request, view, obj):
        return request.user.has_perm("exchange.can_approve_exchange")
