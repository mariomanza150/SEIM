"""
Exchange application serializers.

This module provides comprehensive serializers for all models in the exchange application,
organized to mirror the models structure for easy maintenance and development.
"""

# Import all serializers from submodules
from .base import *
from .bulk_action import *
from .notification import *

# Applications
from .applications import *

# Enums  
from .enums import *

# People
from .people import *

# Define what's available when importing from this module
__all__ = [
    # Base serializers
    "BaseSerializer",
    "TimestampedModelSerializer",
    
    # Bulk action serializers
    "BulkActionSerializer",
    "BulkActionItemSerializer", 
    "BulkActionLogSerializer",
    
    # Notification serializers
    "NotificationSerializer",
    
    # Application serializers
    "ExchangeSerializer",
    "ExchangeListSerializer",
    "ExchangeDetailSerializer",
    "ExchangeSubmitSerializer",
    "DocumentSerializer",
    "DocumentUploadSerializer",
    "DocumentVerificationSerializer",
    "DocumentTypeSerializer",
    "CourseSerializer",
    "GradeSerializer",
    "CommentSerializer",
    "ReviewSerializer",
    "TimelineSerializer",
    "WorkflowLogSerializer",
    "ApplicationAnswerSerializer",
    "ApplicationStatusSerializer",
    "CourseCategorySerializer",
    
    # Enum serializers
    "ExchangeProgramSerializer",
    "ExchangeProgramListSerializer",
    "ExchangeProgramDetailSerializer",
    "UniversitySerializer",
    "CampusSerializer",
    "InstitutionSerializer",
    "QuestionSerializer",
    "QuestionCategorySerializer",
    "ConfigModelSerializer",
    "AcademicTermSerializer",
    "DegreeSerializer",
    "LanguageSerializer",
    "FundingTypeSerializer",
    "PartnerAgreementSerializer",
    "ProgramRequirementsSerializer",
    "ProgramTypeSerializer",
    "CountrySerializer",
    "StateSerializer",
    "CitySerializer",
    
    # People serializers
    "UserSerializer",
    "BaseProfileSerializer",
    "StudentProfileSerializer",
    "StaffProfileSerializer",
    "ContactProfileSerializer",
]
