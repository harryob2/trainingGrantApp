#!/usr/bin/env python3
"""
Migration script to add trainer_email column to training_forms table.

This script adds the trainer_email column to the existing training_forms table
for databases that were created before this feature was added.
"""

import sqlite3
import os
import sys

# Add the parent directory to the path so we can import from the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import DATABASE_URL


def add_trainer_email_column():
    """Add trainer_email column to training_forms table if it doesn't exist."""
    
    # Extract the database path from the DATABASE_URL
    db_path = DATABASE_URL.replace("sqlite:///", "")
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(training_forms)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'trainer_email' in columns:
            print("trainer_email column already exists. No migration needed.")
            conn.close()
            return True
        
        # Add the trainer_email column
        print("Adding trainer_email column to training_forms table...")
        cursor.execute("ALTER TABLE training_forms ADD COLUMN trainer_email TEXT")
        
        # Commit the changes
        conn.commit()
        print("Successfully added trainer_email column.")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(training_forms)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'trainer_email' in columns:
            print("Migration completed successfully!")
            conn.close()
            return True
        else:
            print("ERROR: Column was not added successfully.")
            conn.close()
            return False
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if 'conn' in locals():
            conn.close()
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        if 'conn' in locals():
            conn.close()
        return False


if __name__ == "__main__":
    print("Running trainer_email migration...")
    success = add_trainer_email_column()
    
    if success:
        print("Migration completed successfully!")
        sys.exit(0)
    else:
        print("Migration failed!")
        sys.exit(1) 