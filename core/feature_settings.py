"""Helpers for institution feature flags."""

from django.core.cache import cache

from core.models import InstitutionFeatureSettings

_SCHOLARSHIPS_ENABLED_CACHE_KEY = "institution:scholarships_enabled"
_SCHOLARSHIPS_ENABLED_CACHE_TIMEOUT = 60


def scholarships_enabled() -> bool:
    """Return whether scholarship surfaces/APIs should be exposed."""
    cached = cache.get(_SCHOLARSHIPS_ENABLED_CACHE_KEY)
    if cached is not None:
        return bool(cached)
    value = bool(InstitutionFeatureSettings.scholarships_are_enabled())
    cache.set(
        _SCHOLARSHIPS_ENABLED_CACHE_KEY,
        value,
        timeout=_SCHOLARSHIPS_ENABLED_CACHE_TIMEOUT,
    )
    return value


def clear_scholarships_enabled_cache() -> None:
    """Drop the cached scholarships flag (call after admin toggles)."""
    cache.delete(_SCHOLARSHIPS_ENABLED_CACHE_KEY)


def scholarships_disabled_response():
    """DRF 404 payload when scholarship features are turned off."""
    from rest_framework import status
    from rest_framework.response import Response

    return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
