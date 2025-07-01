#!/usr/bin/env python
"""
Test script for the SEIM project.
"""

import os
import sys
import django
from django.core.management import call_command

def run_tests():
    """Run the test suite."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seim.settings")
    django.setup()
    
    # Run the tests
    call_command("test")

if __name__ == "__main__":
    run_tests()
