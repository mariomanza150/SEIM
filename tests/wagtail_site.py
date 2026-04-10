"""Helpers for tests that need a live Wagtail site root at ``/``."""

from django.apps import apps
from django.test import Client


def ensure_wagtail_site_root_live():
    """Publish a ``HomePage`` at the default site root if ``GET /`` would otherwise 404."""
    if not apps.is_installed("wagtail"):
        return
    from cms.models import HomePage
    from wagtail.models import Page, Site

    client = Client()
    if client.get("/").status_code == 200:
        return
    site = Site.objects.filter(is_default_site=True).first()
    if site is None:
        return
    root = Page.get_first_root_node()
    home = HomePage(title="Test home", slug="home")
    root.add_child(instance=home)
    home.save_revision().publish()
    site.root_page = home
    site.save(update_fields=["root_page_id"])
