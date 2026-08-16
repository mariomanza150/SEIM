from django.test import Client, TestCase

from accounts.models import Role, User


class DynformsAccessTest(TestCase):
    """Legacy /dynforms/ URLs redirect admins into the Vue visual builder."""

    def setUp(self):
        self.admin_role, _created = Role.objects.get_or_create(name="admin")
        self.admin_user = User.objects.create_user(
            username="admin", email="admin@test.com", password="admin123"
        )
        self.admin_user.roles.add(self.admin_role)
        self.regular_user = User.objects.create_user(
            username="student", email="student@test.com", password="student123"
        )
        self.client = Client()

    def test_dynforms_accessible_for_admin(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.get("/dynforms/")
        self.assertRedirects(
            response, "/seim/admin/dynforms", fetch_redirect_response=False
        )

    def test_dynforms_inaccessible_for_non_admin(self):
        self.client.login(username="student", password="student123")
        response = self.client.get("/dynforms/")
        self.assertEqual(response.status_code, 403)

    def test_dynforms_inaccessible_for_anonymous(self):
        response = self.client.get("/dynforms/")
        self.assertIn(response.status_code, [302, 403])

    def test_dynforms_builder_edit_accessible_for_admin(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.get("/dynforms/builder/1/")
        self.assertRedirects(
            response, "/seim/admin/dynforms/1", fetch_redirect_response=False
        )

    def test_application_forms_html_list_redirects_to_spa(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.get("/api/application-forms/list/")
        self.assertRedirects(
            response, "/seim/admin/dynforms", fetch_redirect_response=False
        )

    def test_application_forms_html_builder_redirects_to_spa(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.get("/api/application-forms/builder/4/")
        self.assertRedirects(
            response, "/seim/admin/dynforms/4", fetch_redirect_response=False
        )
