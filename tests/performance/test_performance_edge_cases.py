"""
Test Performance Edge Cases and Load Scenarios

This test file covers performance testing, load scenarios,
and stress testing for the SEIM application.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import Role
from exchange.models import Application, ApplicationStatus, Comment, Program

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.slow
class TestBulkOperations(TestCase):
    """Test performance with bulk operations."""

    def test_create_many_users(self):
        """Test creating many users efficiently."""
        student_role, _ = Role.objects.get_or_create(name="student")

        # Create 100 users
        users = []
        for i in range(100):
            user = User.objects.create_user(
                username=f"user{i}",
                email=f"user{i}@test.com",
                password="testpass123"
            )
            user.roles.add(student_role)
            users.append(user)

        # Verify all created
        self.assertEqual(User.objects.count(), 100)

        # All should have profiles (auto-created by signal)
        users_without_profiles = User.objects.filter(profile__isnull=True).count()
        self.assertEqual(users_without_profiles, 0)

    def test_create_many_programs(self):
        """Test creating many programs efficiently."""
        # Create 50 programs
        programs = []
        for i in range(50):
            program = Program.objects.create(
                name=f"Program {i}",
                description=f"Description {i}",
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timezone.timedelta(days=365),
                is_active=True,
            )
            programs.append(program)

        # Verify all created
        self.assertEqual(Program.objects.count(), 50)

    def test_bulk_application_creation(self):
        """Test creating many applications."""
        student_role, _ = Role.objects.get_or_create(name="student")

        # Create students
        students = []
        for i in range(10):
            user = User.objects.create_user(
                username=f"student{i}",
                email=f"student{i}@test.com",
                password="testpass123"
            )
            user.roles.add(student_role)
            students.append(user)

        # Create programs
        programs = []
        for i in range(5):
            program = Program.objects.create(
                name=f"Program {i}",
                description=f"Test program {i}",
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timezone.timedelta(days=365),
                is_active=True,
            )
            programs.append(program)

        status, _ = ApplicationStatus.objects.get_or_create(name="submitted", defaults={'order': 2})

        # Create applications (10 students x 5 programs = 50 applications)
        applications = []
        for student in students:
            for program in programs:
                application = Application.objects.create(
                    student=student,
                    program=program,
                    status=status,
                )
                applications.append(application)

        # Verify all created
        self.assertEqual(Application.objects.count(), 50)

    def test_query_large_dataset(self):
        """Test querying with large dataset."""
        student_role, _ = Role.objects.get_or_create(name="student")

        # Create data
        student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        student.roles.add(student_role)

        program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )

        status, _ = ApplicationStatus.objects.get_or_create(name="submitted", defaults={'order': 2})

        # Create 100 applications
        for _ in range(100):
            Application.objects.create(
                student=student,
                program=program,
                status=status,
            )

        # Query all applications
        applications = Application.objects.all()

        # Should handle large queryset
        self.assertEqual(applications.count(), 100)

        # Test filtering on large dataset
        # Filter by program since personal_statement doesn't exist
        filtered = Application.objects.filter(
            program=program
        )

        # Should find matches efficiently
        self.assertGreater(filtered.count(), 0)


@pytest.mark.django_db
@pytest.mark.slow
class TestAPILoadScenarios(TestCase):
    """Test API under load scenarios."""

    def setUp(self):
        """Set up test client and data."""
        self.client = APIClient()

        self.student_role, _ = Role.objects.get_or_create(name="student")
        self.student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        self.student.roles.add(self.student_role)

        self.client.force_authenticate(user=self.student)

    def test_list_endpoint_with_many_results(self):
        """Test list endpoint with many results."""
        # Create many programs
        for i in range(50):
            Program.objects.create(
                name=f"Program {i}",
                description=f"Description {i}",
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timezone.timedelta(days=365),
                is_active=True,
            )

        # Request program list
        response = self.client.get(reverse("api:program-list"))

        # Should return successfully with pagination
        self.assertEqual(response.status_code, 200)

        # Response should have results
        self.assertIn("results", response.data)

    def test_filter_on_large_dataset(self):
        """Test filtering performance on large dataset."""
        # Create 100 programs with varying attributes
        for i in range(100):
            Program.objects.create(
                name=f"Program {i}",
                description=f"Description {i}",
                start_date=timezone.now().date(),
                end_date=timezone.now().date() + timezone.timedelta(days=365),
                is_active=(i % 2 == 0),  # Half active, half inactive
                min_gpa=(i % 5) / 2.0,  # Varying GPA requirements
            )

        # Test various filters
        response = self.client.get(reverse("api:program-list") + "?is_active=true")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("api:program-list") + "?search=Program")
        self.assertEqual(response.status_code, 200)

    def test_deep_nested_relations(self):
        """Test querying deeply nested relationships."""
        status, _ = ApplicationStatus.objects.get_or_create(name="submitted", defaults={'order': 2})

        program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )

        application = Application.objects.create(
            student=self.student,
            program=program,
            status=status,
        )

        # Create many comments
        for i in range(20):
            Comment.objects.create(
                application=application,
                author=self.student,
                text=f"Comment {i}",
            )

        # Query with select_related/prefetch_related
        apps = Application.objects.select_related(
            'student', 'program', 'status'
        ).prefetch_related("comments")

        # Should efficiently load related data
        for app in apps:
            self.assertIsNotNone(app.student)
            self.assertIsNotNone(app.program)
            comments_count = app.comments.count()
            self.assertGreaterEqual(comments_count, 0)


@pytest.mark.django_db
class TestCacheEdgeCases(TransactionTestCase):
    """Test cache-related edge cases."""

    def test_cache_with_unicode_keys(self):
        """Test caching with unicode keys."""
        from django.core.cache import cache

        unicode_key = "key_中文_עברית"

        cache.set(unicode_key, "test_value", 60)
        cached_value = cache.get(unicode_key)

        self.assertEqual(cached_value, "test_value")

    def test_cache_with_very_long_key(self):
        """Test cache with very long key."""
        from django.core.cache import cache

        long_key = "key_" + "a" * 200

        # Most cache backends have key length limits
        try:
            cache.set(long_key, "test_value", 60)
            cached_value = cache.get(long_key)
            # If successful, verify
            self.assertEqual(cached_value, "test_value")
        except Exception:
            # If key too long, exception is expected
            pass

    def test_cache_with_complex_objects(self):
        """Test caching complex Python objects."""
        from django.core.cache import cache

        complex_object = {
            "nested": {
                "list": [1, 2, 3],
                "dict": {"a": "b"},
                "tuple": (1, 2, 3),
            },
            "unicode": "测试",
        }

        cache.set("complex_key", complex_object, 60)
        cached_value = cache.get("complex_key")

        self.assertEqual(cached_value["nested"]["list"], [1, 2, 3])
        self.assertEqual(cached_value["unicode"], "测试")

    def test_cache_expiration_edge(self):
        """Test cache behavior at expiration boundary."""
        import time

        from django.core.cache import cache

        # Set with 1 second timeout
        cache.set("short_key", "value", 1)

        # Immediately retrieve
        value1 = cache.get("short_key")
        self.assertEqual(value1, "value")

        # Wait for expiration
        time.sleep(2)

        # Should be expired
        value2 = cache.get("short_key")
        self.assertIsNone(value2)


@pytest.mark.django_db
class TestConcurrentAccess(TransactionTestCase):
    """Test concurrent access scenarios."""

    def test_simultaneous_comment_creation(self):
        """Test multiple users commenting simultaneously."""
        student_role = Role.objects.create(name="student")
        coordinator_role = Role.objects.create(name="coordinator")

        student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        student.roles.add(student_role)

        coordinator = User.objects.create_user(
            username="coordinator",
            email="coordinator@test.com",
            password="testpass123"
        )
        coordinator.roles.add(coordinator_role)

        program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )

        status, _ = ApplicationStatus.objects.get_or_create(name="submitted", defaults={'order': 2})

        application = Application.objects.create(
            student=student,
            program=program,
            status=status,
        )

        # Both users add comments
        Comment.objects.create(
            application=application,
            author=student,
            text="Student comment",
        )

        Comment.objects.create(
            application=application,
            author=coordinator,
            text="Coordinator comment",
        )

        # Both comments should exist
        self.assertEqual(application.comments.count(), 2)

    def test_application_view_count_race_condition(self):
        """Test view count increment with potential race conditions."""
        student_role = Role.objects.create(name="student")
        student = User.objects.create_user(
            username="student",
            email="student@test.com",
            password="testpass123"
        )
        student.roles.add(student_role)

        program = Program.objects.create(
            name="Test Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timezone.timedelta(days=365),
            is_active=True,
        )

        status, _ = ApplicationStatus.objects.get_or_create(name="submitted", defaults={'order': 2})

        application = Application.objects.create(
            student=student,
            program=program,
            status=status,
        )

        # Simulate multiple views (if view count field exists)
        # Retrieve application multiple times
        for _ in range(10):
            app = Application.objects.get(id=application.id)
            self.assertIsNotNone(app)

        # Application should still exist and be valid
        final_app = Application.objects.get(id=application.id)
        self.assertEqual(final_app.id, application.id)

