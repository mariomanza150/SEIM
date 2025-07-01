"""
Application-related serializers.

This package contains serializers for all application-related models including
exchanges, documents, courses, comments, timelines, and related functionality.
"""

from .exchange import *
from .document import *
from .course import *
from .comment import *
from .timeline import *
from .application_answer import *
from .application_status import *
from .document_type import *

# For backward compatibility with course models that may not have been split
try:
    from .course_category import *
except ImportError:
    pass

__all__ = [
    # Exchange serializers
    "ExchangeSerializer",
    "ExchangeListSerializer", 
    "ExchangeDetailSerializer",
    "ExchangeSubmitSerializer",
    
    # Document serializers
    "DocumentSerializer",
    "DocumentUploadSerializer",
    "DocumentVerificationSerializer",
    "DocumentTypeSerializer",
    
    # Course serializers
    "CourseSerializer",
    "GradeSerializer",
    
    # Comment serializers  
    "CommentSerializer",
    "ReviewSerializer",
    
    # Timeline serializers
    "TimelineSerializer",
    "WorkflowLogSerializer",
    
    # Application answer serializers
    "ApplicationAnswerSerializer",
    
    # Application status serializers
    "ApplicationStatusSerializer",
]
