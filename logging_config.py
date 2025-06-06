"""
Centralized logging configuration for Flask Training Form Application.
Provides structured logging to both files and Seq server in production.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

# Try to import seqlog - optional for development
try:
    import seqlog
    SEQLOG_AVAILABLE = True
except ImportError:
    SEQLOG_AVAILABLE = False
    print("SeqLog not available - install with: pip install seqlog")


def setup_logging(app=None):
    """
    Configure logging for the application.
    - Console logging for development
    - File logging as backup
    - Seq logging for production
    """
    # Determine environment
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if not is_production else logging.INFO)
    
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
    
    # Seq handler (production only)
    if is_production and SEQLOG_AVAILABLE:
        try:
            seqlog.log_to_seq(
                server_url="http://localhost:5341",
                api_key=None,  # No auth required
                level=logging.INFO,
                batch_size=10,
                auto_flush_timeout=10,
                override_root_logger=False
            )
            logging.info("Seq logging configured successfully")
        except Exception as e:
            logging.error(f"Failed to configure Seq logging: {e}")
    
    # Log startup information
    logging.info("=" * 50)
    logging.info(f"Application starting - Environment: {os.environ.get('FLASK_ENV', 'development')}")
    logging.info(f"Log directory: {log_dir.absolute()}")
    if is_production and SEQLOG_AVAILABLE:
        logging.info("Seq logging enabled - View logs at http://localhost:5341")
    logging.info("=" * 50)
    
    # Configure Flask app logging if provided
    if app:
        app.logger.handlers = root_logger.handlers
        app.logger.setLevel(root_logger.level)
        
        # Log Flask requests
        @app.before_request
        def log_request_info():
            """Log incoming request details"""
            if not request.path.startswith('/static'):  # Skip static files
                logger = get_logger('flask.request')
                logger.info(
                    "Request received",
                    extra={
                        'method': request.method,
                        'path': request.path,
                        'remote_addr': request.remote_addr,
                        'user_agent': str(request.user_agent)
                    }
                )
        
        @app.after_request
        def log_response_info(response):
            """Log response details"""
            if not request.path.startswith('/static'):
                logger = get_logger('flask.response')
                logger.info(
                    "Response sent",
                    extra={
                        'method': request.method,
                        'path': request.path,
                        'status': response.status_code,
                        'content_length': response.content_length
                    }
                )
            return response


def get_logger(name):
    """
    Get a logger instance with structured logging support.
    
    Args:
        name: Logger name (typically __name__ from the calling module)
    
    Returns:
        Logger instance configured for structured logging
    """
    logger = logging.getLogger(name)
    
    # Add structured logging capability
    original_log = logger._log
    
    def structured_log(level, msg, args, exc_info=None, extra=None, stack_info=False, **kwargs):
        """Enhanced logging with structured data support"""
        # Merge kwargs into extra for structured logging
        if extra is None:
            extra = {}
        extra.update(kwargs)
        
        # Call original log method
        original_log(level, msg, args, exc_info=exc_info, extra=extra, stack_info=stack_info)
    
    # Replace _log method
    logger._log = structured_log
    
    return logger


# Import Flask request for request logging
try:
    from flask import request
except ImportError:
    pass  # Flask not available during initial setup 