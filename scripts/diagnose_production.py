#!/usr/bin/env python
"""
Diagnostic script to identify production deployment issues.
Run this to check environment, paths, and dependencies before starting the production app.
"""

import os
import sys
import importlib
from pathlib import Path

def check_python_environment():
    """Check Python environment and executable."""
    print("=" * 50)
    print("PYTHON ENVIRONMENT CHECK")
    print("=" * 50)
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path:")
    for path in sys.path:
        print(f"  {path}")
    print()

def check_file_structure():
    """Check if all required files exist."""
    print("=" * 50)
    print("FILE STRUCTURE CHECK")
    print("=" * 50)
    
    # Get the script directory and parent directory
    script_dir = Path(__file__).parent
    parent_dir = script_dir.parent
    
    print(f"Script directory: {script_dir}")
    print(f"Parent directory: {parent_dir}")
    
    required_files = [
        "app.py",
        "config.py", 
        "models.py",
        "forms.py",
        "auth.py",
        "setup_db.py",
        "requirements.txt",
        ".env"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = parent_dir / file
        if file_path.exists():
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - MISSING")
            missing_files.append(file)
    
    if missing_files:
        print(f"\nMISSING FILES: {', '.join(missing_files)}")
        return False
    else:
        print("\nAll required files found!")
        return True

def check_environment_variables():
    """Check environment variables."""
    print("=" * 50)
    print("ENVIRONMENT VARIABLES CHECK")
    print("=" * 50)
    
    important_vars = [
        "FLASK_ENV",
        "SECRET_KEY", 
        "DEBUG",
        "USE_SQLITE",
        "DB_HOST",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD"
    ]
    
    for var in important_vars:
        value = os.environ.get(var, "NOT SET")
        # Hide sensitive values
        if "PASSWORD" in var or "SECRET" in var:
            display_value = "***" if value != "NOT SET" else value
        else:
            display_value = value
        print(f"{var}: {display_value}")
    print()

def test_imports():
    """Test importing key modules."""
    print("=" * 50)
    print("IMPORT TESTS")
    print("=" * 50)
    
    # Add parent directory to path
    script_dir = Path(__file__).parent
    parent_dir = script_dir.parent
    sys.path.insert(0, str(parent_dir))
    os.chdir(parent_dir)
    
    modules_to_test = [
        "config",
        "models", 
        "forms",
        "auth",
        "app"
    ]
    
    failed_imports = []
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except Exception as e:
            print(f"✗ {module} - ERROR: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\nFAILED IMPORTS: {', '.join(failed_imports)}")
        return False
    else:
        print("\nAll modules imported successfully!")
        return True

def test_database_connection():
    """Test database connectivity."""
    print("=" * 50)
    print("DATABASE CONNECTION TEST")
    print("=" * 50)
    
    try:
        from models import engine
        from config import DATABASE_URL, USE_SQLITE
        
        print(f"Database type: {'SQLite' if USE_SQLITE else 'MariaDB'}")
        print(f"Database URL: {DATABASE_URL}")
        
        # Test connection
        conn = engine.connect()
        print("✓ Database connection successful!")
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def check_port_availability():
    """Check if port 5000 is available."""
    print("=" * 50)
    print("PORT AVAILABILITY CHECK")
    print("=" * 50)
    
    import socket
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', 5000))
        sock.close()
        print("✓ Port 5000 is available")
        return True
    except socket.error as e:
        print(f"✗ Port 5000 is not available: {e}")
        return False

def main():
    """Run all diagnostic checks."""
    print("PRODUCTION DEPLOYMENT DIAGNOSTICS")
    print("=" * 50)
    
    checks = [
        ("Python Environment", check_python_environment),
        ("File Structure", check_file_structure),
        ("Environment Variables", check_environment_variables),
        ("Module Imports", test_imports),
        ("Database Connection", test_database_connection),
        ("Port Availability", check_port_availability)
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"✗ {check_name} - CRITICAL ERROR: {e}")
            results[check_name] = False
        print()
    
    print("=" * 50)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for check_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{check_name}: {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("✓ All diagnostics passed! The app should start successfully.")
        return 0
    else:
        print("✗ Some diagnostics failed. Fix the issues above before starting the app.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 