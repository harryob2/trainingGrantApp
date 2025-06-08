"""
Centralized logging configuration for Flask Training Form Application.
Provides structured logging to both files and Seq server in production.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
import time
import requests

# Try to import seqlog - optional for development
try:
    import seqlog
    SEQLOG_AVAILABLE = True
except ImportError:
    SEQLOG_AVAILABLE = False


def test_seq_connectivity(server_url, api_key):
    """Test if Seq server is accessible and API key works"""
    try:
        # Test basic connectivity
        test_url = f"{server_url}/api"
        headers = {'X-Seq-ApiKey': api_key} if api_key else {}
        
        print(f"DEBUG: Testing Seq connectivity to {test_url}")
        response = requests.get(test_url, headers=headers, timeout=5)
        print(f"DEBUG: Seq connectivity test - Status: {response.status_code}")
        
        if response.status_code == 200:
            print("DEBUG: Seq server is accessible and API key is valid")
            return True
        elif response.status_code == 401:
            print("DEBUG: Seq server accessible but API key is invalid/unauthorized")
            return False
        else:
            print(f"DEBUG: Seq server returned unexpected status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectRefusedError:
        print(f"DEBUG: Connection refused to Seq server at {server_url}")
        return False
    except requests.exceptions.Timeout:
        print(f"DEBUG: Timeout connecting to Seq server at {server_url}")
        return False
    except Exception as e:
        print(f"DEBUG: Error testing Seq connectivity: {e}")
        return False


def setup_logging(app=None):
    """
    Configure logging for the application.
    - Console logging for development
    - File logging as backup
    - Seq logging for production
    """
    # Determine environment
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    print(f"DEBUG: Environment detected as: {'production' if is_production else 'development'}")
    print(f"DEBUG: SEQLOG_AVAILABLE = {SEQLOG_AVAILABLE}")
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if not is_production else logging.INFO)
    
    print(f"DEBUG: Root logger level set to: {root_logger.level}")
    
    # Clear existing handlers
    root_logger.handlers = []
    
    # Console handler (for development)
    if not is_production:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        print("DEBUG: Console handler added")
    
    # File handler (always enabled as backup)
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    print("DEBUG: File handler added")
    
    # Seq handler (production only)
    if is_production and SEQLOG_AVAILABLE:
        try:
            # Configure Seq logging with API key authentication
            seq_api_key = os.environ.get('SEQ_API_KEY')
            seq_server_url = "http://localhost:5341"
            
            print(f"DEBUG: Seq API key present: {bool(seq_api_key)}")
            print(f"DEBUG: Seq server URL: {seq_server_url}")
            
            if seq_api_key:
                # Test connectivity first
                connectivity_ok = test_seq_connectivity(seq_server_url, seq_api_key)
                print(f"DEBUG: Seq connectivity test result: {connectivity_ok}")
                
                # Configure seqlog with more aggressive settings for debugging
                print("DEBUG: Configuring seqlog...")
                seqlog.log_to_seq(
                    server_url=seq_server_url,
                    api_key=seq_api_key,
                    level=logging.INFO,  # Back to INFO level to reduce noise
                    batch_size=1,  # Send immediately, don't batch
                    auto_flush_timeout=1,  # Flush every second
                    override_root_logger=True  # Changed to True to ensure logs go to Seq
                )
                
                print("DEBUG: seqlog.log_to_seq() completed successfully")
                
                # Test logging immediately after configuration
                logging.info("SEQ_TEST: Seq logging initialized successfully")
                
                # Force flush any pending logs
                try:
                    seqlog.flush()
                    print("DEBUG: Forced flush of seqlog completed")
                except Exception as flush_error:
                    print(f"DEBUG: Error during seqlog flush: {flush_error}")
                
                logging.info("Seq logging configured successfully with API key")
                print("DEBUG: Seq logging setup completed")
                
            else:
                logging.info("No Seq API key found - using file logging only")
                logging.info("Set SEQ_API_KEY environment variable to enable Seq logging")
                print("DEBUG: No Seq API key found")
                
        except Exception as e:
            logging.error(f"Failed to configure Seq logging: {e}")
            logging.info("Continuing with file logging only")
            print(f"DEBUG: Exception during Seq setup: {e}")
            print(f"DEBUG: Exception type: {type(e).__name__}")
            import traceback
            print(f"DEBUG: Full traceback: {traceback.format_exc()}")
    else:
        if not is_production:
            print("DEBUG: Not configuring Seq logging - not in production environment")
        elif not SEQLOG_AVAILABLE:
            print("DEBUG: Not configuring Seq logging - seqlog module not available")
    
    # Log startup information and any import errors
    logging.info("=" * 50)
    logging.info(f"Application starting - Environment: {os.environ.get('FLASK_ENV', 'development')}")
    logging.info(f"Log directory: {log_dir.absolute()}")
    
    # Log seqlog status with more detail
    if SEQLOG_AVAILABLE and is_production:
        logging.info("Seq logging enabled - View logs at http://localhost:5341")
        logging.info(f"Seq configuration: API key present={bool(os.environ.get('SEQ_API_KEY'))}")
    
    logging.info("=" * 50)
    
    # Configure Flask app logging if provided (but remove verbose request/response logging)
    if app:
        app.logger.handlers = root_logger.handlers
        app.logger.setLevel(root_logger.level)


def get_logger(name):
    """
    Get a logger instance with structured logging support.
    
    Args:
        name: Logger name (typically __name__ from the calling module)
    
    Returns:
        Logger instance configured for structured logging
    """
    return logging.getLogger(name)


# Import Flask request for request logging
try:
    from flask import request
except ImportError:
    pass  # Flask not available during initial setup 