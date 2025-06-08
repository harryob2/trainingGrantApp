#!/usr/bin/env python3
"""
Standalone test script for Seq logging functionality.
Run this to test if Seq logging is working properly.
"""

import os
import sys
import logging
import time

# Add the current directory to Python path to import logging_config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logging_config import setup_logging, get_logger


def main():
    """Test Seq logging functionality"""
    print("=" * 60)
    print("SEQ LOGGING TEST SCRIPT")
    print("=" * 60)
    
    # Set environment to production to enable Seq logging
    os.environ['FLASK_ENV'] = 'production'
    
    # Check if API key is set
    api_key = os.environ.get('SEQ_API_KEY')
    print(f"SEQ_API_KEY environment variable: {'SET' if api_key else 'NOT SET'}")
    
    if not api_key:
        print("ERROR: SEQ_API_KEY environment variable is not set!")
        print("Please set it before running this test.")
        return
    
    print(f"API Key length: {len(api_key)} characters")
    print(f"API Key starts with: {api_key[:8]}...")
    
    # Initialize logging
    print("\nInitializing logging configuration...")
    setup_logging()
    
    # Get a logger instance
    logger = get_logger(__name__)
    
    print("\nSending test messages to Seq...")
    
    # Send various test messages
    test_messages = [
        (logging.DEBUG, "DEBUG level test message"),
        (logging.INFO, "INFO level test message"),
        (logging.WARNING, "WARNING level test message"),
        (logging.ERROR, "ERROR level test message"),
        (logging.CRITICAL, "CRITICAL level test message")
    ]
    
    for level, message in test_messages:
        logger.log(level, f"TEST_MESSAGE: {message}")
        print(f"Sent: {logging.getLevelName(level)} - {message}")
        time.sleep(0.5)  # Small delay between messages
    
    # Send structured logging test
    logger.info("STRUCTURED_TEST: This is a structured log message", 
                extra={
                    'user_id': 'test_user',
                    'action': 'seq_test',
                    'result': 'success',
                    'timestamp': time.time()
                })
    
    print("Sent structured log message")
    
    # Force flush logs
    try:
        import seqlog
        seqlog.flush()
        print("Forced flush of Seq logs")
    except Exception as e:
        print(f"Error flushing Seq logs: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)
    print("If Seq logging is working correctly, you should see these messages in Seq at:")
    print("http://localhost:5341 (or http://azulimpbi01:5341)")
    print("\nLook for messages with 'TEST_MESSAGE' and 'STRUCTURED_TEST' prefixes")
    print("Check the debug output above for any connection issues")
    

if __name__ == "__main__":
    main() 