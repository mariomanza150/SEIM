"""
Unit tests for exchange views.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from exchange.models import Application, ApplicationStatus, Program

User = get_user_model()

@pytest.mark.django_db
class TestProgramViews:
    """Test cases for program-related views."""

    def test_program_list_view(self):
        client = APIClient()
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        # Create test programs
        Program.objects.create(
            name="Test Program 1",
            description="Test Description 1",
            is_active=True,
            start_date="2024-01-01",
            end_date="2024-06-30"
        )
        Program.objects.create(
            name="Test Program 2",
            description="Test Description 2",
            is_active=True,
            start_date="2024-07-01",
            end_date="2024-12-31"
        )
        # Unauthenticated
        response = client.get(reverse('api:program-list'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        # JWT Auth
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = client.get(reverse('api:program-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        # Session Auth
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(reverse('api:program-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_program_detail_view(self):
        client = APIClient()
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        program = Program.objects.create(
            name="Test Program",
            description="Test Description",
            is_active=True,
            start_date="2024-01-01",
            end_date="2024-06-30"
        )
        # Unauthenticated
        response = client.get(reverse('api:program-detail', kwargs={'pk': program.pk}))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        # JWT Auth
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = client.get(reverse('api:program-detail', kwargs={'pk': program.pk}))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == "Test Program"
        assert response.data['description'] == "Test Description"
        # Session Auth
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(reverse('api:program-detail', kwargs={'pk': program.pk}))
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == "Test Program"
        assert response.data['description'] == "Test Description"

@pytest.mark.django_db
class TestApplicationViews:
    """Test cases for application-related views."""

    def test_application_list_view(self):
        client = APIClient()
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        program = Program.objects.create(
            name="Test Program",
            description="Test Description",
            is_active=True,
            start_date="2024-01-01",
            end_date="2024-06-30"
        )
        status_obj, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={"order": 1})
        Application.objects.create(
            student=user,
            program=program,
            status=status_obj
        )
        Application.objects.create(
            student=user,
            program=program,
            status=status_obj
        )
        # Unauthenticated
        response = client.get(reverse('api:application-list'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        # JWT Auth
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = client.get(reverse('api:application-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        # Session Auth
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(reverse('api:application-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_application_detail_view(self):
        client = APIClient()
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        program = Program.objects.create(
            name="Test Program",
            description="Test Description",
            is_active=True,
            start_date="2024-01-01",
            end_date="2024-06-30"
        )
        status_obj, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={"order": 1})
        application = Application.objects.create(
            student=user,
            program=program,
            status=status_obj
        )
        # Unauthenticated
        response = client.get(reverse('api:application-detail', kwargs={'pk': application.pk}))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        # JWT Auth
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = client.get(reverse('api:application-detail', kwargs={'pk': application.pk}))
        assert response.status_code == status.HTTP_200_OK
        assert str(response.data["program"]) == str(program.pk)
        # Session Auth
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(reverse('api:application-detail', kwargs={'pk': application.pk}))
        assert response.status_code == status.HTTP_200_OK
        assert str(response.data["program"]) == str(program.pk)

    def test_application_create_view(self):
        client = APIClient()
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        program = Program.objects.create(
            name="Test Program",
            description="Test Description",
            is_active=True,
            start_date="2024-01-01",
            end_date="2024-06-30"
        )
        status_obj, _ = ApplicationStatus.objects.get_or_create(name="draft", defaults={"order": 1})
        data = {
            "program": program.pk,
            "status": status_obj.pk
        }
        # JWT Auth
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = client.post(reverse('api:application-list'), data)
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_201_CREATED]
        # Session Auth
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(reverse('api:application-list'), data)
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_201_CREATED]

