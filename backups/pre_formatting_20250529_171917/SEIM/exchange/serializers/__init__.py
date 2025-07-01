"""
Exchange application serializers.

This module now redirects to the API v1 serializers for backward compatibility.
All serializers have been moved to exchange.api.v1.serializers.
"""

# Redirect imports to the new API v1 location
from ..api.v1.serializers import *

# Maintain backward compatibility
__all__ = [
    # Document serializers
    "DocumentSerializer",
    "DocumentUploadSerializer",
    "DocumentTypeSerializer",
    # Exchange serializers
    "ExchangeSerializer",
    "ExchangeListSerializer",
    "ExchangeDetailSerializer",
    # User serializers
    "UserSerializer",
    "UserProfileSerializer",
    "RegisterSerializer",
]
