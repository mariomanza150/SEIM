"""SPA help-center API and public FAQ surface guards.

Requires Wagtail + cms::

    DJANGO_SETTINGS_MODULE=seim.settings.test_cms
"""

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from rest_framework import status

if "wagtail" not in settings.INSTALLED_APPS or "cms" not in settings.INSTALLED_APPS:
    pytest.skip("Wagtail disabled in test settings", allow_module_level=True)

from tests.utils import APITestCase


def _publish_help_tree():
    from wagtail.models import Page, Site

    from cms.help import (
        FAQ_AUDIENCE_ALL,
        FAQ_AUDIENCE_PARTNER,
        FAQ_AUDIENCE_STUDENT,
        FAQ_INDEX_KIND_SPA_HELP,
        FAQ_SURFACE_PUBLIC,
        FAQ_SURFACE_SPA,
    )
    from cms.models import FAQIndexPage, FAQPage, HomePage

    root = Page.get_first_root_node()
    site = Site.objects.get(is_default_site=True)
    home = HomePage(
        title="Home Help",
        slug="home-help-api",
        hero_title="T",
        hero_subtitle="S",
    )
    root.add_child(instance=home)
    home.save_revision().publish()
    site.root_page = home
    site.save()

    spa_index = FAQIndexPage(
        title="SPA Help",
        slug="ayuda-seim-test",
        introduction="In-app",
        index_kind=FAQ_INDEX_KIND_SPA_HELP,
    )
    home.add_child(instance=spa_index)
    spa_index.save_revision().publish()

    public_index = FAQIndexPage(
        title="Public FAQ",
        slug="preguntas-frecuentes-test",
        introduction="Public",
        index_kind="public",
    )
    home.add_child(instance=public_index)
    public_index.save_revision().publish()

    student = FAQPage(
        title="Student apply help",
        slug="student-apply-help",
        introduction="How to apply",
        audiences=[FAQ_AUDIENCE_STUDENT],
        surfaces=[FAQ_SURFACE_SPA],
        topic="applications",
        contextual_keys="ApplicationNew,ApplicationEdit",
        body=[{"type": "paragraph", "value": "<p>Student body</p>"}],
    )
    spa_index.add_child(instance=student)
    student.save_revision().publish()

    partner = FAQPage(
        title="Partner portal help",
        slug="partner-portal-help",
        introduction="Partner overview",
        audiences=[FAQ_AUDIENCE_PARTNER],
        surfaces=[FAQ_SURFACE_SPA],
        topic="partner",
        contextual_keys="PartnerPortal",
        body=[{"type": "paragraph", "value": "<p>Partner body</p>"}],
    )
    spa_index.add_child(instance=partner)
    partner.save_revision().publish()

    shared = FAQPage(
        title="Dashboard help",
        slug="dashboard-help-all",
        introduction="For everyone",
        audiences=[FAQ_AUDIENCE_ALL],
        surfaces=[FAQ_SURFACE_SPA],
        topic="getting_started",
        contextual_keys="Dashboard",
        body=[{"type": "paragraph", "value": "<p>All roles</p>"}],
    )
    spa_index.add_child(instance=shared)
    shared.save_revision().publish()

    public_faq = FAQPage(
        title="Public FAQ article",
        slug="public-faq-help-test",
        introduction="Public",
        audiences=[FAQ_AUDIENCE_STUDENT],
        surfaces=[FAQ_SURFACE_PUBLIC, FAQ_SURFACE_SPA],
        topic="applications",
        contextual_keys="",
        body=[{"type": "paragraph", "value": "<p>Public</p>"}],
    )
    public_index.add_child(instance=public_faq)
    public_faq.save_revision().publish()

    return {
        "student": student,
        "partner": partner,
        "shared": shared,
        "public_faq": public_faq,
        "spa_index": spa_index,
        "public_index": public_index,
    }


