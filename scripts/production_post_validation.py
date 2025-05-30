#!/usr/bin/env python
"""Post-deployment validation for production."""
from models import db
from app import app

with app.app_context():
    try:
        # Test database connectivity
        result = db.session.execute(db.text('SELECT 1')).scalar()
        print('PASS: Database query successful')
        
        # Check tables exist
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f'Database has {len(tables)} tables')
        if len(tables) > 0:
            print('PASS: Database schema is initialized')
        else:
            print('WARNING: No tables found in database')
    except Exception as e:
        print(f'ERROR: Database validation failed: {e}')
        raise 