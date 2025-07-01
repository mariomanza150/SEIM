"""API v1 serializers for exchange application."""

# Import all serializers for easy access
from .document_serializers import *
from .exchange_serializers import *
from .user_serializers import *
from rest_framework import serializers
from SEIM.exchange.models.applications.course import Course
from SEIM.exchange.models.applications.comment import Comment
from SEIM.exchange.models.applications.timeline import Timeline

# Define what's available when importing from this module
__all__ = [
    # From exchange_serializers
    "ExchangeSerializer",
    #'ExchangeListSerializer',
    #'ExchangeDetailSerializer',
    "ExchangeSubmitSerializer",
    # From document_serializers
    "DocumentSerializer",
    #'DocumentUploadSerializer',
    "DocumentVerificationSerializer",
    #'DocumentTypeSerializer',
    # From user_serializers
    "UserSerializer",
    "UserProfileSerializer",
    #'RegisterSerializer',
    'CourseSerializer',
    'CommentSerializer',
    'TimelineSerializer',
]

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class TimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeline
        fields = '__all__'
