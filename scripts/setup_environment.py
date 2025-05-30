#!/usr/bin/env python3
"""
Environment Setup Script for Training Form Application

This script helps set up the environment configuration and test database connections.
"""

import os
import sys
import shutil
from pathlib import Path

def create_env_files():
    """Create environment files based on the template"""
    template_content = """# Environment Configuration for Training Form Application
# Adjust values as needed for your environment

# Flask settings
DEBUG=True
SECRET_KEY=change-this-secret-key-in-production

# Database settings
USE_SQLITE=True
DB_PATH=training_forms.db

# MariaDB/MySQL settings (for production)
DB_HOST=azulimpbi01
DB_PORT=3306
DB_NAME=training_tool
DB_USER=admin
DB_PASSWORD=your-password-here

# File upload settings
UPLOAD_FOLDER=uploads

# LDAP Configuration
LDAP_HOST=limdc02.strykercorp.com
LDAP_PORT=3268
LDAP_BASE_DN=DC=strykercorp,DC=com
LDAP_DOMAIN=strykercorp.com
LDAP_USE_SSL=False
LDAP_REQUIRED_GROUP=

# Environment specific settings
FLASK_ENV=development
"""

    production_content = template_content.replace(
        "USE_SQLITE=True", "USE_SQLITE=False"
    ).replace(
        "DEBUG=True", "DEBUG=False"
    ).replace(
        "FLASK_ENV=development", "FLASK_ENV=production"
    )

    # Create development environment file
    if not os.path.exists('.env.development'):
        with open('.env.development', 'w') as f:
            f.write(template_content)
        print("✅ Created .env.development")
    else:
        print("ℹ️  .env.development already exists")

    # Create production environment file
    if not os.path.exists('.env.production'):
        with open('.env.production', 'w') as f:
            f.write(production_content)
        print("✅ Created .env.production")
    else:
        print("ℹ️  .env.production already exists")

    # Create default .env pointing to development
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(template_content)
        print("✅ Created .env (development settings)")
    else:
        print("ℹ️  .env already exists")

def test_database_connections():
    """Test database connections for both SQLite and MariaDB"""
    print("\n🔍 Testing database connections...")
    
    # Test SQLite
    try:
        os.environ['USE_SQLITE'] = 'True'
        from config import DATABASE_URL, USE_SQLITE
        print(f"✅ SQLite configuration loaded: {DATABASE_URL}")
        
        # Test SQLite connection
        from sqlalchemy import create_engine
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ SQLite connection successful")
    except Exception as e:
        print(f"❌ SQLite connection failed: {e}")

    # Test MariaDB (if configured)
    try:
        os.environ['USE_SQLITE'] = 'False'
        # Reload config to pick up new environment variable
        import importlib
        import config
        importlib.reload(config)
        
        from config import DATABASE_URL, USE_SQLITE, DB_NAME
        print(f"🔍 Testing MariaDB configuration: {DATABASE_URL.replace(config.DB_PASSWORD, '***')}")
        
        from sqlalchemy import create_engine
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print(f"✅ MariaDB connection successful to database: {DB_NAME}")
    except Exception as e:
        print(f"⚠️  MariaDB connection test failed: {e}")
        print("   This is expected if you haven't set up the MariaDB database yet.")
        print("   Run the SQL script: scripts/setup_mariadb_production.sql")

def install_dependencies():
    """Install required Python dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")

def main():
    """Main setup function"""
    print("🚀 Training Form Application Environment Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py') or not os.path.exists('config.py'):
        print("❌ Error: Please run this script from the application root directory")
        sys.exit(1)
    
    # Install dependencies
    install_dependencies()
    
    # Create environment files
    print("\n📝 Setting up environment files...")
    create_env_files()
    
    # Test database connections
    test_database_connections()
    
    print("\n" + "=" * 50)
    print("🎉 Environment setup completed!")
    print("\nNext steps:")
    print("1. Review and update .env.development and .env.production files")
    print("2. For production: Run the MariaDB setup script:")
    print("   mysql -u root -p < scripts/setup_mariadb_production.sql")
    print("3. To use production environment:")
    print("   export FLASK_ENV=production")
    print("4. To start the application:")
    print("   python main.py")

if __name__ == "__main__":
    main() 