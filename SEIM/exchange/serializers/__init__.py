"""
Exchange application serializers.

This module now redirects to the API v1 serializers for backward compatibility.
All serializers have been moved to exchange.api.v1.serializers.
"""

# Redirect imports to the new API v1 location
from .people import UserSerializer, StudentProfileSerializer, StaffProfileSerializer, ContactProfileSerializer
from .enums import CitySerializer, StateSerializer, CampusSerializer, CountrySerializer, QuestionSerializer, UniversitySerializer
from .applications import CommentSerializer, DocumentSerializer, ExchangeSerializer, TimelineSerializer, DocumentTypeSerializer, ApplicationStatusSerializer, ApplicationAnswerSerializer


# Maintain backward compatibility
__all__ = [
    "CitySerializer",
    "StateSerializer",
    "CampusSerializer",
    "CountrySerializer",
    "QuestionSerializer",
    "UniversitySerializer",
    # Document serializers
    "DocumentSerializer",
    "DocumentTypeSerializer",
    # Exchange serializers
    "ExchangeSerializer",
    "CommentSerializer",
    "TimelineSerializer",
    # User serializers
    "UserSerializer",
    "StudentProfileSerializer",
    "StaffProfileSerializer",
    "ContactProfileSerializer",
    # Application
    "ApplicationAnswerSerializer",
    "ApplicationStatusSerializer"
]
