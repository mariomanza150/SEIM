"""Application Django admin changelist query-count regressions."""

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext

from tests.utils import APITestCase

User = get_user_model()


class ApplicationAdminChangelistPerfTests(APITestCase):
    def setUp(self):
        super().setUp()
        self.admin_user = User.objects.create_superuser(
            username="admin_changelist_perf",
            email="admin_changelist_perf@example.com",
            password="pass12345",
        )
        self.client = Client()
        self.client.force_login(self.admin_user)
        self.url = "/seim/django-admin/exchange/application/"
        self.program = self.create_program()

    def _seed(self, n: int) -> None:
        for _ in range(n):
            student = self.create_user(role="student")
            self.create_application(
                student=student, program=self.program, status_name="draft"
            )

    def _changelist_query_count(self) -> tuple[int, int]:
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # Count application rows rendered; Django admin uses result_list.
        result_list = response.context["cl"].result_list
        return len(ctx.captured_queries), len(result_list)

    def test_application_changelist_query_count_does_not_grow_with_rows(self):
        """Changelist must not re-run eligibility (or FK lookups) per row."""
        self._seed(3)
        count_small, n_small = self._changelist_query_count()
        self.assertEqual(n_small, 3)

        self._seed(9)
        count_large, n_large = self._changelist_query_count()
        self.assertEqual(n_large, 12)

        self.assertLessEqual(
            count_large,
            count_small + 2,
            f"Query count grew from {count_small} (3 rows) to {count_large} "
            f"(12 rows); application admin changelist still looks N+1.",
        )
        with self.assertNumQueries(count_large):
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(count_large, 40)

    def test_eligibility_status_column_is_lightweight(self):
        from django.contrib import admin

        from exchange.admin import ApplicationAdmin

        app = self.create_application(
            student=self.create_user(role="student"),
            program=self.program,
            status_name="draft",
        )
        ma = ApplicationAdmin(app.__class__, admin.site)
        with CaptureQueriesContext(connection) as ctx:
            html = str(ma.eligibility_status(app))
        self.assertIn("Open detail to check", html)
        self.assertLessEqual(len(ctx.captured_queries), 0)
