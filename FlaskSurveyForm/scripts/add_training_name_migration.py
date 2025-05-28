#!/usr/bin/env python3
"""
Migration script to add training_name column to training_forms table.

This script adds the training_name column to the existing training_forms table
for databases that were created before this feature was added.
"""

import sqlite3
import os
import sys

# Add the parent directory to the path so we can import from the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import DATABASE_URL


def add_training_name_column():
    """Add training_name column to training_forms table if it doesn't exist."""
    
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
        
        if 'training_name' in columns:
            print("training_name column already exists. No migration needed.")
            conn.close()
            return True
        
        # Add the training_name column (NOT NULL with default value)
        print("Adding training_name column to training_forms table...")
        cursor.execute("ALTER TABLE training_forms ADD COLUMN training_name TEXT NOT NULL DEFAULT 'Untitled Training'")
        
        # Update existing records to have a meaningful default value based on training_description
        print("Updating existing records with default training names...")
        cursor.execute("""
            UPDATE training_forms 
            SET training_name = CASE 
                WHEN training_description IS NOT NULL AND LENGTH(TRIM(training_description)) > 0 
                THEN SUBSTR(TRIM(training_description), 1, 100)
                ELSE 'Untitled Training'
            END
            WHERE training_name = 'Untitled Training'
        """)
        
        # Commit the changes
        conn.commit()
        print("Successfully added training_name column and updated existing records.")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(training_forms)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'training_name' in columns:
            print("Migration completed successfully!")
            
            # Show how many records were updated
            cursor.execute("SELECT COUNT(*) FROM training_forms")
            total_records = cursor.fetchone()[0]
            print(f"Updated {total_records} existing training form records.")
            
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
    print("Running training_name migration...")
    success = add_training_name_column()
    
    if success:
        print("Migration completed successfully!")
        sys.exit(0)
    else:
        print("Migration failed!")
        sys.exit(1) 