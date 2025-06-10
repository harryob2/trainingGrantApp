#!/usr/bin/env python3
"""
Staging Environment Setup Script for Training Form Application

This script helps set up the staging environment configuration and validates the setup.
"""

import os
import sys
import subprocess

def create_staging_env_file():
    """Create a staging environment file template"""
    staging_env_content = """# Staging Environment Configuration
# This is a template - update the values for your staging environment

# Flask settings
DEBUG=False
SECRET_KEY=staging-secret-key-change-this

# Database settings (MariaDB Staging)
USE_SQLITE=False
DB_HOST=azulimpbi01
DB_PORT=3306
DB_NAME=training_tool_staging
DB_USER=training_staging
DB_PASSWORD=your-staging-password-here

# File upload settings
UPLOAD_FOLDER=TrainingAppData/Uploads_staging
NETWORK_STORAGE_PATH=\\\\strykercorp.com\\lim\\Engineering_DOG\\5. Automation & Controls\\01. Projects\\Training Form Invoices\\staging

# LDAP Configuration
LDAP_HOST=limdc02.strykercorp.com
LDAP_PORT=3268
LDAP_BASE_DN=DC=strykercorp,DC=com
LDAP_DOMAIN=strykercorp.com
LDAP_USE_SSL=False
LDAP_REQUIRED_GROUP=

# Environment
FLASK_ENV=staging
"""
    
    with open('.env.staging', 'w') as f:
        f.write(staging_env_content)
    
    print("✅ Created .env.staging file")
    print("⚠️  Please update the database password and other settings as needed")

def test_staging_database_connection():
    """Test connection to staging database"""
    try:
        # Set environment to staging
        os.environ['FLASK_ENV'] = 'staging'
        
        # Try to import and connect
        from config import DATABASE_URL, USE_SQLITE, DB_NAME
        from models import engine
        
        print(f"Testing staging database connection...")
        print(f"Database: {DB_NAME}")
        print(f"SQLite: {USE_SQLITE}")
        
        # Test connection
        conn = engine.connect()
        print("✅ Staging database connection successful")
        conn.close()
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the application root directory")
        return False
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Check your staging database configuration and ensure the database server is accessible")
        return False

def run_staging_migrations():
    """Run database migrations on staging environment"""
    try:
        print("Running staging database migrations...")
        
        # Set environment to staging
        os.environ['FLASK_ENV'] = 'staging'
        
        # Run migrations
        result = subprocess.run([
            sys.executable, 'scripts/migrate_database.py'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Staging migrations completed successfully")
            print(result.stdout)
            return True
        else:
            print("❌ Staging migrations failed")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False

def validate_staging_setup():
    """Validate the staging environment setup"""
    try:
        # Set environment to staging
        os.environ['FLASK_ENV'] = 'staging'
        
        from config import DATABASE_URL, USE_SQLITE, DB_NAME, UPLOAD_FOLDER
        from models import get_admin_by_email
        
        print("Validating staging environment setup...")
        
        # Check configuration
        print(f"Environment: staging")
        print(f"Database: {DB_NAME}")
        print(f"Use SQLite: {USE_SQLITE}")
        print(f"Upload folder: {UPLOAD_FOLDER}")
        
        # Test admin access
        admin = get_admin_by_email('harry@test.com')
        if admin:
            print("✅ Admin users configured correctly")
        else:
            print("⚠️  No admin users found - run database setup if needed")
        
        # Create upload directory
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
            print(f"✅ Created upload directory: {UPLOAD_FOLDER}")
        else:
            print(f"✅ Upload directory exists: {UPLOAD_FOLDER}")
        
        print("✅ Staging environment validation completed")
        return True
        
    except Exception as e:
        print(f"❌ Staging validation failed: {e}")
        return False

def main():
    """Main staging setup function"""
    print("Training Form Application - Staging Environment Setup")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('config.py'):
        print("❌ Error: config.py not found. Please run this script from the application root directory.")
        sys.exit(1)
    
    success = True
    
    # Step 1: Create staging environment file if it doesn't exist
    if not os.path.exists('.env.staging'):
        print("\n1. Creating staging environment file...")
        create_staging_env_file()
    else:
        print("\n1. Staging environment file already exists")
    
    # Step 2: Test database connection
    print("\n2. Testing staging database connection...")
    if not test_staging_database_connection():
        print("⚠️  Database connection failed. Please:")
        print("   - Ensure the staging database exists (run setup_mariadb_staging.sql)")
        print("   - Update .env.staging with correct database credentials")
        print("   - Ensure the database server is accessible")
        success = False
    
    # Step 3: Run migrations (if database connection works)
    if success:
        print("\n3. Running staging database migrations...")
        if not run_staging_migrations():
            print("⚠️  Migrations failed. Check the error messages above.")
            success = False
    
    # Step 4: Validate setup
    if success:
        print("\n4. Validating staging environment...")
        if not validate_staging_setup():
            success = False
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 Staging environment setup completed successfully!")
        print("\nNext steps:")
        print("1. Update .env.staging with your actual database credentials")
        print("2. Test the staging environment:")
        print("   copy .env.staging .env")
        print("   python main.py")
        print("3. Push to main branch to trigger staging deployment")
    else:
        print("❌ Staging environment setup completed with issues")
        print("Please review the error messages above and resolve the issues")
    
    print("\nFor more information, see docs/deployment.md")

if __name__ == "__main__":
    main() 