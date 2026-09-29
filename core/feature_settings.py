"""Helpers for institution feature flags."""

from core.models import InstitutionFeatureSettings


def scholarships_enabled() -> bool:
    """Return whether scholarship surfaces/APIs should be exposed."""
    return InstitutionFeatureSettings.scholarships_are_enabled()


def scholarships_disabled_response():
    """DRF 404 payload when scholarship features are turned off."""
    from rest_framework import status
    from rest_framework.response import Response

    return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
