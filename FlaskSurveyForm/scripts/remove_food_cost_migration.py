#!/usr/bin/env python3
"""
Migration script to remove the food_cost column from training_forms table.

This script removes the food_cost column that is no longer needed.
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

def remove_food_cost_column():
    """Remove the food_cost column from the training_forms table."""
    
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
        
        # Check if food_cost column exists
        cursor.execute("PRAGMA table_info(training_forms)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'food_cost' not in column_names:
            logger.info("food_cost column does not exist. No migration needed.")
            conn.close()
            return True
        
        logger.info("food_cost column found. Starting migration...")
        
        # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
        
        # 1. Create new table without food_cost column
        create_new_table_sql = """
        CREATE TABLE training_forms_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            training_type VARCHAR NOT NULL,
            training_name VARCHAR NOT NULL,
            trainer_name VARCHAR,
            trainer_email VARCHAR,
            supplier_name VARCHAR,
            location_type VARCHAR NOT NULL,
            location_details VARCHAR,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            training_hours FLOAT,
            trainees_data TEXT,
            submission_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            approved BOOLEAN DEFAULT 0,
            concur_claim VARCHAR,
            travel_cost FLOAT DEFAULT 0,
            materials_cost FLOAT DEFAULT 0,
            other_cost FLOAT DEFAULT 0,
            other_expense_description TEXT,
            course_cost FLOAT DEFAULT 0,
            invoice_number VARCHAR,
            training_description TEXT NOT NULL,
            submitter VARCHAR,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            ida_class VARCHAR
        )
        """
        
        cursor.execute(create_new_table_sql)
        logger.info("Created new table without food_cost column")
        
        # 2. Copy data from old table to new table (excluding food_cost)
        copy_data_sql = """
        INSERT INTO training_forms_new (
            id, training_type, training_name, trainer_name, trainer_email, supplier_name,
            location_type, location_details, start_date, end_date, training_hours,
            trainees_data, submission_date, approved, concur_claim, travel_cost,
            materials_cost, other_cost, other_expense_description, course_cost,
            invoice_number, training_description, submitter, created_at, ida_class
        )
        SELECT 
            id, training_type, training_name, trainer_name, trainer_email, supplier_name,
            location_type, location_details, start_date, end_date, training_hours,
            trainees_data, submission_date, approved, concur_claim, travel_cost,
            materials_cost, other_cost, other_expense_description, course_cost,
            invoice_number, training_description, submitter, created_at, ida_class
        FROM training_forms
        """
        
        cursor.execute(copy_data_sql)
        logger.info("Copied data to new table")
        
        # 3. Drop old table
        cursor.execute("DROP TABLE training_forms")
        logger.info("Dropped old table")
        
        # 4. Rename new table to original name
        cursor.execute("ALTER TABLE training_forms_new RENAME TO training_forms")
        logger.info("Renamed new table to training_forms")
        
        # Commit changes
        conn.commit()
        logger.info("Migration completed successfully!")
        
        # Verify the migration
        cursor.execute("PRAGMA table_info(training_forms)")
        new_columns = cursor.fetchall()
        new_column_names = [col[1] for col in new_columns]
        
        if 'food_cost' not in new_column_names:
            logger.info("Verification successful: food_cost column has been removed")
        else:
            logger.error("Verification failed: food_cost column still exists")
            return False
        
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
    logger.info("Starting food_cost column removal migration...")
    success = remove_food_cost_column()
    
    if success:
        logger.info("Migration completed successfully!")
        sys.exit(0)
    else:
        logger.error("Migration failed!")
        sys.exit(1) 