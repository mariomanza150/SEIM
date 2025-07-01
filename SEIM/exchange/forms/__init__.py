"""
Exchange forms module for the SEIM application.

This module provides a clean interface for importing all form classes
while maintaining backward compatibility with existing code.

The forms have been refactored into logical submodules:
- authentication_forms: Login and registration forms
- profile_forms: User profile management forms
- exchange_forms: Exchange application forms
- form_choices: Reusable choice constants
- form_widgets: Bootstrap-styled widget configurations
- form_utils: Utility functions for forms
"""

# Import helper modules for advanced usage
from . import form_choices, form_utils, form_widgets
# Import all form classes for backward compatibility
from .authentication_forms import LoginForm, RegistrationForm
from .exchange_forms import ExchangeForm
from .profiles import BaseProfileForm, ContactProfileForm, StaffProfileForm, StudentProfileForm

# Export all forms for easy importing
__all__ = [
    # Authentication forms
    "LoginForm",
    "RegistrationForm",
    # Profile forms
    "BaseProfileForm",
    "ContactProfileForm",
    "StaffProfileForm",
    "StudentProfileForm",
    # Exchange forms
    "ExchangeForm",
    # Helper modules
    "form_choices",
    "form_widgets",
    "form_utils",
]
