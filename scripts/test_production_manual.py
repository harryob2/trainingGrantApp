#!/usr/bin/env python
"""
Manual test script for production deployment.
Run this script to test the production startup process manually.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_diagnostics():
    """Run the diagnostics script."""
    print("=" * 60)
    print("RUNNING PRODUCTION DIAGNOSTICS")
    print("=" * 60)
    
    script_dir = Path(__file__).parent
    diagnose_script = script_dir / "diagnose_production.py"
    
    try:
        result = subprocess.run([sys.executable, str(diagnose_script)], 
                              capture_output=True, text=True, cwd=script_dir.parent)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"Failed to run diagnostics: {e}")
        return False

def test_start_production():
    """Test starting the production script."""
    print("=" * 60)
    print("TESTING PRODUCTION STARTUP")
    print("=" * 60)
    
    script_dir = Path(__file__).parent
    start_script = script_dir / "start_production.py"
    
    if not start_script.exists():
        print(f"ERROR: start_production.py not found at {start_script}")
        return False
    
    print(f"Starting production script: {start_script}")
    print("Note: This will start the Flask app. Press Ctrl+C to stop it.")
    print("Press Enter to continue or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\nCancelled by user")
        return False
    
    # Change to parent directory
    os.chdir(script_dir.parent)
    
    try:
        # Run the production script
        subprocess.run([sys.executable, str(start_script)], cwd=script_dir.parent)
        return True
    except KeyboardInterrupt:
        print("\nProduction script stopped by user")
        return True
    except Exception as e:
        print(f"Failed to start production script: {e}")
        return False

def test_flask_import():
    """Test importing the Flask app directly."""
    print("=" * 60)
    print("TESTING FLASK APP IMPORT")
    print("=" * 60)
    
    script_dir = Path(__file__).parent
    parent_dir = script_dir.parent
    
    # Change to parent directory and add to path
    original_cwd = os.getcwd()
    os.chdir(parent_dir)
    sys.path.insert(0, str(parent_dir))
    
    try:
        print(f"Changed directory to: {os.getcwd()}")
        print("Attempting to import Flask app...")
        
        from app import app
        print("✓ Flask app imported successfully!")
        
        print(f"App name: {app.name}")
        print(f"Debug mode: {app.config.get('DEBUG', 'Not set')}")
        print(f"Secret key configured: {bool(app.config.get('SECRET_KEY'))}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to import Flask app: {e}")
        import traceback
        print("Traceback:")
        print(traceback.format_exc())
        return False
    finally:
        os.chdir(original_cwd)

def main():
    """Run all manual tests."""
    print("MANUAL PRODUCTION TESTING SCRIPT")
    print("=" * 60)
    
    tests = [
        ("Diagnostics", run_diagnostics),
        ("Flask Import", test_flask_import),
        ("Production Startup", test_start_production),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name.upper()} {'=' * 20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"ERROR in {test_name}: {e}")
            results[test_name] = False
        
        status = "PASS" if results[test_name] else "FAIL"
        print(f"\n{test_name}: {status}")
    
    print("\n" + "=" * 60)
    print("MANUAL TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n✓ All manual tests passed!")
    else:
        print("\n✗ Some manual tests failed.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 