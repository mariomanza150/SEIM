#!/usr/bin/env python
"""
Quick verification script to test SGII exchange functionality after fixes
"""
import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent / 'SEIM'
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seim.settings')

def test_imports():
    """Test that all imports work correctly"""
    print("Testing imports...")
    try:
        # Initialize Django
        django.setup()
        
        # Test model import
        from exchange.models import Exchange, UserProfile, WorkflowLog
        print("✅ Models imported successfully")
        
        # Test form import
        from exchange.forms import ExchangeForm
        print("✅ Forms imported successfully")
        
        # Test service import
        from exchange.services.workflow import WorkflowService
        print("✅ Services imported successfully")
        
        # Test view import
        from exchange.views.exchange_views import create_exchange, exchange_detail
        from exchange.views.workflow_views import approve_exchange, reject_exchange
        print("✅ Views imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_form_validation():
    """Test form validation"""
    print("\nTesting form validation...")
    try:
        from exchange.forms import ExchangeForm
        from django.contrib.auth.models import User
        
        # Create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        
        # Test form with missing data
        form = ExchangeForm(data={}, user=user)
        if not form.is_valid():
            print("✅ Form correctly rejects invalid data")
        else:
            print("❌ Form should reject invalid data")
            return False
        
        # Test form with valid data
        valid_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'student_number': 'TEST123',
            'current_university': 'Test University',
            'current_program': 'Test Program',
            'destination_university': 'Partner University',
            'destination_country': 'USA',
            'exchange_program': 'Test Exchange',
            'start_date': '2024-09-01',
            'end_date': '2024-12-31',
            'motivation_letter': 'This is a test motivation letter. ' * 20,
        }
        
        form = ExchangeForm(data=valid_data, user=user)
        if form.is_valid():
            print("✅ Form correctly accepts valid data")
        else:
            print(f"❌ Form should accept valid data. Errors: {form.errors}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Form validation test error: {e}")
        return False

def test_model_creation():
    """Test exchange model creation"""
    print("\nTesting model creation...")
    try:
        from exchange.models import Exchange
        from django.contrib.auth.models import User
        from datetime import date, timedelta
        
        # Get or create test user
        user, created = User.objects.get_or_create(
            username='modeltest',
            defaults={'email': 'modeltest@example.com'}
        )
        
        # Create exchange
        exchange = Exchange.objects.create(
            student=user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            student_number='TEST456',
            current_university='Test University',
            current_program='Test Program',
            destination_university='Partner University',
            destination_country='USA',
            exchange_program='Test Exchange',
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=180),
            motivation_letter='Test motivation letter',
            status='DRAFT'
        )
        
        print(f"✅ Exchange created successfully with ID: {exchange.id}")
        
        # Test status transitions
        if exchange.can_transition_to('SUBMITTED'):
            print("✅ Status transition validation working")
        else:
            print("❌ Status transition validation failed")
            return False
        
        # Clean up
        exchange.delete()
        if created:
            user.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ Model creation test error: {e}")
        return False

def test_workflow_service():
    """Test workflow service"""
    print("\nTesting workflow service...")
    try:
        from exchange.services.workflow import WorkflowService
        from exchange.models import Exchange
        from django.contrib.auth.models import User
        from datetime import date, timedelta
        
        # Get or create test user
        user, created = User.objects.get_or_create(
            username='workflowtest',
            defaults={'email': 'workflowtest@example.com'}
        )
        
        # Create test exchange
        exchange = Exchange.objects.create(
            student=user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            student_number='TEST789',
            current_university='Test University',
            current_program='Test Program',
            destination_university='Partner University',
            destination_country='USA',
            exchange_program='Test Exchange',
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=180),
            motivation_letter='Test motivation letter. ' * 20,
            status='DRAFT'
        )
        
        # Test can_submit validation
        can_submit, reason = WorkflowService.can_submit(exchange)
        if can_submit:
            print("✅ Workflow validation working correctly")
        else:
            print(f"❌ Workflow validation failed: {reason}")
            return False
        
        # Test transition
        success, message = WorkflowService.transition(
            exchange=exchange,
            new_status='SUBMITTED',
            user=user,
            comment='Test transition'
        )
        
        if success:
            print("✅ Workflow transition successful")
        else:
            print(f"❌ Workflow transition failed: {message}")
            return False
        
        # Clean up
        exchange.delete()
        if created:
            user.delete()
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow service test error: {e}")
        return False

def main():
    """Main verification function"""
    print("🔍 SGII Exchange Application Verification")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Run tests
    tests = [
        test_imports,
        test_form_validation,
        test_model_creation,
        test_workflow_service,
    ]
    
    for test in tests:
        if not test():
            all_tests_passed = False
            print("❌ Test failed, stopping verification")
            break
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED!")
        print("The exchange application fixes have been successfully applied.")
        print("\nNext steps:")
        print("1. Start the Django development server")
        print("2. Test the application manually through the web interface")
        print("3. Create a test exchange application as a student")
        print("4. Test approval/rejection workflow as a coordinator")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please review the error messages above and fix any issues.")
        print("You may need to:")
        print("1. Check that all files were copied correctly")
        print("2. Run database migrations")
        print("3. Check for any import or syntax errors")
    
    return all_tests_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
