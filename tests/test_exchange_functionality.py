#!/usr/bin/env python
"""
Comprehensive test script for exchange creation functionality.
This script validates all components needed for exchange creation.
"""
import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent / 'SEIM'
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seim.settings')

def test_django_setup():
    """Test Django setup and imports"""
    print("=== Testing Django Setup ===")
    try:
        django.setup()
        print("✅ Django setup successful")
        return True
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False


def test_model_imports():
    """Test model imports"""
    print("\n=== Testing Model Imports ===")
    try:
        from exchange.models import Exchange, WorkflowLog, Document
        from django.contrib.auth.models import User
        print("✅ Exchange model imported")
        print("✅ WorkflowLog model imported")
        print("✅ Document model imported")
        print("✅ User model imported")
        return True
    except Exception as e:
        print(f"❌ Model import failed: {e}")
        return False


def test_form_imports():
    """Test form imports"""
    print("\n=== Testing Form Imports ===")
    try:
        from exchange.forms import ExchangeForm, LoginForm, RegistrationForm, UserProfileForm
        print("✅ ExchangeForm imported")
        print("✅ LoginForm imported")
        print("✅ RegistrationForm imported")
        print("✅ UserProfileForm imported")
        return True
    except Exception as e:
        print(f"❌ Form import failed: {e}")
        return False


def test_service_imports():
    """Test service imports"""
    print("\n=== Testing Service Imports ===")
    try:
        from exchange.services.workflow import WorkflowService
        print("✅ WorkflowService imported")
        
        # Test service methods
        required_methods = ['transition', 'get_available_transitions', 'get_workflow_history', 'can_submit']
        for method in required_methods:
            if hasattr(WorkflowService, method):
                print(f"✅ WorkflowService.{method} method found")
            else:
                print(f"❌ WorkflowService.{method} method missing")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Service import failed: {e}")
        return False


def test_form_instantiation():
    """Test form instantiation"""
    print("\n=== Testing Form Instantiation ===")
    try:
        from exchange.forms import ExchangeForm
        from django.contrib.auth.models import User
        
        # Create a test user
        user = User(username='testuser', email='test@example.com', first_name='Test', last_name='User')
        
        # Test form instantiation
        form = ExchangeForm(user=user)
        print("✅ ExchangeForm instantiation successful")
        print(f"✅ Form has {len(form.fields)} fields")
        
        # Check for required custom fields
        required_custom_fields = [
            'student_id', 'contact_email', 'phone_number', 'host_university',
            'host_country', 'program', 'academic_level', 'current_gpa',
            'current_institution', 'academic_background', 'purpose_statement'
        ]
        
        missing_fields = []
        for field in required_custom_fields:
            if field in form.fields:
                print(f"✅ Custom field '{field}' found")
            else:
                missing_fields.append(field)
                print(f"❌ Custom field '{field}' missing")
        
        if missing_fields:
            print(f"❌ Missing custom fields: {missing_fields}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Form instantiation failed: {e}")
        return False


