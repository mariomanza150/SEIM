"""
User-related serializers for the exchange application.

This module contains serializers for handling user accounts,
profiles, and authentication-related data.
"""

from django.contrib.auth.models import User
from rest_framework import serializers

from ...models import StudentProfile


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.

    Provides basic user information including name and contact details.
    Username is read-only to prevent unauthorized changes.
    """

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id", "username"]


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.

    Extends user information with institutional details,
    contact information, and verification status.
    Role changes are restricted to administrators only.
    """

    user = UserSerializer(read_only=True)

    class Meta:
        model = StudentProfile
        fields = [
            "user",
            "institution",
            "department",
            "position",
            "role",
            "office_phone",
            "is_verified",
            "verification_date",
            "date_of_birth",
            "phone",
            "gender",
            "street_address",
            "city",
            "country",
        ]
        read_only_fields = ["role", "is_verified", "verification_date"]

    def validate_phone(self, value):
        """
        Validate phone number format.

        Args:
            value: Phone number string

        Returns:
            str: Validated phone number

        Raises:
            ValidationError: If phone number format is invalid
        """
        if (
            value
            and not value.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "").isdigit()
        ):
            raise serializers.ValidationError(
                "Phone number must contain only digits, spaces, hyphens, parentheses, and plus signs"
            )
        return value

    def validate_office_phone(self, value):
        """
        Validate office phone number format.

        Args:
            value: Office phone number string

        Returns:
            str: Validated office phone number

        Raises:
            ValidationError: If office phone number format is invalid
        """
        if (
            value
            and not value.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "").isdigit()
        ):
            raise serializers.ValidationError(
                "Office phone number must contain only digits, spaces, hyphens, parentheses, and plus signs"
            )
        return value
