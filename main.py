"""
Entry point for the training form application.

This module imports the Flask application and starts the server.
"""

import sys
import argparse
from app import app

def main():
    """Main entry point with command line argument support."""
    parser = argparse.ArgumentParser(description='Training Form Application')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to listen on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--no-debug', action='store_true', help='Disable debug mode')
    
    args = parser.parse_args()
    
    # Determine debug mode
    if args.no_debug:
        debug_mode = False
    elif args.debug:
        debug_mode = True
    else:
        debug_mode = app.config.get("DEBUG", True)
    
    print(f"Starting Training Form Application...")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Debug: {debug_mode}")
    print(f"Environment: {app.config.get('FLASK_ENV', 'development')}")
    
    app.run(host=args.host, port=args.port, debug=debug_mode)

if __name__ == "__main__":
    main()
