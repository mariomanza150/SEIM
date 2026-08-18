"""
Tests for URL configuration in SEIM project.
"""

from django.apps import apps
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import NoReverseMatch, reverse

from tests.wagtail_site import ensure_wagtail_site_root_live

User = get_user_model()


class UrlConfigurationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        ensure_wagtail_site_root_live()

    def test_root_url_public_home_or_wagtail(self):
        """Site root is public CMS (Wagtail when installed), not the ``/seim/`` SPA shell."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertNotIn('id="app"', body)
        if not apps.is_installed("wagtail"):
            self.assertIn("student exchange information manager", body.lower())
            self.assertIn("<title>", body.lower())

    def test_seim_url_resolves_to_vue_app(self):
        """``/seim/`` serves the Vue shell template (``index.html``)."""
        response = self.client.get("/seim/")
        self.assertEqual(response.status_code, 200)
        self.assertIn('id="app"', str(response.content))

    def test_django_admin_legacy_path_redirects(self):
        """``/django/admin/`` redirects to Django admin at ``/seim/django-admin/``."""
        response = self.client.get("/django/admin/", follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get("Location"), "/seim/django-admin/")

    def test_wagtail_admin_url(self):
        """Wagtail CMS admin is only mounted when ``wagtail`` is installed."""
        response = self.client.get("/cms/", follow=False)
        if apps.is_installed("wagtail"):
            self.assertEqual(response.status_code, 302)
        else:
            self.assertEqual(response.status_code, 404)

    def test_api_url_requires_auth_or_documents_itself(self):
        """API root may return 401 (JWT) or 200 (e.g. browsable API) depending on config."""
        response = self.client.get("/api/")
        self.assertIn(response.status_code, (200, 401))

    def test_root_auth_routes_are_registered(self):
        """Legacy paths outside ``/seim/`` redirect to the Vue auth shell."""
        self.assertEqual(self.client.get("/dashboard/", follow=False).status_code, 302)
        self.assertEqual(
            self.client.get("/dashboard/", follow=False).headers.get("Location"),
            "/seim/dashboard/",
        )
        self.assertEqual(
            self.client.get("/admin-dashboard/", follow=False).status_code, 302
        )
        self.assertEqual(
            self.client.get("/admin-dashboard/", follow=False).headers.get("Location"),
            "/seim/dashboard/",
        )
        self.assertEqual(
            self.client.get("/dashboard/analytics/", follow=False).status_code, 302
        )
        self.assertEqual(
            self.client.get("/dashboard/analytics/", follow=False).headers.get(
                "Location"
            ),
            "/seim/analytics-forecasts/",
        )
        self.assertEqual(self.client.get("/login/", follow=False).status_code, 302)
        self.assertEqual(
            self.client.get("/login/", follow=False).headers.get("Location"),
            "/seim/login/",
        )
        self.assertEqual(self.client.get("/register/", follow=False).status_code, 302)
        self.assertEqual(
            self.client.get("/register/", follow=False).headers.get("Location"),
            "/seim/register/",
        )
        self.assertEqual(
            self.client.get("/password-reset/", follow=False).status_code, 302
        )
        self.assertEqual(
            self.client.get("/password-reset/", follow=False).headers.get("Location"),
            "/seim/password-reset/",
        )

    def test_root_logout_route_redirects(self):
        """The public logout route clears session and sends users to the Vue login shell."""
        response = self.client.get("/logout/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get("Location"), "/seim/login/")

    def test_jsreverse_route_is_registered(self):
        """JavaScript reverse URL endpoint is registered."""
        response = self.client.get("/jsreverse/")
        self.assertEqual(response.status_code, 200)

    def test_authentication_integration(self):
        """Staff session can reach Django admin; Wagtail admin when installed."""
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get("/seim/django-admin/", follow=True)
        self.assertEqual(response.status_code, 200)

        if apps.is_installed("wagtail"):
            response = self.client.get("/cms/", follow=True)
            self.assertEqual(response.status_code, 200)

    def test_redirects(self):
        """``/admin/`` and legacy Django admin path redirect to ``/seim/django-admin/``."""
        response = self.client.get("/admin/", follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get("Location"), "/seim/django-admin/")

        response = self.client.get("/django/admin/", follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get("Location"), "/seim/django-admin/")

    def test_legacy_app_paths_redirect_into_spa(self):
        """Bookmarks and notification action URLs outside ``/seim/`` reach the SPA."""
        cases = [
            ("/applications/", "/seim/applications/"),
            ("/applications/create/", "/seim/applications/new"),
            ("/applications/new/", "/seim/applications/new"),
            ("/profile/", "/seim/profile/"),
            ("/settings/", "/seim/settings/"),
            ("/preferences/", "/seim/settings/"),
            ("/calendar/", "/seim/calendar/"),
            ("/documents/", "/seim/documents/"),
            ("/notifications/", "/seim/notifications/"),
            ("/review-queue/", "/seim/review-queue/"),
            ("/programs/compare/", "/seim/programs/compare"),
        ]
        for source, target in cases:
            response = self.client.get(source, follow=False)
            self.assertEqual(response.status_code, 302, msg=source)
            self.assertEqual(response.headers.get("Location"), target, msg=source)

    def test_legacy_application_detail_redirects_into_spa(self):
        app_id = "11111111-1111-1111-1111-111111111111"
        response = self.client.get(f"/applications/{app_id}/", follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers.get("Location"), f"/seim/applications/{app_id}"
        )

        response = self.client.get(f"/applications/{app_id}/edit/", follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers.get("Location"), f"/seim/applications/{app_id}/edit"
        )

    def test_contact_form_route_not_vue_shell(self):
        """Legacy Django contact form is mounted at ``/contact/`` (not the SPA)."""
        response = self.client.get("/contact/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('id="app"', response.content.decode())


class VueAppRoutingTests(TestCase):
    def test_vue_app_catch_all(self):
        """Paths under ``/seim/`` are served by the Vue shell template."""
        test_paths = [
            "/seim/login/",
            "/seim/register/",
            "/seim/dashboard",
            "/seim/applications",
            "/seim/applications/new",
            "/seim/documents",
            "/seim/profile",
            "/seim/admin/programs",
            "/seim/nonexistent-page",
        ]

        for path in test_paths:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertIn('id="app"', str(response.content))

    def test_legacy_frontend_url_namespace_is_gone(self):
        """The removed Django ``frontend`` app must not register URL names."""
        with self.assertRaises(NoReverseMatch):
            reverse("frontend:login")
        with self.assertRaises(NoReverseMatch):
            reverse("frontend:dashboard")

    def test_vue_app_excludes_admin_cms_api(self):
        """Admin, CMS, and API paths are not the Vue ``index.html`` shell."""
        excluded_paths = [
            "/django/admin/",
            "/seim/django-admin/",
            "/cms/",
            "/api/",
            "/media/",
            "/static/",
        ]

        for path in excluded_paths:
            response = self.client.get(path, follow=False)
            self.assertNotIn(
                'id="app"',
                str(response.content),
                msg=f"Unexpected Vue shell for {path} (status {response.status_code})",
            )
