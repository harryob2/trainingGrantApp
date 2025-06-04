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
        logger.info(f"Python executable: {sys.executable}")
        logger.info(f"Log file: {log_file}")
        logger.info("=" * 50)
        
        # Change to parent directory to ensure proper imports
        os.chdir(parent_dir)
        logger.info(f"Changed to directory: {os.getcwd()}")
        
        # Import Flask app
        from app import app
        logger.info("Flask app imported successfully")
        
        # Check configuration
        logger.info(f"Debug mode: {app.config.get('DEBUG', False)}")
        logger.info(f"Environment: {app.config.get('FLASK_ENV', 'production')}")
        logger.info(f"Database URL configured: {bool(app.config.get('DATABASE_URL'))}")
        
        # Write PID file for management
        pid_file = os.path.join(parent_dir, 'production_flask.pid')
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))
        logger.info(f"PID {os.getpid()} written to {pid_file}")
        
        # Run the application
        logger.info("Starting Flask server on 0.0.0.0:5000...")
        logger.info("Application is now ready to serve requests")
        
        # Use threaded mode for better performance in production
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
    finally:
        # Clean up PID file
        pid_file = os.path.join(parent_dir, 'production_flask.pid')
        if os.path.exists(pid_file):
            try:
                os.remove(pid_file)
                logger.info("PID file cleaned up")
            except:
                pass

if __name__ == '__main__':
    main() 