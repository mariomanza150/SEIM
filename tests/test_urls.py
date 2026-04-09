"""
Tests for URL configuration in SEIM project.
"""
from django.apps import apps
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UrlConfigurationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_root_url_public_home_or_wagtail(self):
        """Site root is public content (Wagtail or Django marketing), not the ``/seim/`` SPA shell."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertNotIn('id="app"', body)
        if not apps.is_installed("wagtail"):
            self.assertIn("student exchange information manager", body.lower())

    def test_seim_url_resolves_to_vue_app(self):
        """``/seim/`` serves the Vue shell template (``index.html``)."""
        response = self.client.get("/seim/")
        self.assertEqual(response.status_code, 200)
        self.assertIn('id="app"', str(response.content))

    def test_django_admin_legacy_path_redirects(self):
        """``/django/admin/`` redirects to the unified admin at ``/seim/admin/``."""
        response = self.client.get("/django/admin/", follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get("Location"), "/seim/admin/")

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
        """Public auth routes exist outside the SPA base path."""
        routes = [
            "/dashboard/",
            "/login/",
            "/register/",
            "/password-reset/",
        ]

        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)

    def test_root_logout_route_redirects(self):
        """The public logout route is registered."""
        response = self.client.get("/logout/")
        self.assertEqual(response.status_code, 302)

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

        response = self.client.get("/seim/admin/", follow=True)
        self.assertEqual(response.status_code, 200)

        if apps.is_installed("wagtail"):
            response = self.client.get("/cms/", follow=True)
            self.assertEqual(response.status_code, 200)

    def test_redirects(self):
        """``/admin/`` and legacy Django admin path redirect to ``/seim/admin/``."""
        response = self.client.get("/admin/", follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get("Location"), "/seim/admin/")

        response = self.client.get("/django/admin/", follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers.get("Location"), "/seim/admin/")

    def test_contact_form_route_not_vue_shell(self):
        """Legacy Django contact form is mounted at ``/contact/`` (not the SPA)."""
        response = self.client.get("/contact/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('id="app"', response.content.decode())


class VueAppRoutingTests(TestCase):
    def test_vue_app_catch_all(self):
        """Paths under ``/seim/`` are served by the Vue shell template."""
        test_paths = [
            "/seim/dashboard",
            "/seim/applications",
            "/seim/applications/new",
            "/seim/documents",
            "/seim/profile",
            "/seim/nonexistent-page",
        ]

        for path in test_paths:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertIn('id="app"', str(response.content))

    def test_vue_app_excludes_admin_cms_api(self):
        """Admin, CMS, and API paths are not the Vue ``index.html`` shell."""
        excluded_paths = [
            "/django/admin/",
            "/seim/admin/",
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
