#!/usr/bin/env python3
"""
Simple test script for validating the training form application.

This script performs basic validation tests to ensure the application
can start and core functionality is working.
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported."""
    try:
        import flask
        import sqlalchemy
        from models import create_tables, get_all_training_forms
        from config import DATABASE_URL, USE_SQLITE
        print("[PASS] All imports successful")
        return True
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False

def test_database_connection():
    """Test database connection and basic operations."""
    try:
        from models import engine
        with engine.connect() as conn:
            print("[PASS] Database connection successful")
            return True
    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")
        return False

def test_config():
    """Test configuration loading."""
    try:
        from config import DATABASE_URL, USE_SQLITE, SECRET_KEY
        if not SECRET_KEY or SECRET_KEY == "dev-secret-key":
            print("[WARN] Using default secret key (acceptable for testing)")
        
        print(f"[PASS] Configuration loaded - SQLite: {USE_SQLITE}")
        return True
    except Exception as e:
        print(f"[FAIL] Configuration error: {e}")
        return False

def test_app_creation():
    """Test that the Flask app can be created."""
    try:
        from main import app
        if app:
            print("[PASS] Flask application created successfully")
            return True
        else:
            print("[FAIL] Failed to create Flask application")
            return False
    except Exception as e:
        print(f"[FAIL] Application creation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Running simple application tests...")
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_config),
        ("Database Connection Test", test_database_connection),
        ("Application Creation Test", test_app_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"[FAIL] {test_name} failed")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("[SUCCESS] All tests passed!")
        sys.exit(0)
    else:
        print("[WARNING] Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 