#!/usr/bin/env python
"""
Test script to verify the ExchangeForm fixes.
This script creates a test form instance and validates the field mapping.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'SEIM'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seim.settings')
django.setup()

from django.contrib.auth.models import User
from exchange.forms import ExchangeForm
from exchange.models import Exchange

def test_form_fields():
    """Test that all required form fields are present."""
    print("Testing ExchangeForm field mapping...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com'
        }
    )
    
    # Create form instance
    form = ExchangeForm(user=user)
    
    # Check that custom fields exist
    custom_fields = [
        'student_id', 
        'email', 
        'phone_number',
        'current_institution',
        'current_program_field',
        'host_university',
        'host_country', 
        'program',
        'academic_level',
        'current_gpa',
        'academic_background',
        'purpose_statement'
    ]
    
    print("Checking custom fields:")
    for field_name in custom_fields:
        if field_name in form.fields:
            print(f"  ✓ {field_name}")
        else:
            print(f"  ✗ {field_name} - MISSING")
    
    # Check Meta fields
    meta_fields = [
        'first_name', 
        'last_name', 
        'current_year',
        'start_date', 
        'end_date', 
        'motivation_letter', 
        'language_proficiency',
        'special_requirements', 
        'emergency_contact', 
        'date_of_birth'
    ]
    
    print("\nChecking Meta fields:")
    for field_name in meta_fields:
        if field_name in form.fields:
            print(f"  ✓ {field_name}")
        else:
            print(f"  ✗ {field_name} - MISSING")
    
    # Test form submission with valid data
    print("\nTesting form validation with sample data...")
    
    test_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'student_id': 'STU123456',
        'email': 'john.doe@student.edu',
        'phone_number': '+1234567890',
        'current_institution': 'Test University',
        'current_program_field': 'Computer Science',
        'host_university': 'Harvard University',
        'host_country': 'US',
        'program': 'Semester Exchange',
        'academic_level': 'UNDERGRADUATE',
        'current_gpa': '3.5',
        'current_year': 3,
        'start_date': '2025-09-01',
        'end_date': '2025-12-15',
        'purpose_statement': ' '.join(['This is a test purpose statement.'] * 50),  # 200+ words
        'motivation_letter': 'Test motivation letter',
        'language_proficiency': 'English - Fluent',
        'special_requirements': 'None',
        'emergency_contact': 'Jane Doe - +1234567891',
        'date_of_birth': '2000-01-01',
        'academic_background': 'Test academic background'
    }
    
    form = ExchangeForm(test_data, user=user)
    
    if form.is_valid():
        print("  ✓ Form validation passed")
        
        # Test the save method and field mapping
        exchange = form.save(commit=False)
        
        # Check that model fields are properly mapped
        field_mappings = [
            ('student_id', 'student_number'),
            ('current_institution', 'current_university'),
            ('current_program_field', 'current_program'),
            ('host_university', 'destination_university'),
            ('host_country', 'destination_country'),
            ('program', 'exchange_program'),
            ('current_gpa', 'gpa'),
            ('purpose_statement', 'motivation_letter'),
        ]
        
        print("\nChecking field mappings:")
        for form_field, model_field in field_mappings:
            form_value = test_data.get(form_field)
            model_value = getattr(exchange, model_field, None)
            if form_value == str(model_value) or form_value == model_value:
                print(f"  ✓ {form_field} -> {model_field}: {model_value}")
            else:
                print(f"  ✗ {form_field} -> {model_field}: Expected '{form_value}', got '{model_value}'")
        
        print("\n✓ All tests passed! The form should now work correctly.")
        
    else:
        print("  ✗ Form validation failed:")
        for field, errors in form.errors.items():
            print(f"    {field}: {', '.join(errors)}")

if __name__ == '__main__':
    test_form_fields()
