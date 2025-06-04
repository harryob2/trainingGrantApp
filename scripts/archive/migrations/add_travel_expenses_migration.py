#!/usr/bin/env python3
"""
Migration script to add the travel_expenses table.

This script adds a new table to store travel expense records linked to training forms.
"""

import os
import sys
import sqlite3
import logging
from datetime import datetime

# Add the parent directory to the path so we can import from the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_travel_expenses_table():
    """Add the travel_expenses table to the database."""
    
    # Database path
    db_path = "training_forms.db"
    
    if not os.path.exists(db_path):
        logger.error(f"Database file {db_path} not found!")
        return False
    
    # Create backup
    backup_path = f"training_forms_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    try:
        # Create backup
        logger.info(f"Creating backup: {backup_path}")
        import shutil
        shutil.copy2(db_path, backup_path)
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if travel_expenses table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='travel_expenses'")
        if cursor.fetchone():
            logger.info("travel_expenses table already exists. No migration needed.")
            conn.close()
            return True
        
        logger.info("Creating travel_expenses table...")
        
        # Create the travel_expenses table
        create_table_sql = """
        CREATE TABLE travel_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            form_id INTEGER NOT NULL,
            travel_date DATE NOT NULL,
            destination VARCHAR NOT NULL,
            traveler_type VARCHAR NOT NULL,
            traveler_email VARCHAR NOT NULL,
            traveler_name VARCHAR NOT NULL,
            travel_mode VARCHAR NOT NULL,
            cost FLOAT,
            distance_km FLOAT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (form_id) REFERENCES training_forms(id) ON DELETE CASCADE
        )
        """
        
        cursor.execute(create_table_sql)
        logger.info("travel_expenses table created successfully")
        
        # Create indexes for better performance
        logger.info("Creating indexes...")
        
        cursor.execute("CREATE INDEX idx_travel_expenses_form_id ON travel_expenses(form_id)")
        cursor.execute("CREATE INDEX idx_travel_expenses_travel_date ON travel_expenses(travel_date)")
        cursor.execute("CREATE INDEX idx_travel_expenses_traveler_email ON travel_expenses(traveler_email)")
        
        logger.info("Indexes created successfully")
        
        # Commit changes
        conn.commit()
        logger.info("Migration completed successfully!")
        
        # Verify the table was created
        cursor.execute("PRAGMA table_info(travel_expenses)")
        columns = cursor.fetchall()
        logger.info(f"travel_expenses table has {len(columns)} columns:")
        for col in columns:
            logger.info(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        
        # Restore backup if migration failed
        if os.path.exists(backup_path):
            logger.info(f"Restoring backup from {backup_path}")
            shutil.copy2(backup_path, db_path)
        
        return False

if __name__ == "__main__":
    logger.info("Starting travel_expenses table creation migration...")
    success = add_travel_expenses_table()
    
    if success:
        logger.info("Migration completed successfully!")
        sys.exit(0)
    else:
        logger.error("Migration failed!")
        sys.exit(1) 