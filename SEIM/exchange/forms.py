"""
Legacy forms module for backward compatibility.

This module maintains backward compatibility by importing all forms
from the new modular forms/ package structure.

All forms are now organized in:
- forms/authentication_forms.py
- forms/profile_forms.py
- forms/exchange_forms.py
- forms/form_choices.py
- forms/form_widgets.py
- forms/form_utils.py

This file ensures that existing imports continue to work:
    from exchange.forms import LoginForm, RegistrationForm, UserProfileForm, ExchangeForm
"""

# Make helper modules available
# Explicit imports for clarity and IDE support
# Import all forms from the new modular structure
from .forms import *
from .forms import ExchangeForm, LoginForm, RegistrationForm, UserProfileForm, form_choices, form_utils, form_widgets
