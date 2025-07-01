"""
Test cases for authentication and permissions system.
"""

from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from exchange.models import Exchange, UserProfile
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class AuthenticationTestCase(TestCase):
    """Test cases for authentication system"""

    def setUp(self):
        self.client = APIClient()

        # Create test users with different roles
        self.student_user = User.objects.create_user(
            username="student1", email="student1@test.com", password="testpass123"
        )
        self.student_profile = UserProfile.objects.create(
            user=self.student_user, role="STUDENT", institution="Test University"
        )

        self.coordinator_user = User.objects.create_user(
            username="coordinator1",
            email="coordinator1@test.com",
            password="testpass123",
            is_staff=True,
        )
        self.coordinator_profile = UserProfile.objects.create(
            user=self.coordinator_user,
            role="COORDINATOR",
            institution="Test University",
        )

        self.manager_user = User.objects.create_user(
            username="manager1",
            email="manager1@test.com",
            password="testpass123",
            is_staff=True,
        )
        self.manager_profile = UserProfile.objects.create(
            user=self.manager_user, role="MANAGER", institution="Test University"
        )

    def test_login(self):
        """Test login functionality"""
        response = self.client.post("/api/auth/login/", {"username": "student1", "password": "testpass123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertIn("user", response.data)
        self.assertIn("profile", response.data)

    def test_logout(self):
        """Test logout functionality"""
        token = Token.objects.create(user=self.student_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        response = self.client.post("/api/auth/logout/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify token is deleted
        self.assertFalse(Token.objects.filter(user=self.student_user).exists())

    def test_registration(self):
        """Test user registration"""
        response = self.client.post(
            "/api/auth/register/",
            {
                "username": "newstudent",
                "email": "newstudent@test.com",
                "password": "newpass123",
                "first_name": "New",
                "last_name": "Student",
                "institution": "New University",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)

        # Verify user was created with student role
        new_user = User.objects.get(username="newstudent")
        self.assertEqual(new_user.profile.role, "STUDENT")


class PermissionTestCase(TestCase):
    """Test cases for permission system"""

    def setUp(self):
        self.client = APIClient()

        # Create test users
        self.student1 = User.objects.create_user(username="student1", password="test123")
        self.student1_profile = UserProfile.objects.create(user=self.student1, role="STUDENT")
        self.student1_token = Token.objects.create(user=self.student1)

        self.student2 = User.objects.create_user(username="student2", password="test123")
        self.student2_profile = UserProfile.objects.create(user=self.student2, role="STUDENT")
        self.student2_token = Token.objects.create(user=self.student2)

        self.coordinator = User.objects.create_user(username="coord1", password="test123", is_staff=True)
        self.coordinator_profile = UserProfile.objects.create(user=self.coordinator, role="COORDINATOR")
        self.coordinator_token = Token.objects.create(user=self.coordinator)

        # Create test exchange
        self.exchange1 = Exchange.objects.create(
            student=self.student1,
            first_name="Test",
            last_name="Student",
            email="test@test.com",
            birthdate=date(2000, 1, 1),
            gender="M",
            nationality="Test Country",
            passport_number="TEST123456",
            passport_issue_date=date(2020, 1, 1),
            passport_expiry_date=date(2030, 1, 1),
            passport_issuing_country="Test Country",
            home_university="Test University",
            academic_year="3",
            major="Computer Science",
            host_university="Host University",
            host_country="Host Country",
            exchange_program="Test Program",
            start_date=date(2025, 9, 1),
            end_date=date(2026, 5, 31),
            emergency_contact_name="Emergency Contact",
            emergency_contact_relationship="Parent",
            emergency_contact_phone="+1234567890",
            emergency_contact_email="emergency@test.com",
        )

    def test_student_can_view_own_exchange(self):
        """Test that students can view their own exchanges"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.student1_token.key}")
        response = self.client.get(f"/api/exchanges/{self.exchange1.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_cannot_view_others_exchange(self):
        """Test that students cannot view other students' exchanges"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.student2_token.key}")
        response = self.client.get(f"/api/exchanges/{self.exchange1.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_coordinator_can_view_all_exchanges(self):
        """Test that coordinators can view all exchanges"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.coordinator_token.key}")
        response = self.client.get("/api/exchanges/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data["results"]), 1)

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated requests are denied"""
        response = self.client.get("/api/exchanges/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
