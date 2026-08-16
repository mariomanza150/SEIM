"""SPA data-management catalog API."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Role

User = get_user_model()


class DataManagementAPITests(APITestCase):
    def setUp(self):
        admin_role, _ = Role.objects.get_or_create(name="admin")
        self.admin = User.objects.create_user(
            username="dm-admin",
            email="dm-admin@example.com",
            password="testpass123",
            is_staff=True,
            is_superuser=True,
        )
        self.admin.roles.add(admin_role)
        self.student = User.objects.create_user(
            username="dm-student",
            email="dm-student@example.com",
            password="testpass123",
        )

    def test_catalog_requires_admin(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.get("/api/data-management/catalog/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_read_catalog_and_logs(self):
        self.client.force_authenticate(user=self.admin)
        catalog = self.client.get("/api/data-management/catalog/")
        self.assertEqual(catalog.status_code, status.HTTP_200_OK)
        self.assertTrue(catalog.data["sections"])
        self.assertTrue(all("url" in row for row in catalog.data["sections"]))

        logs = self.client.get("/api/data-management/logs/")
        self.assertEqual(logs.status_code, status.HTTP_200_OK)
        self.assertIn("results", logs.data)
