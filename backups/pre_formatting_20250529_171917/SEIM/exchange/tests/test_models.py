"""
Test cases for Exchange models
"""

import datetime
import tempfile
import os

from django.contrib.auth.models import User
from django.test import TestCase
from django.core.files import File
from PIL import Image

from exchange.models import Document, Exchange


class ExchangeModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_exchange_creation(self):
        """Test Exchange model can be created with valid data"""
        exchange = Exchange.objects.create(
            student=self.user,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            current_university="Test University",
            current_program="Computer Science",
            destination_university="Host University",
            destination_country="Germany",
            exchange_program="Semester Exchange",
            start_date=datetime.date(2025, 9, 1),
            end_date=datetime.date(2026, 6, 30),
            status="DRAFT",
            student_number="12345",
        )
        self.assertEqual(exchange.first_name, "John")
        self.assertEqual(exchange.current_university, "Test University")
        self.assertEqual(exchange.status, "DRAFT")


class DocumentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.exchange = Exchange.objects.create(
            student=self.user,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            current_university="Test University",
            current_program="Computer Science",
            destination_university="Host University",
            destination_country="Germany",
            exchange_program="Semester Exchange",
            start_date=datetime.date(2025, 9, 1),
            end_date=datetime.date(2026, 6, 30),
            status="DRAFT",
            student_number="12345",
        )

    def test_document_creation(self):
        """Test Document model can be created with valid data"""
        # Create a temporary image file
        image = Image.new("RGB", (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        image.save(tmp_file)
        tmp_file.close()

        # Create the document with proper file handling
        try:
            with open(tmp_file.name, 'rb') as f:
                django_file = File(f, name='test_passport.jpg')
                document = Document.objects.create(
                    exchange=self.exchange,
                    category="passport",
                    title="Passport Copy",
                    file=django_file,
                    description="Test passport document",
                )

            self.assertEqual(document.category, "passport")
            self.assertEqual(document.description, "Test passport document")
            self.assertEqual(document.exchange, self.exchange)
        finally:
            # Clean up
            try:
                os.unlink(tmp_file.name)
                if hasattr(document, 'file') and document.file:
                    document.file.delete()
            except:
                pass
