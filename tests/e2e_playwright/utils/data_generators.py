"""
Test data generation utilities for E2E tests.

Provides functions to generate realistic test data.
"""

import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any


def generate_random_string(length: int = 10) -> str:
    """Generate a random string of specified length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_random_email() -> str:
    """Generate a random email address."""
    return f"test_{generate_random_string(8)}@example.com"


def generate_random_username() -> str:
    """Generate a random username."""
    return f"user_{generate_random_string(8)}"


def generate_random_password(length: int = 12) -> str:
    """Generate a random password with mixed characters."""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(random.choices(characters, k=length))
    # Ensure it has at least one uppercase, lowercase, digit, and special char
    return f"A{password}1!"


def generate_user_data() -> Dict[str, str]:
    """Generate complete user registration data."""
    username = generate_random_username()
    return {
        'username': username,
        'email': generate_random_email(),
        'password': generate_random_password(),
        'first_name': random.choice(['John', 'Jane', 'Alice', 'Bob', 'Charlie']),
        'last_name': random.choice(['Smith', 'Doe', 'Johnson', 'Williams', 'Brown']),
    }


def generate_application_data() -> Dict[str, Any]:
    """Generate application form data."""
    return {
        'personal_statement': 'I am very interested in participating in this exchange program. ' * 10,
        'academic_background': 'I have completed 60 credits with a GPA of 3.5.',
        'language_proficiency': 'I am fluent in English and have intermediate Spanish skills.',
        'financial_plan': 'I have savings and will apply for scholarships.',
        'motivation': 'I want to experience a new culture and academic environment.',
    }


def generate_program_data() -> Dict[str, Any]:
    """Generate program creation data."""
    return {
        'name': f'Test Program {generate_random_string(5)}',
        'description': 'This is a test exchange program for E2E testing purposes.',
        'start_date': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d'),
        'end_date': (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d'),
        'min_gpa': round(random.uniform(2.5, 3.5), 2),
        'required_language': random.choice(['English', 'Spanish', 'French', 'German']),
        'max_participants': random.randint(10, 50),
    }


def generate_comment_text() -> str:
    """Generate comment text."""
    comments = [
        'This looks good. Please proceed to the next step.',
        'Could you provide more information about your language skills?',
        'Your application is complete. We will review it shortly.',
        'Please upload the missing documents.',
        'Great application! We are excited to have you.',
    ]
    return random.choice(comments)


def generate_document_filename(extension: str = 'pdf') -> str:
    """Generate a document filename."""
    return f"test_document_{generate_random_string(6)}.{extension}"

