"""Template context shared across Django/Wagtail pages."""

from core.branding import brand_from_settings


def institution(request):
    """Expose configurable institution branding (UAdeC defaults)."""
    from django.conf import settings

    return {"institution": brand_from_settings(settings)}
