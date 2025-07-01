#!/usr/bin/env python
"""
Simple import checker - check imports by running the Django shell.
"""

import subprocess
import sys


def check_django_imports():
    """Check Django imports by running management commands"""
    print("Checking Django imports and configuration...")
    
    try:
        # Test Django check command
        result = subprocess.run([
            'python', 'manage.py', 'check'
        ], capture_output=True, text=True, cwd='/app')
        
        if result.returncode == 0:
            print("✅ Django check passed")
        else:
            print("❌ Django check failed:")
            print(result.stdout)
            print(result.stderr)
            return False
            
        # Test Django shell imports
        import_tests = [
            "import exchange.models",
            "import exchange.views", 
            "import exchange.forms",
            "import exchange.serializers",
            "import exchange.services",
            "from exchange.models import Exchange, Document, UserProfile",
            "from django.contrib.auth.models import User",
        ]
        
        for test in import_tests:
            result = subprocess.run([
                'python', 'manage.py', 'shell', '-c', test
            ], capture_output=True, text=True, cwd='/app')
            
            if result.returncode == 0:
                print(f"✅ {test}")
            else:
                print(f"❌ {test}")
                print(f"   Error: {result.stderr.strip()}")
                return False
                
        print("\n🎉 All Django imports are working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error running import checks: {e}")
        return False


if __name__ == "__main__":
    success = check_django_imports()
    sys.exit(0 if success else 1)
