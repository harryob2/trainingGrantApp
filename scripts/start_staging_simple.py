#!/usr/bin/env python
"""Simple staging startup script for deployment."""
import os
import sys
import logging

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
        
        # Import Flask app
        from app import app
        logger.info("Flask app imported successfully")
        
        # Run the application
        logger.info("Starting Flask server on port 5001...")
        app.run(host='0.0.0.0', port=5001, debug=False)
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    main() 