"""
Base Profile serializers for the exchange application.

Handles serialization for the base profile functionality.
"""

from rest_framework import serializers
from ....models import BaseProfile
from ...base import TimestampedModelSerializer, UserSerializer


class BaseProfileSerializer(TimestampedModelSerializer):
    """
    Serializer for BaseProfile model (abstract base).
    """
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = BaseProfile
        fields = '__all__'
        abstract = True


class BaseProfileCreateSerializer(serializers.ModelSerializer):
    """
    Base serializer for creating profiles.
    """
    
    class Meta:
        model = BaseProfile
        fields = ['is_verified', 'verification_date']
        abstract = True
    
    def create(self, validated_data):
        """Create profile with user from context."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BaseProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Base serializer for updating profiles.
    """
    
    class Meta:
        model = BaseProfile
        fields = ['is_verified', 'verification_date']
        read_only_fields = ['user', 'created_at', 'updated_at']
        abstract = True
