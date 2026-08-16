"""SPA data-management catalog and execute API."""

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Role
from data_management.models import DataExport, DataImport, DataOperationLog

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
        self.export_config = DataExport.objects.create(
            name="Export users",
            model_name="accounts.user",
            format="CSV",
            created_by=self.admin,
        )
        self.import_config = DataImport.objects.create(
            name="Import users",
            model_name="accounts.user",
            format="CSV",
            created_by=self.admin,
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
        self.assertTrue(
            all(
                row["url"].startswith("/seim/admin/data-management")
                for row in catalog.data["sections"]
            )
        )

        logs = self.client.get("/api/data-management/logs/")
        self.assertEqual(logs.status_code, status.HTTP_200_OK)
        self.assertIn("results", logs.data)

    def test_admin_can_list_and_execute_export(self):
        self.client.force_authenticate(user=self.admin)
        resources = self.client.get(
            "/api/data-management/resources/", {"section": "data_export"}
        )
        self.assertEqual(resources.status_code, status.HTTP_200_OK)
        self.assertEqual(resources.data["results"][0]["name"], "Export users")

        execute = self.client.post(
            "/api/data-management/execute/",
            {"section": "data_export", "item_id": str(self.export_config.id)},
            format="json",
        )
        self.assertEqual(execute.status_code, status.HTTP_200_OK)
        self.assertEqual(
            DataOperationLog.objects.get(operation_type="EXPORT").status, "PENDING"
        )

    def test_admin_can_reset_and_cleanup(self):
        self.client.force_authenticate(user=self.admin)
        denied = self.client.post(
            "/api/data-management/execute/",
            {"section": "database", "confirm": "NOPE"},
            format="json",
        )
        self.assertEqual(denied.status_code, status.HTTP_400_BAD_REQUEST)

        reset = self.client.post(
            "/api/data-management/execute/",
            {"section": "database", "confirm": "RESET"},
            format="json",
        )
        self.assertEqual(reset.status_code, status.HTTP_200_OK)
        self.assertTrue(DataOperationLog.objects.filter(operation_type="DB_RESET").exists())

        cleanup = self.client.post(
            "/api/data-management/execute/",
            {
                "section": "data_cleanup",
                "cleanup_options": {"clean_orphaned": True},
            },
            format="json",
        )
        self.assertEqual(cleanup.status_code, status.HTTP_200_OK)
        self.assertTrue(DataOperationLog.objects.filter(operation_type="CLEANUP").exists())

    def test_admin_can_import_students(self):
        self.client.force_authenticate(user=self.admin)
        upload = SimpleUploadedFile(
            "users.csv",
            b"email,username,first_name,last_name\napi@example.com,apiuser,Api,User\n",
            content_type="text/csv",
        )
        response = self.client.post(
            "/api/data-management/execute/",
            {
                "section": "data_import",
                "item_id": str(self.import_config.id),
                "file": upload,
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(email="api@example.com").exists())
