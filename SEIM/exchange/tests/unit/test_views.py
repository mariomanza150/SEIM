"""
Unit tests for Exchange views
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from exchange.forms import ExchangeForm
from exchange.models import Document, Exchange, UserProfile

TEST_PASSWORD = "testpass123"


class BaseTestCase(TestCase):
    """Base test case with common setup for all tests"""

    def setUp(self):
        self.client = Client()

        # Create test users
        self.student_user = User.objects.create_user(
            username="student1", email="student@test.com", password=TEST_PASSWORD
        )
        self.student_profile = UserProfile.objects.create(
            user=self.student_user, role="STUDENT", phone_number="+1234567890"
        )

        self.coordinator_user = User.objects.create_user(
            username="coordinator1",
            email="coordinator@test.com",
            password=TEST_PASSWORD,
        )
        self.coordinator_profile = UserProfile.objects.create(user=self.coordinator_user, role="COORDINATOR")

        self.admin_user = User.objects.create_user(
            username="admin1",
            email="admin@test.com",
            password=TEST_PASSWORD,
            is_staff=True,
        )
        self.admin_profile = UserProfile.objects.create(user=self.admin_user, role="ADMINISTRATOR")

        # Create test exchange
        self.exchange = Exchange.objects.create(
            student=self.student_user,
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            phone_number="+1234567890",
            academic_level="BACHELOR",
            current_university="Test University",
            host_university="Host University",
            host_country="Germany",
            start_date=timezone.now().date() + timedelta(days=90),
            end_date=timezone.now().date() + timedelta(days=180),
            status="DRAFT",
        )


class DashboardViewTest(BaseTestCase):
    """Test cases for dashboard view"""

    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication"""
        response = self.client.get(reverse("exchange:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_student_dashboard(self):
        """Test student can access dashboard"""
        self.client.login(username="student1", password=TEST_PASSWORD)
        response = self.client.get(reverse("exchange:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Exchanges")

    def test_coordinator_dashboard(self):
        """Test coordinator can access dashboard with different content"""
        self.client.login(username="coordinator1", password=TEST_PASSWORD)
        response = self.client.get(reverse("exchange:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pending Reviews")


class ExchangeListViewTest(BaseTestCase):
    """Test cases for exchange list view"""

    def test_exchange_list_requires_login(self):
        """Test that exchange list requires authentication"""
        response = self.client.get(reverse("exchange:exchange-list"))
        self.assertEqual(response.status_code, 302)

    def test_student_sees_own_exchanges(self):
        """Test student only sees their own exchanges"""
        # Create another student's exchange
        other_student = User.objects.create_user("student2", "student2@test.com", TEST_PASSWORD)
        UserProfile.objects.create(user=other_student, role="STUDENT")
        other_exchange = Exchange.objects.create(
            student=other_student,
            first_name="Jane",
            last_name="Smith",
            status="SUBMITTED",
        )

        self.client.login(username="student1", password=TEST_PASSWORD)
        response = self.client.get(reverse("exchange:exchange-list"))

        self.assertContains(response, "John Doe")
        self.assertNotContains(response, "Jane Smith")

    def test_coordinator_sees_all_exchanges(self):
        """Test coordinator sees all exchanges"""
        self.client.login(username="coordinator1", password=TEST_PASSWORD)
        response = self.client.get(reverse("exchange:exchange-list"))

        self.assertContains(response, "John Doe")
        self.assertEqual(response.status_code, 200)

    def test_filter_by_status(self):
        """Test filtering exchanges by status"""
        # Create exchanges with different statuses
        submitted_exchange = Exchange.objects.create(
            student=self.student_user,
            first_name="Test",
            last_name="Submitted",
            status="SUBMITTED",
        )

        self.client.login(username="coordinator1", password=TEST_PASSWORD)
        response = self.client.get(reverse("exchange:exchange-list") + "?status=SUBMITTED")

        self.assertContains(response, "Test Submitted")
        self.assertNotContains(response, "John Doe")  # Draft status


class ExchangeDetailViewTest(BaseTestCase):
    """Test cases for exchange detail view"""

    def test_detail_view_requires_login(self):
        """Test that detail view requires authentication"""
        response = self.client.get(reverse("exchange:exchange-detail", args=[self.exchange.id]))
        self.assertEqual(response.status_code, 302)

    def test_student_can_view_own_exchange(self):
        """Test student can view their own exchange"""
        self.client.login(username="student1", password=TEST_PASSWORD)
        response = self.client.get(reverse("exchange:exchange-detail", args=[self.exchange.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")
        self.assertContains(response, "Host University")

    def test_student_cannot_view_others_exchange(self):
        """Test student cannot view other's exchange"""
        other_student = User.objects.create_user("student2", "student2@test.com", TEST_PASSWORD)
        UserProfile.objects.create(user=other_student, role="STUDENT")
        other_exchange = Exchange.objects.create(student=other_student, first_name="Other", last_name="Student")

        self.client.login(username="student1", password=TEST_PASSWORD)
        response = self.client.get(reverse("exchange:exchange-detail", args=[other_exchange.id]))

        self.assertEqual(response.status_code, 403)

    def test_coordinator_can_view_any_exchange(self):
        """Test coordinator can view any exchange"""
        self.client.login(username="coordinator1", password=TEST_PASSWORD)
        response = self.client.get(reverse("exchange:exchange-detail", args=[self.exchange.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John Doe")


class ExchangeCreateViewTest(BaseTestCase):
    """Test cases for exchange creation"""

    def test_create_requires_login(self):
        """Test that creating exchange requires authentication"""
        response = self.client.get(reverse("exchange:create-exchange"))
        self.assertEqual(response.status_code, 302)

    def test_only_students_can_create(self):
        """Test that only students can create exchanges"""
        self.client.login(username="coordinator1", password=TEST_PASSWORD)
        response = self.client.get(reverse("exchange:create-exchange"))
        self.assertEqual(response.status_code, 403)

    def test_create_exchange_get(self):
        """Test GET request for create exchange"""
        self.client.login(username="student1", password=TEST_PASSWORD)
        response = self.client.get(reverse("exchange:create-exchange"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create Exchange Application")

    def test_create_exchange_post_valid(self):
        """Test POST request with valid data"""
        self.client.login(username="student1", password=TEST_PASSWORD)

        data = {
            "first_name": "New",
            "last_name": "Exchange",
            "email": "new@test.com",
            "phone_number": "+9876543210",
            "academic_level": "MASTER",
            "current_university": "Current Uni",
            "host_university": "New Host Uni",
            "host_country": "France",
            "start_date": (timezone.now().date() + timedelta(days=100)).isoformat(),
            "end_date": (timezone.now().date() + timedelta(days=200)).isoformat(),
            "action": "submit",
        }

        response = self.client.post(reverse("exchange:create-exchange"), data)

        # Check if exchange was created
        new_exchange = Exchange.objects.filter(
            student=self.student_user, first_name="New", last_name="Exchange"
        ).first()

        self.assertIsNotNone(new_exchange)
        self.assertEqual(new_exchange.status, "SUBMITTED")
        self.assertRedirects(response, reverse("exchange:exchange-detail", args=[new_exchange.id]))

    def test_create_exchange_save_draft(self):
        """Test saving exchange as draft"""
        self.client.login(username="student1", password=TEST_PASSWORD)

        data = {
            "first_name": "Draft",
            "last_name": "Exchange",
            "email": "draft@test.com",
            "action": "save_draft",
        }

        response = self.client.post(reverse("exchange:create-exchange"), data)

        draft_exchange = Exchange.objects.filter(student=self.student_user, first_name="Draft").first()

        self.assertIsNotNone(draft_exchange)
        self.assertEqual(draft_exchange.status, "DRAFT")


class ExchangeEditViewTest(BaseTestCase):
    """Test cases for exchange editing"""

    def test_edit_requires_login(self):
        """Test that editing requires authentication"""
        response = self.client.get(reverse("exchange:exchange-edit", args=[self.exchange.id]))
        self.assertEqual(response.status_code, 302)

    def test_student_can_edit_draft(self):
        """Test student can edit their draft exchange"""
        self.client.login(username="student1", password=TEST_PASSWORD)
        response = self.client.get(reverse("exchange:exchange-edit", args=[self.exchange.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Exchange Application")

    def test_student_cannot_edit_submitted(self):
        """Test student cannot edit submitted exchange"""
        self.exchange.status = "SUBMITTED"
        self.exchange.save()

        self.client.login(username="student1", password=TEST_PASSWORD)
        response = self.client.get(reverse("exchange:exchange-edit", args=[self.exchange.id]))

        self.assertEqual(response.status_code, 403)

    def test_coordinator_can_edit_any_status(self):
        """Test coordinator can edit exchange in any status"""
        self.exchange.status = "SUBMITTED"
        self.exchange.save()

        self.client.login(username="coordinator1", password=TEST_PASSWORD)
        response = self.client.get(reverse("exchange:exchange-edit", args=[self.exchange.id]))

        self.assertEqual(response.status_code, 200)


class WorkflowActionsTest(BaseTestCase):
    """Test cases for workflow actions"""

    def test_student_submit_exchange(self):
        """Test student can submit draft exchange"""
        self.client.login(username="student1", password=TEST_PASSWORD)

        response = self.client.post(
            reverse("exchange:exchange-submit", args=[self.exchange.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.exchange.refresh_from_db()
        self.assertEqual(self.exchange.status, "SUBMITTED")
        self.assertEqual(response.status_code, 200)

    def test_coordinator_start_review(self):
        """Test coordinator can start review"""
        self.exchange.status = "SUBMITTED"
        self.exchange.save()

        self.client.login(username="coordinator1", password=TEST_PASSWORD)

        response = self.client.post(
            reverse("exchange:exchange-review", args=[self.exchange.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.exchange.refresh_from_db()
        self.assertEqual(self.exchange.status, "UNDER_REVIEW")

    def test_coordinator_approve_exchange(self):
        """Test coordinator can approve exchange"""
        self.exchange.status = "UNDER_REVIEW"
        self.exchange.save()

        self.client.login(username="coordinator1", password=TEST_PASSWORD)

        response = self.client.post(
            reverse("exchange:exchange-approve", args=[self.exchange.id]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.exchange.refresh_from_db()
        self.assertEqual(self.exchange.status, "APPROVED")

    def test_coordinator_reject_exchange(self):
        """Test coordinator can reject exchange"""
        self.exchange.status = "UNDER_REVIEW"
        self.exchange.save()

        self.client.login(username="coordinator1", password=TEST_PASSWORD)

        response = self.client.post(
            reverse("exchange:exchange-reject", args=[self.exchange.id]),
            data={"reason": "Missing documents"},
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.exchange.refresh_from_db()
        self.assertEqual(self.exchange.status, "REJECTED")
