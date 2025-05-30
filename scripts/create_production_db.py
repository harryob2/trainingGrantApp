#!/usr/bin/env python
"""Create production database if it doesn't exist."""
import pymysql
import os
import sys

# Get connection details from environment or secrets
db_host = os.getenv('DB_HOST', sys.argv[1] if len(sys.argv) > 1 else 'localhost')
db_port = int(os.getenv('DB_PORT', sys.argv[2] if len(sys.argv) > 2 else '3306'))
db_name = os.getenv('DB_NAME', sys.argv[3] if len(sys.argv) > 3 else 'training_tool')
db_user = os.getenv('DB_USER', sys.argv[4] if len(sys.argv) > 4 else 'root')
db_password = os.getenv('DB_PASSWORD', sys.argv[5] if len(sys.argv) > 5 else '')

print(f'Connecting to MySQL server at {db_host}:{db_port}...')

try:
    # Connect without specifying database
    conn = pymysql.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        charset='utf8mb4'
    )
    
    with conn.cursor() as cursor:
        # Check if database exists
        cursor.execute('SHOW DATABASES')
        databases = [row[0] for row in cursor.fetchall()]
        
        if db_name in databases:
            print(f'Database {db_name} already exists')
        else:
            print(f'Creating database {db_name}...')
            cursor.execute(f'CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
            conn.commit()
            print(f'Database {db_name} created successfully')
    
    conn.close()
    print('PASS: Database setup completed')
    sys.exit(0)
    
except Exception as e:
    print(f'ERROR: Failed to setup database: {e}')
    sys.exit(1) 