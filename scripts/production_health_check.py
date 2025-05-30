#!/usr/bin/env python
"""Production health check script."""
import requests
import sys

try:
    # Test root endpoint
    r = requests.get('http://localhost:5000', timeout=15)
    if r.status_code == 200:
        print('PASS: Production root endpoint responding')
    else:
        print(f'FAIL: Root endpoint returned status {r.status_code}')
        sys.exit(1)
    
    # Test API endpoint
    r = requests.get('http://localhost:5000/api/employees', timeout=15)
    if r.status_code == 200:
        print('PASS: Production API health check passed')
    elif r.status_code == 401:
        print('PASS: Production API requires authentication (expected)')
    else:
        print(f'WARNING: API health check status: {r.status_code}')
except Exception as e:
    print(f'FAIL: Health check failed: {e}')
    sys.exit(1) 