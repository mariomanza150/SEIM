"""Align Wagtail Site hostname/port with the current request host.

Wagtail builds absolute URLs from ``Site.hostname`` / ``Site.port``. Those default
to ``localhost`` (often port 8000), so a page served at ``https://<tailnet>.ts.net``
or ``http://192.168.x.x:8020`` can emit ``http://localhost:8000/...`` or
``https://localhost/...`` links. Browsers then hit localhost over TLS and show a
certificate error.

This middleware copies the default site onto the request (it does not write the DB)
and sets hostname/port from the incoming Host / proxy headers.
"""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from django.http.request import split_domain_port

if TYPE_CHECKING:
    from wagtail.models import Site


def request_site_identity(request) -> tuple[str, int]:
    """Hostname and Wagtail Site port for the current request."""
    host = request.get_host()
    hostname, host_port = split_domain_port(host)
    hostname = hostname or "localhost"
    if request.is_secure():
        return hostname, 443
    if host_port:
        return hostname, int(host_port)
    return hostname, int(request.get_port() or 80)


def align_site_with_request(site: Site, request) -> Site:
    """Return a shallow copy of *site* whose root URL matches this request."""
    aligned = copy.copy(site)
    hostname, port = request_site_identity(request)
    aligned.hostname = hostname
    aligned.port = port
    return aligned


class RequestHostWagtailSiteMiddleware:
    """Point Wagtail ``request._wagtail_site`` at the current Host."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from wagtail.models import Site

        site = Site.objects.filter(is_default_site=True).first()
        if site is not None:
            aligned = align_site_with_request(site, request)
            # Wagtail 6 used ``_wagtail_cached_site``; Wagtail 7 uses ``_wagtail_site``.
            request._wagtail_site = aligned
            request._wagtail_cached_site = aligned
        return self.get_response(request)
