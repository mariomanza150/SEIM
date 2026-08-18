"""URL helpers for CMS templates served behind LAN / Tailscale hosts."""

from __future__ import annotations

import re

from django import template

register = template.Library()

_LOCALHOST_ABSOLUTE = re.compile(
    r"^https?://(?:localhost|127\.0\.0\.1)(?::\d+)?(/.*)?$",
    re.IGNORECASE,
)


def localhost_url_to_path(url: str | None) -> str:
    """Turn ``http://localhost:8000/programas/`` into ``/programas/``."""
    if not url:
        return ""
    stripped = url.strip()
    match = _LOCALHOST_ABSOLUTE.match(stripped)
    if not match:
        return stripped
    return match.group(1) or "/"


@register.filter(name="site_href")
def site_href(url: str | None) -> str:
    """Filter for ``href`` values so localhost absolute links stay same-origin."""
    return localhost_url_to_path(url)
