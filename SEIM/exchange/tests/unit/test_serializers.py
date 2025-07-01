"""Unit tests for API serializers."""

import unittest
import pytest
from django.contrib.auth import get_user_model
from django.apps import apps
from SEIM.exchange.api.v1.exchange_serializers import ExchangeSerializer

Exchange = apps.get_model('exchange', 'Exchange')
User = get_user_model()


class ExchangeSerializerTest(unittest.TestCase):
    """Test cases for Exchange serializer."""

    def test_serialization(self):
        """Test serializing exchange data."""
        # TODO: Implement test
        pass

    def test_deserialization(self):
        """Test deserializing exchange data."""
        # TODO: Implement test
        pass

    def test_validation(self):
        """Test serializer validation."""
        # TODO: Implement test
        pass

    @pytest.mark.django_db
    def test_exchange_serializer_valid(self):
        """Test ExchangeSerializer with valid data."""
        user = User.objects.create_user(username='student', password='pass')
        exchange = Exchange.objects.create(student=user)
        data = dict(ExchangeSerializer(exchange).data)
        assert data['student'] == user.id or data['student'] == user.pk
        assert data['status'] == 'DRAFT'

    @pytest.mark.django_db
    def test_exchange_serializer_invalid(self):
        """Test ExchangeSerializer with invalid data."""
        # Missing required student field
        serializer = ExchangeSerializer(data={})
        assert not serializer.is_valid()
        assert 'student' in serializer.errors


class DocumentSerializerTest(unittest.TestCase):
    """Test cases for Document serializer."""

    def test_file_serialization(self):
        """Test file field serialization."""
        # TODO: Implement test
        pass

    def test_validation(self):
        """Test document validation."""
        # TODO: Implement test
        pass


class UserSerializerTest(unittest.TestCase):
    """Test cases for User serializer."""

    def test_password_handling(self):
        """Test password is not serialized."""
        # TODO: Implement test
        pass

    def test_user_creation(self):
        """Test creating user through serializer."""
        # TODO: Implement test
        pass


# TODO: Add more serializer tests
