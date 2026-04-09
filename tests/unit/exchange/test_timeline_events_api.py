from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Profile, Role, User
from exchange.models import Application, ApplicationStatus, Program, TimelineEvent


class TestTimelineEventsAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student_role, _ = Role.objects.get_or_create(name="student")
        self.coord_role, _ = Role.objects.get_or_create(name="coordinator")
        self.student = User.objects.create_user(
            username="tl-student",
            email="tl-student@example.com",
            password="testpass123",
        )
        self.student.roles.add(self.student_role)
        Profile.objects.get_or_create(user=self.student)
        self.coordinator = User.objects.create_user(
            username="tl-coord",
            email="tl-coord@example.com",
            password="testpass123",
        )
        self.coordinator.roles.add(self.coord_role)
        self.client.force_authenticate(user=self.student)

        self.program = Program.objects.create(
            name="TL Program",
            description="Test",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=60),
            is_active=True,
        )
        self.draft, _ = ApplicationStatus.objects.get_or_create(
            name="draft",
            defaults={"order": 1},
        )
        self.application = Application.objects.create(
            program=self.program,
            student=self.student,
            status=self.draft,
        )
        TimelineEvent.objects.create(
            application=self.application,
            event_type="submitted",
            description="Application submitted.",
            created_by=self.coordinator,
        )

    def test_list_filtered_by_application_includes_created_by_name(self):
        response = self.client.get(
            "/api/timeline-events/",
            {"application": str(self.application.id), "ordering": "created_at"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rows = response.data.get("results", response.data)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["event_type"], "submitted")
        self.assertEqual(rows[0]["created_by_name"], self.coordinator.username)

    def test_student_cannot_see_other_students_timeline(self):
        other = User.objects.create_user(
            username="tl-other",
            email="tl-other@example.com",
            password="testpass123",
        )
        other.roles.add(self.student_role)
        Profile.objects.get_or_create(user=other)
        other_app = Application.objects.create(
            program=self.program,
            student=other,
            status=self.draft,
        )
        TimelineEvent.objects.create(
            application=other_app,
            event_type="submitted",
            description="Other submitted.",
            created_by=other,
        )

        response = self.client.get(
            "/api/timeline-events/",
            {"application": str(other_app.id)},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rows = response.data.get("results", response.data)
        self.assertEqual(len(rows), 0)
