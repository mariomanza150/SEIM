"""
Test data loader utilities for E2E tests.

Provides functions for loading fixtures and managing test data.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

import django
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command

from accounts.models import Role
from exchange.models import Application, ApplicationStatus, Program

User = get_user_model()


def load_fixture_json(filename: str) -> Dict[str, Any]:
    """
    Load fixture data from JSON file.
    
    Args:
        filename: Name of the fixture file
    
    Returns:
        Parsed JSON data
    """
    fixture_path = Path(__file__).parent.parent / 'fixtures' / filename
    if not fixture_path.exists():
        raise FileNotFoundError(f"Fixture file not found: {fixture_path}")
    
    with open(fixture_path, 'r') as f:
        return json.load(f)


def load_users_fixture() -> List[Dict[str, Any]]:
    """Load users from fixture."""
    return load_fixture_json('users.json')


def load_programs_fixture() -> List[Dict[str, Any]]:
    """Load programs from fixture."""
    return load_fixture_json('programs.json')


def load_applications_fixture() -> List[Dict[str, Any]]:
    """Load applications from fixture."""
    return load_fixture_json('applications.json')


def create_test_users(users_data: List[Dict[str, Any]] = None) -> List[User]:
    """
    Create test users from data.
    
    Args:
        users_data: List of user data dictionaries
    
    Returns:
        List of created User objects
    """
    if users_data is None:
        users_data = load_users_fixture()
    
    created_users = []
    for user_data in users_data:
        role_name = user_data.pop('role', 'student')
        role, _ = Role.objects.get_or_create(name=role_name)
        
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        
        if created:
            user.set_password(user_data.get('password', 'password123'))
            user.roles.add(role)
            user.save()
        
        created_users.append(user)
    
    return created_users


def create_test_programs(programs_data: List[Dict[str, Any]] = None) -> List[Program]:
    """
    Create test programs from data.
    
    Args:
        programs_data: List of program data dictionaries
    
    Returns:
        List of created Program objects
    """
    if programs_data is None:
        programs_data = load_programs_fixture()
    
    created_programs = []
    for program_data in programs_data:
        program, created = Program.objects.get_or_create(
            name=program_data['name'],
            defaults=program_data
        )
        created_programs.append(program)
    
    return created_programs


def create_test_applications(applications_data: List[Dict[str, Any]] = None) -> List[Application]:
    """
    Create test applications from data.
    
    Args:
        applications_data: List of application data dictionaries
    
    Returns:
        List of created Application objects
    """
    if applications_data is None:
        applications_data = load_applications_fixture()
    
    created_applications = []
    for app_data in applications_data:
        student = User.objects.get(username=app_data['student_username'])
        program = Program.objects.get(name=app_data['program_name'])
        status = ApplicationStatus.objects.get(name=app_data['status'])
        
        app, created = Application.objects.get_or_create(
            student=student,
            program=program,
            defaults={'status': status}
        )
        created_applications.append(app)
    
    return created_applications


def seed_database(
    load_users: bool = True,
    load_programs: bool = True,
    load_applications: bool = True
) -> Dict[str, List]:
    """
    Seed database with test data.
    
    Args:
        load_users: Whether to load users
        load_programs: Whether to load programs
        load_applications: Whether to load applications
    
    Returns:
        Dictionary with lists of created objects
    """
    result = {
        'users': [],
        'programs': [],
        'applications': []
    }
    
    if load_users:
        result['users'] = create_test_users()
    
    if load_programs:
        result['programs'] = create_test_programs()
    
    if load_applications:
        result['applications'] = create_test_applications()
    
    return result


def cleanup_test_data() -> None:
    """Clean up all test data from database."""
    # Delete test applications
    Application.objects.filter(student__username__startswith='test_').delete()
    
    # Delete test programs
    Program.objects.filter(name__startswith='Test').delete()
    
    # Delete test users
    User.objects.filter(username__startswith='test_').delete()


def reset_database() -> None:
    """Reset database to initial state."""
    cleanup_test_data()
    call_command('flush', '--noinput')
    call_command('migrate')


def create_minimal_test_data() -> Dict[str, Any]:
    """
    Create minimal test data for E2E tests.
    
    Returns:
        Dictionary with created objects
    """
    # Create roles
    student_role, _ = Role.objects.get_or_create(name='student')
    coordinator_role, _ = Role.objects.get_or_create(name='coordinator')
    admin_role, _ = Role.objects.get_or_create(name='admin')
    
    # Create users
    admin = User.objects.create_user(
        username='admin',
        email='admin@seim.edu',
        password='admin123',
        is_staff=True,
        is_superuser=True
    )
    admin.roles.add(admin_role)
    
    coordinator = User.objects.create_user(
        username='coordinator',
        email='coordinator@seim.edu',
        password='coord123'
    )
    coordinator.roles.add(coordinator_role)
    
    student1 = User.objects.create_user(
        username='student1',
        email='student1@university.edu',
        password='student123'
    )
    student1.roles.add(student_role)
    
    student2 = User.objects.create_user(
        username='student2',
        email='student2@university.edu',
        password='student123'
    )
    student2.roles.add(student_role)
    
    # Create application statuses
    statuses = {}
    for i, status_name in enumerate(['draft', 'submitted', 'under_review', 'approved', 'rejected', 'completed', 'cancelled']):
        status, _ = ApplicationStatus.objects.get_or_create(
            name=status_name,
            defaults={'order': i}
        )
        statuses[status_name] = status
    
    # Create programs
    program1 = Program.objects.create(
        name='Test Exchange Program',
        description='A test exchange program',
        is_active=True,
        min_gpa=3.0,
        required_language='English'
    )
    
    return {
        'users': {
            'admin': admin,
            'coordinator': coordinator,
            'student1': student1,
            'student2': student2,
        },
        'roles': {
            'admin': admin_role,
            'coordinator': coordinator_role,
            'student': student_role,
        },
        'statuses': statuses,
        'programs': {
            'program1': program1,
        }
    }


def snapshot_database(snapshot_name: str) -> None:
    """
    Create a snapshot of the current database state.
    
    Args:
        snapshot_name: Name for the snapshot
    """
    snapshot_dir = Path(__file__).parent.parent / 'snapshots'
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    snapshot_file = snapshot_dir / f"{snapshot_name}.json"
    call_command('dumpdata', '--output', str(snapshot_file))


def restore_database(snapshot_name: str) -> None:
    """
    Restore database from a snapshot.
    
    Args:
        snapshot_name: Name of the snapshot to restore
    """
    snapshot_dir = Path(__file__).parent.parent / 'snapshots'
    snapshot_file = snapshot_dir / f"{snapshot_name}.json"
    
    if not snapshot_file.exists():
        raise FileNotFoundError(f"Snapshot not found: {snapshot_file}")
    
    call_command('loaddata', str(snapshot_file))

