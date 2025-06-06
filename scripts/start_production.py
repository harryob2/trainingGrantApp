#!/usr/bin/env python
"""Production startup script for deployment."""
import os
import sys
import logging
import signal
import time
from datetime import datetime

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Configure logging
log_file = os.path.join(parent_dir, 'production.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)

def main():
    """Start the production application."""
    try:
        # Set up signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Set environment
        os.environ['FLASK_ENV'] = 'production'
        
        logger.info("=" * 50)
        logger.info("Starting Training Form Application - PRODUCTION")
        logger.info(f"Timestamp: {datetime.now()}")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Script directory: {current_dir}")
        logger.info(f"Parent directory: {parent_dir}")
        logger.info(f"Python executable: {sys.executable}")
        logger.info(f"Log file: {log_file}")
        logger.info("=" * 50)
        
        # Change to parent directory to ensure proper imports
        original_cwd = os.getcwd()
        os.chdir(parent_dir)
        logger.info(f"Changed working directory from {original_cwd} to {os.getcwd()}")
        
        # Verify critical files exist
        critical_files = ['app.py', 'config.py', 'models.py', '.env']
        for file in critical_files:
            file_path = os.path.join(parent_dir, file)
            if os.path.exists(file_path):
                logger.info(f"[OK] Found {file}")
            else:
                logger.error(f"[FAIL] Missing critical file: {file}")
                raise FileNotFoundError(f"Critical file missing: {file}")
        
        # Check environment variables
        required_env_vars = ['SECRET_KEY']
        for var in required_env_vars:
            if not os.environ.get(var):
                logger.warning(f"Environment variable {var} is not set")
        
        # Import Flask app
        logger.info("Importing Flask application...")
        from app import app
        logger.info("Flask app imported successfully")
        
        # Check configuration
        logger.info("Configuration check:")
        logger.info(f"  Debug mode: {app.config.get('DEBUG', False)}")
        logger.info(f"  Environment: {app.config.get('FLASK_ENV', 'production')}")
        logger.info(f"  Secret key configured: {bool(app.config.get('SECRET_KEY'))}")
        logger.info(f"  Database URL configured: {bool(app.config.get('DATABASE_URL'))}")
        logger.info(f"  Upload folder: {app.config.get('UPLOAD_FOLDER', 'Not set')}")
        
        # Test database connection
        try:
            from models import engine
            with engine.connect() as conn:
                logger.info("[OK] Database connection test successful")
        except Exception as e:
            logger.error(f"[FAIL] Database connection test failed: {e}")
            # Don't fail here - let Flask handle database errors
        
        # Write PID file for management
        pid_file = os.path.join(parent_dir, 'production_flask.pid')
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))
        logger.info(f"PID {os.getpid()} written to {pid_file}")
        
        # Run the application using Waitress (production WSGI server)
        logger.info("Starting Waitress production server on 0.0.0.0:5000...")
        logger.info("Application is now ready to serve requests")
        
        # Use Waitress for production deployment
        from waitress import serve
        serve(app, host='0.0.0.0', port=5000, threads=6, connection_limit=1000, cleanup_interval=30)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Additional debugging info
        logger.error("Debug information:")
        logger.error(f"  Current working directory: {os.getcwd()}")
        logger.error(f"  Python path: {sys.path[:3]}...")  # First few entries
        logger.error(f"  Environment variables (partial): FLASK_ENV={os.environ.get('FLASK_ENV')}")
        
        sys.exit(1)
    finally:
        # Clean up PID file
        pid_file = os.path.join(parent_dir, 'production_flask.pid')
        if os.path.exists(pid_file):
            try:
                os.remove(pid_file)
                logger.info("PID file cleaned up")
            except Exception as e:
                logger.warning(f"Could not clean up PID file: {e}")

if __name__ == '__main__':
    main() 