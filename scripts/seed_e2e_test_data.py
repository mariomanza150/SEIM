#!/usr/bin/env python
"""
Seed test data for E2E tests.

This script creates test users and basic data needed for E2E testing.
Run this before executing E2E tests.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seim.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Role, Profile
from exchange.models import Program, ApplicationStatus

User = get_user_model()


def create_test_users():
    """Create test users for E2E testing."""
    print("Creating test users...")
    
    # Create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
            'is_email_verified': True,
        }
    )
    if created:
        admin_user.set_password('admin123')
    else:
        # Update existing user to ensure email is verified
        admin_user.is_active = True
        admin_user.is_email_verified = True
    admin_user.save()
    if created:
        print(f"✅ Created admin user: {admin_user.username}")
    else:
        print(f"ℹ️  Admin user already exists: {admin_user.username} (updated)")
    
    # Create coordinator user
    coordinator_user, created = User.objects.get_or_create(
        username='coordinator',
        defaults={
            'email': 'coordinator@example.com',
            'is_active': True,
            'is_email_verified': True,
        }
    )
    if created:
        coordinator_user.set_password('coord123')
    else:
        coordinator_user.is_active = True
        coordinator_user.is_email_verified = True
    coordinator_user.save()
    # Assign coordinator role
    try:
        coordinator_role = Role.objects.get(name='coordinator')
        coordinator_user.roles.add(coordinator_role)
        if created:
            print(f"✅ Created coordinator user: {coordinator_user.username}")
        else:
            print(f"ℹ️  Coordinator user already exists: {coordinator_user.username} (updated)")
    except Role.DoesNotExist:
        print(f"⚠️  Coordinator role not found, user created without role")
    
    # Create student user
    student_user, created = User.objects.get_or_create(
        username='student1',
        defaults={
            'email': 'student1@example.com',
            'is_active': True,
            'is_email_verified': True,
        }
    )
    if created:
        student_user.set_password('student123')
    else:
        student_user.is_active = True
        student_user.is_email_verified = True
    student_user.save()
    # Assign student role
    try:
        student_role = Role.objects.get(name='student')
        student_user.roles.add(student_role)
        if created:
            print(f"✅ Created student user: {student_user.username}")
        else:
            print(f"ℹ️  Student user already exists: {student_user.username} (updated)")
    except Role.DoesNotExist:
        print(f"⚠️  Student role not found, user created without role")
    
    # Create additional test student
    student2_user, created = User.objects.get_or_create(
        username='student2',
        defaults={
            'email': 'student2@example.com',
            'is_active': True,
            'is_email_verified': True,
        }
    )
    if created:
        student2_user.set_password('student123')
    else:
        student2_user.is_active = True
        student2_user.is_email_verified = True
    student2_user.save()
    try:
        student_role = Role.objects.get(name='student')
        student2_user.roles.add(student_role)
        if created:
            print(f"✅ Created student2 user: {student2_user.username}")
        else:
            print(f"ℹ️  Student2 user already exists: {student2_user.username} (updated)")
    except Role.DoesNotExist:
        print(f"⚠️  Student role not found, user created without role")
    
    return {
        'admin': admin_user,
        'coordinator': coordinator_user,
        'student1': student_user,
        'student2': student2_user,
    }


def create_test_programs():
    """Create test programs for E2E testing."""
    print("\nCreating test programs...")
    
    programs = []
    
    # Create sample program 1
    program1, created = Program.objects.get_or_create(
        name='Erasmus+ University of Barcelona',
        defaults={
            'description': 'Exchange program with University of Barcelona. Experience Spanish culture while studying.',
            'min_gpa': 3.0,
            'required_language': 'Spanish B2',
            'is_active': True,
        }
    )
    if created:
        print(f"✅ Created program: {program1.name}")
    else:
        print(f"ℹ️  Program already exists: {program1.name}")
    programs.append(program1)
    
    # Create sample program 2
    program2, created = Program.objects.get_or_create(
        name='Study Abroad - Tokyo University',
        defaults={
            'description': 'Semester exchange program at Tokyo University. Immerse yourself in Japanese culture.',
            'min_gpa': 3.5,
            'required_language': 'Japanese N3',
            'is_active': True,
        }
    )
    if created:
        print(f"✅ Created program: {program2.name}")
    else:
        print(f"ℹ️  Program already exists: {program2.name}")
    programs.append(program2)
    
    return programs


def main():
    """Main function to seed all test data."""
    print("=" * 60)
    print("Seeding E2E Test Data")
    print("=" * 60)
    
    try:
        users = create_test_users()
        programs = create_test_programs()
        
        print("\n" + "=" * 60)
        print("✅ Test data seeding completed successfully!")
        print("=" * 60)
        print("\nTest Users Created:")
        for role, user in users.items():
            print(f"  - {role}: {user.username} ({user.email})")
        print(f"\nTest Programs Created: {len(programs)}")
        for program in programs:
            print(f"  - {program.name}")
        print("\nYou can now run E2E tests!")
        
    except Exception as e:
        print(f"\n❌ Error seeding test data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

