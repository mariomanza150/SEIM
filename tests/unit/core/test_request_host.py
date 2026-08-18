"""Tests for request-host Wagtail Site alignment."""

from unittest.mock import Mock

import pytest
from django.test import RequestFactory

from core.request_host import (
    RequestHostWagtailSiteMiddleware,
    align_site_with_request,
    request_site_identity,
)


def test_request_site_identity_uses_https_port_443():
    request = RequestFactory().get("/", HTTP_HOST="box.tailnet.ts.net")
    request.is_secure = lambda: True
    assert request_site_identity(request) == ("box.tailnet.ts.net", 443)


def test_request_site_identity_keeps_lan_http_port():
    request = RequestFactory().get("/", HTTP_HOST="192.168.1.20:8020")
    request.is_secure = lambda: False
    assert request_site_identity(request) == ("192.168.1.20", 8020)


def test_align_site_with_request_does_not_mutate_original():
    request = RequestFactory().get("/", HTTP_HOST="box.tailnet.ts.net")
    request.is_secure = lambda: True
    site = Mock(hostname="localhost", port=8000)
    aligned = align_site_with_request(site, request)
    assert aligned.hostname == "box.tailnet.ts.net"
    assert aligned.port == 443
    assert site.hostname == "localhost"
    assert site.port == 8000


@pytest.mark.django_db
def test_middleware_sets_cached_site_from_request_host():
    from django.conf import settings

    if "cms" not in settings.INSTALLED_APPS or not any(
        app == "wagtail" or app.startswith("wagtail.") for app in settings.INSTALLED_APPS
    ):
        pytest.skip("Wagtail/CMS not in INSTALLED_APPS for this settings module")

    from wagtail.models import Page, Site

    root = Page.get_first_root_node()
    site = Site.objects.filter(is_default_site=True).first()
    if site is None:
        site = Site.objects.create(
            hostname="localhost",
            port=8000,
            root_page=root,
            is_default_site=True,
            site_name="SEIM",
        )
    else:
        site.hostname = "localhost"
        site.port = 8000
        site.save()

    captured = {}

    def get_response(request):
        captured["site"] = getattr(
            request, "_wagtail_site", getattr(request, "_wagtail_cached_site", None)
        )
        return Mock()

    middleware = RequestHostWagtailSiteMiddleware(get_response)
    request = RequestFactory().get("/seim/login/", HTTP_HOST="box.tailnet.ts.net")
    request.is_secure = lambda: True
    middleware(request)

    aligned = captured["site"]
    assert aligned is not None
    assert aligned.hostname == "box.tailnet.ts.net"
    assert aligned.port == 443
    site.refresh_from_db()
    assert site.hostname == "localhost"
    assert site.port == 8000
