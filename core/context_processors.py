"""Template context shared across Django/Wagtail pages."""

from django.conf import settings


def institution(request):
    """Expose configurable institution branding (UAdeC defaults)."""
    theme = getattr(settings, "INSTITUTION_THEME", {}) or {}
    short_name = getattr(settings, "INSTITUTION_SHORT_NAME", "SEIM")
    tagline = getattr(settings, "INSTITUTION_TAGLINE", "")
    nav_brand = getattr(settings, "INSTITUTION_NAV_BRAND", "") or " ".join(
        part for part in (short_name, tagline) if part
    )
    return {
        "institution": {
            "name": getattr(settings, "INSTITUTION_NAME", "SEIM"),
            "short_name": short_name,
            "tagline": tagline,
            "department": getattr(settings, "INSTITUTION_DEPARTMENT", ""),
            "location": getattr(settings, "INSTITUTION_LOCATION", ""),
            "website": getattr(settings, "INSTITUTION_WEBSITE", ""),
            "logo_url": getattr(settings, "INSTITUTION_LOGO_URL", ""),
            "nav_brand": nav_brand,
            "social_facebook": getattr(settings, "INSTITUTION_SOCIAL_FACEBOOK", ""),
            "social_twitter": getattr(settings, "INSTITUTION_SOCIAL_TWITTER", ""),
            "social_instagram": getattr(settings, "INSTITUTION_SOCIAL_INSTAGRAM", ""),
            "theme": theme,
        }
    }
