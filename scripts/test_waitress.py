#!/usr/bin/env python
"""Test script to verify Waitress WSGI server setup."""
import os
import sys

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def test_waitress_import():
    """Test if Waitress can be imported."""
    try:
        from waitress import serve
        print("[OK] Waitress import successful")
        return True
    except ImportError as e:
        print(f"[FAIL] Waitress import failed: {e}")
        return False

def test_flask_app_import():
    """Test if Flask app can be imported."""
    try:
        # Change to parent directory
        os.chdir(parent_dir)
        from app import app
        print("[OK] Flask app import successful")
        return True, app
    except Exception as e:
        print(f"[FAIL] Flask app import failed: {e}")
        return False, None

def test_flask_config(app):
    """Test Flask configuration."""
    print("\nFlask Configuration:")
    print(f"  Debug mode: {app.config.get('DEBUG', 'Not set')}")
    print(f"  Environment: {app.config.get('FLASK_ENV', 'Not set')}")
    print(f"  Secret key configured: {'Yes' if app.config.get('SECRET_KEY') else 'No'}")
    print(f"  Database URL configured: {'Yes' if app.config.get('DATABASE_URL') else 'No'}")

def main():
    """Run all tests."""
    print("Testing Waitress WSGI Server Setup")
    print("=" * 40)
    
    # Test imports
    waitress_ok = test_waitress_import()
    flask_ok, app = test_flask_app_import()
    
    if not waitress_ok:
        print("\n[FAIL] Please install Waitress: pip install waitress")
        return False
    
    if not flask_ok:
        print("\n[FAIL] Flask app cannot be imported")
        return False
    
    # Test configuration
    test_flask_config(app)
    
    print("\n[SUCCESS] All tests passed! Waitress should work correctly.")
    print("\nTo start the server with Waitress:")
    print("  python scripts/start_production.py")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 