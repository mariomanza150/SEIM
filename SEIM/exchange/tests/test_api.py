"""
Test cases for Exchange API views
"""

import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from exchange.models import Exchange
from rest_framework import status
from rest_framework.test import APIClient


class ExchangeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.client.force_authenticate(user=self.user)

        self.exchange_data = {
            "student": self.user.id,
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "university": "Test University",
            "program": "Business Administration",
            "start_date": "2025-09-01",
            "end_date": "2026-06-30",
            "status": "DRAFT",
            "notes": "Test exchange application",
        }

    def test_create_exchange(self):
        """Test creating an exchange through the API"""
        url = reverse("exchange-list")
        response = self.client.post(url, self.exchange_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Exchange.objects.count(), 1)
        self.assertEqual(Exchange.objects.get().first_name, "Jane")

    def test_list_exchanges(self):
        """Test listing exchanges through the API"""
        Exchange.objects.create(
            student=self.user,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            university="Test University",
            program="Computer Science",
            start_date=datetime.date(2025, 9, 1),
            end_date=datetime.date(2026, 6, 30),
            status="DRAFT",
        )

        url = reverse("exchange-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
