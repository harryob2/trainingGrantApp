#!/usr/bin/env python3
"""
Test script for Microsoft Graph profile picture functionality
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
try:
    from dotenv import load_dotenv
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print("✓ Loaded environment variables from .env")
    else:
        print("ℹ No .env file found, using system environment variables")
except ImportError:
    print("ℹ python-dotenv not available, using system environment variables")

def test_microsoft_graph_connection():
    """Test basic Microsoft Graph API connection"""
    print("\n=== Testing Microsoft Graph API Connection ===")
    
    try:
        from microsoft_graph import MicrosoftGraphClient
        
        # Check if Azure credentials are available
        client_id = os.environ.get('AZURE_CLIENT_ID')
        client_secret = os.environ.get('AZURE_CLIENT_SECRET')
        tenant_id = os.environ.get('AZURE_TENANT_ID')
        
        if not all([client_id, client_secret, tenant_id]):
            print("❌ Missing Azure credentials. Please set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and AZURE_TENANT_ID")
            return False
        
        print(f"✓ Azure Client ID: {client_id[:8]}...")
        print(f"✓ Azure Tenant ID: {tenant_id}")
        print(f"✓ Azure Client Secret: {'*' * len(client_secret) if client_secret else 'Not set'}")
        
        # Create client and test connection
        client = MicrosoftGraphClient()
        
        # Try to get access token
        token = client._get_access_token()
        if token:
            print("✓ Successfully acquired access token")
            return True
        else:
            print("❌ Failed to acquire access token")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Microsoft Graph connection: {e}")
        return False

def test_profile_picture_functions():
    """Test profile picture retrieval functions"""
    print("\n=== Testing Profile Picture Functions ===")
    
    try:
        from microsoft_graph import get_user_profile_picture, get_user_info
        
        # Test with a known test user
        test_emails = [
            "harry@test.com",  # Bypass user that might exist in Graph
            "harry.obrien@stryker.com",  # Real user (if exists)
        ]
        
        for email in test_emails:
            print(f"\nTesting profile picture for: {email}")
            
            # Test user info retrieval
            user_info = get_user_info(email)
            if user_info:
                print(f"✓ User info retrieved: {user_info.get('display_name', 'No display name')}")
            else:
                print(f"ℹ No user info found for {email}")
            
            # Test profile picture retrieval
            profile_pic = get_user_profile_picture(email)
            if profile_pic:
                print(f"✓ Profile picture retrieved for {email}")
                print(f"  - Data URL length: {len(profile_pic)} characters")
                print(f"  - Format: {profile_pic[:50]}...")
            else:
                print(f"ℹ No profile picture found for {email}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing profile picture functions: {e}")
        return False

def test_employee_data():
    """Test employee data retrieval (limited test)"""
    print("\n=== Testing Employee Data Retrieval ===")
    
    try:
        from microsoft_graph import get_all_employees
        
        print("Getting employee list (this may take a moment)...")
        employees = get_all_employees()
        
        if employees:
            print(f"✓ Retrieved {len(employees)} employees")
            
            # Show a few sample employees (without exposing sensitive data)
            print("\nSample employees:")
            for i, emp in enumerate(employees[:3]):
                first_name = emp.get('first_name', 'Unknown')
                last_name = emp.get('last_name', 'Unknown') 
                department = emp.get('department', 'Unknown')
                print(f"  {i+1}. {first_name} {last_name} - {department}")
            
            if len(employees) > 3:
                print(f"  ... and {len(employees) - 3} more")
        else:
            print("ℹ No employees retrieved")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing employee data retrieval: {e}")
        return False

def main():
    """Run all tests"""
    print("Microsoft Graph Profile Picture Test Suite")
    print("==========================================")
    
    tests = [
        test_microsoft_graph_connection,
        test_profile_picture_functions,
        test_employee_data
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with exception: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 