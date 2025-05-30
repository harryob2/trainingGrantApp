#!/usr/bin/env python3
"""
Staging Environment Startup Script

This script starts the Training Form Application specifically for staging deployment.
It ensures proper environment configuration and error handling.
"""

import os
import sys
import time
import signal
import logging
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

def setup_staging_environment():
    """Set up staging environment variables."""
    # Ensure we're using the staging environment
    os.environ['FLASK_ENV'] = 'staging'
    
    # Verify the .env file exists
    env_file = '.env'
    if not os.path.exists(env_file):
        print(f"ERROR: {env_file} not found!")
        print("The deployment script should have created this file.")
        sys.exit(1)
    
    print(f"Using environment file: {env_file}")

def check_dependencies():
    """Check that all required dependencies are available."""
    try:
        import flask
        import sqlalchemy
        import pymysql
        import alembic
        print("✅ All required dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def test_database_connection():
    """Test the database connection before starting the application."""
    try:
        from config import DATABASE_URL, USE_SQLITE
        from models import engine
        
        print(f"Testing database connection...")
        print(f"Database URL: {DATABASE_URL}")
        print(f"Using SQLite: {USE_SQLITE}")
        
        # Test connection
        conn = engine.connect()
        conn.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def start_application():
    """Start the Flask application for staging."""
    try:
        print("Starting Training Form Application (Staging)...")
        
        # Import the application
        from app import app
        
        # Configure for staging
        app.config['ENV'] = 'staging'
        
        # Start the application
        print("🚀 Starting application on port 5001...")
        app.run(
            host='0.0.0.0', 
            port=5001, 
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

def handle_shutdown(signum, frame):
    """Handle graceful shutdown."""
    print("\n🛑 Shutting down staging application...")
    sys.exit(0)

def main():
    """Main startup function."""
    print("=" * 60)
    print("🎯 Training Form Application - Staging Startup")
    print("=" * 60)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    # Step 1: Setup environment
    print("\n1. Setting up staging environment...")
    setup_staging_environment()
    
    # Step 2: Check dependencies
    print("\n2. Checking dependencies...")
    if not check_dependencies():
        print("Please install missing dependencies and try again.")
        sys.exit(1)
    
    # Step 3: Test database connection
    print("\n3. Testing database connection...")
    if not test_database_connection():
        print("Please check database configuration and try again.")
        sys.exit(1)
    
    # Step 4: Start application
    print("\n4. Starting application...")
    start_application()

if __name__ == "__main__":
    main() 