class TestHelpArticlesAPI(APITestCase):
    def setUp(self):
        super().setUp()
        self.pages = _publish_help_tree()
        self.student = self.create_user(
            role="student", username="help-stu", email="help-stu@test.com"
        )
        self.partner = self.create_user(
            role="partner", username="help-par", email="help-par@test.com"
        )
        self.coord = self.create_user(
            role="responsible", username="help-coord", email="help-coord@test.com"
        )

    def test_unauthenticated_rejected(self):
        url = reverse("api:help-article-list")
        resp = self.client.get(url)
        self.assertIn(
            resp.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
        )

    def test_student_list_excludes_partner_only(self):
        self.authenticate_user(self.student)
        url = reverse("api:help-article-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        slugs = {row["slug"] for row in resp.data["results"]}
        self.assertIn("student-apply-help", slugs)
        self.assertIn("dashboard-help-all", slugs)
        self.assertNotIn("partner-portal-help", slugs)
        student_row = next(r for r in resp.data["results"] if r["slug"] == "student-apply-help")
        self.assertIn("<p>", student_row["body_html"])

    def test_partner_cannot_read_student_slug(self):
        self.authenticate_user(self.partner)
        detail = reverse("api:help-article-detail", kwargs={"slug": "student-apply-help"})
        resp = self.client.get(detail)
        self.assertEqual(resp.status_code, 404)
        list_url = reverse("api:help-article-list")
        resp = self.client.get(list_url)
        slugs = {row["slug"] for row in resp.data["results"]}
        self.assertIn("partner-portal-help", slugs)
        self.assertNotIn("student-apply-help", slugs)

    def test_key_filter_returns_tagged_article(self):
        self.authenticate_user(self.student)
        url = reverse("api:help-article-list")
        resp = self.client.get(url, {"key": "ApplicationNew"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)
        self.assertEqual(resp.data["results"][0]["slug"], "student-apply-help")

    def test_responsible_can_read_student_help(self):
        self.authenticate_user(self.coord)
        detail = reverse("api:help-article-detail", kwargs={"slug": "student-apply-help"})
        resp = self.client.get(detail)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["slug"], "student-apply-help")


@pytest.mark.django_db
def test_spa_only_faq_404_on_public_serve():
    pages = _publish_help_tree()
    client = Client()
    url = pages["student"].url
    assert url
    resp = client.get(url)
    assert resp.status_code == 404


@pytest.mark.django_db
def test_spa_help_index_404_on_public_serve():
    pages = _publish_help_tree()
    client = Client()
    url = pages["spa_index"].url
    assert url
    resp = client.get(url)
    assert resp.status_code == 404


@pytest.mark.django_db
def test_public_surface_faq_still_serves():
    pages = _publish_help_tree()
    client = Client()
    url = pages["public_faq"].url
    assert url
    resp = client.get(url)
    assert resp.status_code == 200


@pytest.mark.django_db
def test_spa_only_pages_excluded_from_wagtail_pages_api_queryset():
    """PublicPagesAPIViewSet must not list spa-only FAQ pages or spa_help indexes."""
    from django.test import RequestFactory

    from cms.wagtail_api import PublicPagesAPIViewSet

    pages = _publish_help_tree()
    request = RequestFactory().get("/api/cms/pages/")
    view = PublicPagesAPIViewSet()
    view.request = request
    view.action = "listing"
    ids = set(view.get_queryset().values_list("pk", flat=True))
    assert pages["student"].id not in ids
    assert pages["partner"].id not in ids
    assert pages["spa_index"].id not in ids
    assert pages["public_faq"].id in ids
    assert pages["public_index"].id in ids


def test_seed_spa_help_contextual_keys_match_vue_routes():
    """Catalog keys must use Vue route names (no dead ApplicationForm)."""
    from cms.management.commands.seed_spa_help import PUBLIC_FAQ_RETAG, SPA_HELP_ARTICLES

    keys: set[str] = set()
    for article in SPA_HELP_ARTICLES:
        keys.update(
            part.strip()
            for part in article["contextual_keys"].split(",")
            if part.strip()
        )
    for meta in PUBLIC_FAQ_RETAG.values():
        keys.update(
            part.strip()
            for part in meta["contextual_keys"].split(",")
            if part.strip()
        )

    assert "ApplicationForm" not in keys
    assert "AdminWorkflowCatalogs" in keys
    assert "AdminDynformEditor" in keys
    assert "AdminApplicationEdit" in keys
    assert "ApplicationNew" in keys
    assert "ApplicationEdit" in keys
