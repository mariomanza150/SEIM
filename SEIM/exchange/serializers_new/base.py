"""
Base serializers for the exchange application.

Provides common serializer functionality and base classes used throughout the application.
"""

from rest_framework import serializers
from django.contrib.auth.models import User


class BaseSerializer(serializers.ModelSerializer):
    """
    Base serializer with common functionality for all model serializers.
    """
    
    class Meta:
        abstract = True
    
    def to_representation(self, instance):
        """
        Customize serialization output.
        """
        representation = super().to_representation(instance)
        
        # Remove null values from output if desired
        if getattr(self.Meta, 'remove_null_fields', False):
            representation = {
                key: value for key, value in representation.items()
                if value is not None
            }
        
        return representation


class TimestampedModelSerializer(BaseSerializer):
    """
    Base serializer for models that inherit from TimestampedModel.
    """
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        abstract = True


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for Django User model.
    """
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']
    
    def get_full_name(self, obj):
        """Get user's full name."""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username
