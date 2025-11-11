#!/usr/bin/env python
"""
Test Frontend Issues

This script tests the frontend issues reported by the user.
"""

import django
import os
import sys

# Setup Django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seim.settings.development')
django.setup()

from django.test import Client
from accounts.models import User, Role
from exchange.models import Program

def test_admin_user_roles():
    """Test admin user roles and permissions."""
    print("\n" + "="*60)
    print("ADMIN USER ROLES CHECK")
    print("="*60)
    
    admin = User.objects.filter(username='admin1').first()
    
    if admin:
        print(f"✓ Admin user found: {admin.username}")
        print(f"  Email: {admin.email}")
        print(f"  First name: {admin.first_name}")
        print(f"  Last name: {admin.last_name}")
        print(f"  Full name: {admin.get_full_name()}")
        print(f"  Has admin role: {admin.has_role('admin')}")
        print(f"  Roles: {list(admin.roles.values_list('name', flat=True))}")
        print(f"  Is superuser: {admin.is_superuser}")
        print(f"  Is staff: {admin.is_staff}")
    else:
        print("✗ No admin1 user found")

def test_program_creation():
    """Test program creation via form."""
    print("\n" + "="*60)
    print("PROGRAM CREATION TEST")
    print("="*60)
    
    client = Client()
    
    # Get admin user
    admin = User.objects.filter(username='admin1').first()
    
    if not admin:
        print("✗ Cannot test - no admin user")
        return
    
    # Login
    client.force_login(admin)
    
    # Access program create page
    response = client.get('/programs/create/')
    print(f"  GET /programs/create/ : HTTP {response.status_code}")
    
    if response.status_code == 200:
        print("  ✓ Page accessible")
    elif response.status_code == 403:
        print("  ✗ Access forbidden - permission issue")
    elif response.status_code == 404:
        print("  ✗ Page not found - routing issue")
    
    # Try to create a program
    from datetime import date, timedelta
    
    data = {
        'name': 'Test Program via Form',
        'description': 'Test description',
        'start_date': date.today().isoformat(),
        'end_date': (date.today() + timedelta(days=365)).isoformat(),
        'is_active': True,
        'min_gpa': 3.0,
        'required_language': 'English',
        'recurring': False,
    }
    
    response = client.post('/programs/create/', data)
    print(f"  POST /programs/create/ : HTTP {response.status_code}")
    
    if response.status_code == 302:
        print("  ✓ Program created successfully (redirect)")
        # Check if program exists
        if Program.objects.filter(name='Test Program via Form').exists():
            print("  ✓ Program found in database")
        else:
            print("  ✗ Program not found in database")
    elif response.status_code == 200:
        print("  ✗ Form validation failed - check errors")
        # Try to extract errors
        if hasattr(response, 'context') and 'form' in response.context:
            form_errors = response.context['form'].errors
            if form_errors:
                print(f"  Form errors: {form_errors}")
    else:
        print(f"  ✗ Unexpected status code: {response.status_code}")

def test_user_profile_endpoint():
    """Test user profile API endpoint."""
    print("\n" + "="*60)
    print("USER PROFILE API TEST")
    print("="*60)
    
    from rest_framework.test import APIClient
    from rest_framework_simplejwt.tokens import RefreshToken
    
    admin = User.objects.filter(username='admin1').first()
    
    if not admin:
        print("✗ No admin user")
        return
    
    # Get JWT token
    refresh = RefreshToken.for_user(admin)
    access_token = str(refresh.access_token)
    
    # Test API
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    response = client.get('/api/accounts/profile/')
    print(f"  GET /api/accounts/profile/ : HTTP {response.status_code}")
    
    if response.status_code == 200:
        print("  ✓ Profile endpoint working")
        data = response.json()
        print(f"  Username from API: {data.get('username')}")
        print(f"  First name from API: {data.get('first_name')}")
        print(f"  Last name from API: {data.get('last_name')}")
    else:
        print(f"  ✗ Profile endpoint failed: {response.status_code}")

if __name__ == '__main__':
    test_admin_user_roles()
    test_program_creation()
    test_user_profile_endpoint()
    
    print("\n" + "="*60)
    print("FRONTEND ISSUE TESTING COMPLETE")
    print("="*60 + "\n")

