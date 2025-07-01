"""Unit tests for API serializers."""

import unittest

from django.contrib.auth.models import User
from django.test import TestCase

from ..api.v1.serializers import DocumentSerializer, ExchangeSerializer, UserSerializer


class ExchangeSerializerTest(TestCase):
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


class DocumentSerializerTest(TestCase):
    """Test cases for Document serializer."""

    def test_file_serialization(self):
        """Test file field serialization."""
        # TODO: Implement test
        pass

    def test_validation(self):
        """Test document validation."""
        # TODO: Implement test
        pass


class UserSerializerTest(TestCase):
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
