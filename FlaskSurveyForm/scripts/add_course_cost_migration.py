#!/usr/bin/env python3
"""
Migration script to add course_cost column to training_forms table.
This script safely adds the new column to existing databases.
"""

import sqlite3
import os
import sys

def add_course_cost_column():
    """Add course_cost column to training_forms table if it doesn't exist."""
    
    # Database path
    db_path = "training_forms.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found. Please ensure you're running this from the correct directory.")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(training_forms)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'course_cost' in columns:
            print("Column 'course_cost' already exists in training_forms table.")
            conn.close()
            return True
        
        # Add the course_cost column
        print("Adding course_cost column to training_forms table...")
        cursor.execute("ALTER TABLE training_forms ADD COLUMN course_cost REAL DEFAULT 0")
        
        # Commit the changes
        conn.commit()
        print("Successfully added course_cost column.")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(training_forms)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'course_cost' in columns:
            print("Migration completed successfully!")
            return True
        else:
            print("Error: Column was not added successfully.")
            return False
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Running course_cost column migration...")
    success = add_course_cost_column()
    
    if success:
        print("Migration completed successfully!")
        sys.exit(0)
    else:
        print("Migration failed!")
        sys.exit(1) 