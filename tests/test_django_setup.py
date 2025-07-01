#!/usr/bin/env python
"""
Test script to diagnose Django setup issues and run setup_permissions
"""
import os
import sys
import django
import traceback
from pathlib import Path

def main():
    print("=== Django Setup Test ===")
    
    # Set environment variables
    os.environ['USE_SQLITE'] = 'True'
    os.environ['DJANGO_SETTINGS_MODULE'] = 'seim.settings'
    
    try:
        print(f"Python version: {sys.version}")
        print(f"Django version: {django.get_version()}")
        
        # Add the project directory to Python path
        project_dir = Path(__file__).parent
        sys.path.insert(0, str(project_dir))
        
        print(f"Project directory: {project_dir}")
        print(f"Settings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
        
        # Setup Django
        print("Setting up Django...")
        django.setup()
        print("Django setup successful!")
        
        # Import Django components
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        print("Successfully imported Django auth models")
        
        # Try to import our models
        from exchange.models import Exchange, Document, Course, Grade
        print("Successfully imported exchange models")
        
        # Check if we can access the database  
        print(f"Available content types: {ContentType.objects.count()}")
        print(f"Available permissions: {Permission.objects.count()}")
        print(f"Available groups: {Group.objects.count()}")
        
        # Now try to run our setup_permissions command logic
        print("\n=== Running Permission Setup ===")
        
        # Get content types
        exchange_ct = ContentType.objects.get_for_model(Exchange)
        document_ct = ContentType.objects.get_for_model(Document)
        course_ct = ContentType.objects.get_for_model(Course) 
        grade_ct = ContentType.objects.get_for_model(Grade)
        print("Found all content types")
        
        # Check what permissions exist
        exchange_perms = Permission.objects.filter(content_type=exchange_ct)
        document_perms = Permission.objects.filter(content_type=document_ct)
        course_perms = Permission.objects.filter(content_type=course_ct)
        grade_perms = Permission.objects.filter(content_type=grade_ct)
        
        print(f"Exchange permissions: {exchange_perms.count()}")
        for perm in exchange_perms:
            print(f"  - {perm.codename}: {perm.name}")
            
        print(f"Document permissions: {document_perms.count()}")
        for perm in document_perms:
            print(f"  - {perm.codename}: {perm.name}")
            
        print(f"Course permissions: {course_perms.count()}")
        for perm in course_perms:
            print(f"  - {perm.codename}: {perm.name}")
            
        print(f"Grade permissions: {grade_perms.count()}")
        for perm in grade_perms:
            print(f"  - {perm.codename}: {perm.name}")
        
        print("\n=== Test completed successfully! ===")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        print(f"Error type: {type(e).__name__}")
        print("Traceback:")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