def test_form_validation():
    """Test form validation with sample data"""
    print("\n=== Testing Form Validation ===")
    try:
        from exchange.forms import ExchangeForm
        from django.contrib.auth.models import User
        
        # Create a test user
        user = User(username='testuser', email='test@example.com', first_name='Test', last_name='User')
        
        # Test data
        test_data = {
            # Model fields
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '123-456-7890',
            'date_of_birth': '1990-01-15',
            'student_number': 'STU123456',
            'current_university': 'Test University',
            'current_program': 'Computer Science', 
            'current_year': '3',
            'gpa': '3.5',
            'destination_university': 'Partner University',
            'destination_country': 'USA',
            'exchange_program': 'Exchange Program',
            'start_date': '2024-09-01',
            'end_date': '2024-12-31',
            'motivation_letter': 'Test motivation letter with more than 200 words. ' * 10,
            'language_proficiency': 'English - Fluent',
            'special_requirements': 'None',
            'emergency_contact': 'Emergency Contact Info',
            
            # Custom form fields
            'student_id': 'STU123456',
            'contact_email': 'john.doe@example.com',
            'phone_number': '123-456-7890',
            'host_university': 'Partner University',
            'host_country': 'USA',
            'program': 'Computer Science',
            'academic_level': 'UNDERGRADUATE',
            'current_gpa': '3.5',
            'current_institution': 'Test University',
            'academic_background': 'Computer Science student with strong academic performance.',
            'purpose_statement': 'This is my purpose statement for the exchange program. I am highly motivated to participate in this exchange program because it will provide me with invaluable international experience and exposure to different teaching methodologies. Through this program, I hope to broaden my academic horizons, develop cross-cultural communication skills, and gain a global perspective that will enhance my future career prospects. I believe this exchange will be transformative for my personal and professional development, allowing me to contribute meaningfully to both my host institution and my home university upon my return. The opportunity to study in a different educational system will challenge me to adapt and grow, preparing me for an increasingly interconnected world.',
        }
        
        form = ExchangeForm(data=test_data, user=user)
        
        if form.is_valid():
            print("✅ Form validation passed with test data")
            
            # Test save method (without committing)
            exchange = form.save(commit=False)
            print("✅ Form save method successful")
            
            # Check field mapping
            print(f"✅ student_number mapped: {exchange.student_number}")
            print(f"✅ email mapped: {exchange.email}")
            print(f"✅ destination_university mapped: {exchange.destination_university}")
            print(f"✅ destination_country mapped: {exchange.destination_country}")
            print(f"✅ exchange_program mapped: {exchange.exchange_program}")
            print(f"✅ gpa mapped: {exchange.gpa}")
            print(f"✅ motivation_letter mapped: {exchange.motivation_letter[:50]}...")
            
            return True
        else:
            print("❌ Form validation failed:")
            for field, errors in form.errors.items():
                print(f"  - {field}: {errors}")
            return False
            
    except Exception as e:
        print(f"❌ Form validation test failed: {e}")
        return False


def test_view_imports():
    """Test view imports"""
    print("\n=== Testing View Imports ===")
    try:
        from exchange.views import create_exchange, edit_exchange, exchange_detail, exchange_list
        print("✅ create_exchange view imported")
        print("✅ edit_exchange view imported")
        print("✅ exchange_detail view imported")
        print("✅ exchange_list view imported")
        return True
    except Exception as e:
        print(f"❌ View import failed: {e}")
        return False


def test_url_patterns():
    """Test URL patterns"""
    print("\n=== Testing URL Patterns ===")
    try:
        from exchange.urls import urlpatterns
        print("✅ URL patterns imported")
        
        # Check for key URL patterns
        key_patterns = ['create-exchange', 'edit-exchange', 'exchange-detail', 'exchange-list']
        
        pattern_names = []
        for pattern in urlpatterns:
            if hasattr(pattern, 'name') and pattern.name:
                pattern_names.append(pattern.name)
        
        missing_patterns = []
        for pattern in key_patterns:
            if pattern in pattern_names:
                print(f"✅ URL pattern '{pattern}' found")
            else:
                missing_patterns.append(pattern)
                print(f"❌ URL pattern '{pattern}' missing")
        
        if missing_patterns:
            return False
        
        return True
    except Exception as e:
        print(f"❌ URL pattern test failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Exchange Creation Functionality Tests\n")
    
    tests = [
        test_django_setup,
        test_model_imports,
        test_form_imports,
        test_service_imports,
        test_form_instantiation,
        test_form_validation,
        test_view_imports,
        test_url_patterns,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"\n⚠️  Test '{test.__name__}' failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Exchange creation functionality is ready!")
        print("\n📋 Next Steps:")
        print("1. Run Django migrations: python manage.py migrate")
        print("2. Create a superuser: python manage.py createsuperuser")
        print("3. Start the development server: python manage.py runserver")
        print("4. Navigate to /exchanges/create/ to test exchange creation")
        return True
    else:
        print(f"\n❌ {total - passed} tests failed. Please fix the issues before proceeding.")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
