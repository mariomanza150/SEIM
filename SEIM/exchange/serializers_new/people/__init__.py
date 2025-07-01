"""
People serializers for the exchange application.

This package contains serializers for all user profile models.
"""

from .base_profile import *
from .student_profile import *
from .staff_profile import *
from .contact_profile import *

__all__ = [
    # Profile serializers
    "BaseProfileSerializer",
    "StudentProfileSerializer",
    "StudentProfileListSerializer",
    "StudentProfileCreateSerializer",
    "StaffProfileSerializer",
    "StaffProfileListSerializer",
    "StaffProfileCreateSerializer",
    "ContactProfileSerializer",
    "ContactProfileListSerializer",
    "ContactProfileCreateSerializer",
]
