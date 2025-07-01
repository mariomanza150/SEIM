#!/usr/bin/env python3
"""
Test script to verify that the forms refactor maintains backward compatibility.

This script tests that all the original form imports still work after refactoring.
Run this from the SEIM directory with Django properly configured.
"""

import os
import sys
import django

# Add the SEIM directory to Python path
sys.path.insert(0, os.path.abspath('.'))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seim.custom_settings.dev')
django.setup()

def test_forms_imports():
    """Test that all form imports work correctly after refactor."""
    print("Testing forms imports after refactor...")
    
    try:
        # Test backward compatible imports
        from exchange.forms import LoginForm
        print("✅ LoginForm import successful")
        
        from exchange.forms import RegistrationForm  
        print("✅ RegistrationForm import successful")
        
        from exchange.forms import UserProfileForm
        print("✅ UserProfileForm import successful")
        
        from exchange.forms import ExchangeForm
        print("✅ ExchangeForm import successful")
        
        # Test helper module imports
        from exchange.forms import form_choices
        print("✅ form_choices import successful")
        
        from exchange.forms import form_widgets
        print("✅ form_widgets import successful")
        
        from exchange.forms import form_utils
        print("✅ form_utils import successful")
        
        # Test that helper modules have expected content
        assert hasattr(form_choices, 'ACADEMIC_LEVEL_CHOICES')
        assert hasattr(form_widgets, 'BootstrapWidgets')
        assert hasattr(form_utils, 'update_if_not_empty')
        print("✅ Helper modules have expected attributes")
        
        # Test that forms can be instantiated
        login_form = LoginForm()
        reg_form = RegistrationForm()
        profile_form = UserProfileForm()
        exchange_form = ExchangeForm()
        print("✅ All forms can be instantiated")
        
        print("\n🎉 All tests passed! Forms refactor successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_forms_imports()
