from django.test import Client, TestCase

from accounts.models import Role, User


class DynformsAccessTest(TestCase):
    """Test that Dynforms Form Builder is accessible for admin users."""

    def setUp(self):
        """Set up test data."""
        # Create admin role (use get_or_create to handle existing roles)
        self.admin_role, created = Role.objects.get_or_create(name='admin')

        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        self.admin_user.roles.add(self.admin_role)

        # Create regular user (non-admin)
        self.regular_user = User.objects.create_user(
            username='student',
            email='student@test.com',
            password='student123'
        )

        self.client = Client()

    def test_dynforms_accessible_for_admin(self):
        """Test that admin users can access the Dynforms page."""
        # Login as admin
        self.client.login(username='admin', password='admin123')

        # Access the Dynforms page
        response = self.client.get('/dynforms/')

        # Should return 200 OK
        self.assertEqual(response.status_code, 200)

        # Should use the correct template
        self.assertIn('dynforms/builder.html', response.template_name)

        # Should contain the Dynforms JavaScript and CSS files
        self.assertContains(response, 'dynforms.min.js')
        self.assertContains(response, 'dynforms.min.css')
        self.assertContains(response, 'jquery-ui.min.js')
        self.assertContains(response, 'jquery.form.min.js')

    def test_dynforms_inaccessible_for_non_admin(self):
        """Test that non-admin users cannot access the Dynforms page."""
        # Login as regular user
        self.client.login(username='student', password='student123')

        # Try to access the Dynforms page
        response = self.client.get('/dynforms/')

        # Should return 403 Forbidden
        self.assertEqual(response.status_code, 403)

    def test_dynforms_inaccessible_for_anonymous(self):
        """Test that anonymous users cannot access the Dynforms page."""
        # Don't login (anonymous user)

        # Try to access the Dynforms page
        response = self.client.get('/dynforms/')

        # Should redirect to login (302) or return 403 Forbidden
        self.assertIn(response.status_code, [302, 403])

    def test_dynforms_builder_edit_accessible_for_admin(self):
        """Test that admin users can access the Dynforms builder edit page."""
        # Login as admin
        self.client.login(username='admin', password='admin123')

        # Access the Dynforms builder edit page (with a dummy ID)
        response = self.client.get('/dynforms/builder/1/')

        # Should return 200 OK or 404 (if form doesn't exist)
        self.assertIn(response.status_code, [200, 404])

        # If it returns 200, should use the correct template
        if response.status_code == 200:
            self.assertIn('dynforms/builder.html', response.template_name)
