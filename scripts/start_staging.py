#!/usr/bin/env python
"""Simple staging startup script for deployment."""
import os
import sys
import logging

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('staging_simple.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Start the staging application."""
    try:
        # Set environment
        os.environ['FLASK_ENV'] = 'staging'
        
        logger.info("Starting staging application (simple mode)...")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Python executable: {sys.executable}")
        logger.info(f"Python path: {sys.path[:3]}")  # Show first 3 entries
        
        # Change to parent directory to ensure proper imports
        os.chdir(parent_dir)
        logger.info(f"Changed to directory: {os.getcwd()}")
        
        # Import Flask app
        from app import app
        logger.info("Flask app imported successfully")
        
        # Run the application using Waitress (production WSGI server)
        logger.info("Starting Waitress staging server on port 5001...")
        from waitress import serve
        serve(app, host='0.0.0.0', port=5001, threads=4, connection_limit=500, cleanup_interval=30)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    main() 