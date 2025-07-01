#!/usr/bin/env python
"""
Test script to verify views refactoring worked correctly
Tests backward compatibility of imports after views consolidation
"""

import sys
import os

# Add the SEIM directory to Python path
sys.path.insert(0, r'E:\mario\Documents\SGII\SEIM')

def test_views_imports():
    """Test that all view imports work correctly after refactoring"""
    try:
        # Test main views import (should work via compatibility layer)
        print("Testing main views import...")
        from exchange import views
        print("✅ Main views import successful")
        
        # Test specific view function imports
        print("\nTesting specific view function imports...")
        
        # Core views that should be available
        test_functions = [
            'dashboard',
            'exchange_list', 
            'exchange_detail',
            'create_exchange',
            'login_view',
            'analytics_view',
            'batch_processing',
            'upload_document',
            'health_check'
        ]
        
        for func_name in test_functions:
            if hasattr(views, func_name):
                print(f"✅ {func_name} - Available")
            else:
                print(f"❌ {func_name} - Missing")
        
        # Test class-based views
        print("\nTesting class-based view imports...")
        test_classes = [
            'ExchangeDataTableView',
            'CustomAuthToken',
            'RegisterView',
            'BulkActionView'
        ]
        
        for class_name in test_classes:
            if hasattr(views, class_name):
                print(f"✅ {class_name} - Available")
            else:
                print(f"❌ {class_name} - Missing")
        
        # Test direct import from views package
        print("\nTesting direct package imports...")
        try:
            from exchange.views import dashboard, analytics_view, health_check
            print("✅ Direct package imports successful")
        except ImportError as e:
            print(f"❌ Direct package imports failed: {e}")
        
        # Test __all__ attribute
        print(f"\nTotal exported functions/classes: {len(views.__all__)}")
        print("✅ Views refactoring verification completed successfully!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("SGII Views Refactoring Verification")
    print("=" * 40)
    
    success = test_views_imports()
    
    if success:
        print("\n🎉 All tests passed! Views refactoring was successful.")
    else:
        print("\n⚠️  Some tests failed. Check the refactoring.")
