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
import argparse
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

def setup_logging():
    """Set up logging for better debugging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('staging_app.log')
        ]
    )
    return logging.getLogger(__name__)

def setup_staging_environment():
    """Set up staging environment variables."""
    logger = logging.getLogger(__name__)
    
    # Ensure we're using the staging environment
    os.environ['FLASK_ENV'] = 'staging'
    logger.info("Set FLASK_ENV to 'staging'")
    
    # Verify the .env file exists
    env_file = '.env'
    if not os.path.exists(env_file):
        logger.error(f"ERROR: {env_file} not found!")
        logger.error("The deployment script should have created this file.")
        sys.exit(1)
    
    logger.info(f"Using environment file: {env_file}")
    
    # Show some environment info for debugging
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path[0]}")

def check_dependencies():
    """Check that all required dependencies are available."""
    logger = logging.getLogger(__name__)
    
    dependencies = ['flask', 'sqlalchemy', 'pymysql', 'alembic', 'werkzeug']
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep)
            logger.info(f"PASS: {dep} found")
        except ImportError as e:
            logger.error(f"FAIL: {dep} missing: {e}")
            missing.append(dep)
    
    if missing:
        logger.error(f"Missing dependencies: {missing}")
        return False
    
    logger.info("PASS: All required dependencies found")
    return True

def test_database_connection():
    """Test the database connection before starting the application."""
    logger = logging.getLogger(__name__)
    
    try:
        # Import configuration
        logger.info("Loading configuration...")
        from config import DATABASE_URL, USE_SQLITE
        
        logger.info(f"Database URL: {DATABASE_URL}")
        logger.info(f"Using SQLite: {USE_SQLITE}")
        
        # Test connection
        logger.info("Testing database connection...")
        from models import engine
        
        conn = engine.connect()
        logger.info("PASS: Database connection established")
        conn.close()
        logger.info("PASS: Database connection closed cleanly")
        return True
        
    except Exception as e:
        logger.error(f"FAIL: Database connection failed: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def start_application(port=5001):
    """Start the Flask application for staging."""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Loading Flask application...")
        
        # Import the application
        from app import app
        
        # Configure for staging
        app.config['ENV'] = 'staging'
        app.config['DEBUG'] = False
        
        logger.info(f"Application configuration:")
        logger.info(f"  - ENV: {app.config.get('ENV')}")
        logger.info(f"  - DEBUG: {app.config.get('DEBUG')}")
        logger.info(f"  - SECRET_KEY set: {'SECRET_KEY' in app.config}")
        
        # Start the application
        logger.info(f"Starting application on 0.0.0.0:{port}...")
        app.run(
            host='0.0.0.0', 
            port=port, 
            debug=False,
            use_reloader=False,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"FAIL: Failed to start application: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

def handle_shutdown(signum, frame):
    """Handle graceful shutdown."""
    logger = logging.getLogger(__name__)
    logger.info("\nShutting down staging application...")
    sys.exit(0)

def main():
    """Main startup function."""
    parser = argparse.ArgumentParser(description='Training Form Application - Staging Startup')
    parser.add_argument('--port', type=int, default=5001, help='Port to listen on')
    parser.add_argument('--test-only', action='store_true', help='Only run tests, do not start application')
    
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logging()
    
    logger.info("=" * 60)
    logger.info("Training Form Application - Staging Startup")
    logger.info("=" * 60)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    # Step 1: Setup environment
    logger.info("\n1. Setting up staging environment...")
    setup_staging_environment()
    
    # Step 2: Check dependencies
    logger.info("\n2. Checking dependencies...")
    if not check_dependencies():
        logger.error("Please install missing dependencies and try again.")
        sys.exit(1)
    
    # Step 3: Test database connection
    logger.info("\n3. Testing database connection...")
    if not test_database_connection():
        logger.error("Please check database configuration and try again.")
        sys.exit(1)
    
    if args.test_only:
        logger.info("PASS: All tests passed! (test-only mode)")
        return
    
    # Step 4: Start application
    logger.info("\n4. Starting application...")
    start_application(args.port)

if __name__ == "__main__":
    main() 