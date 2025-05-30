#!/usr/bin/env python3
"""
Migration script to add invoice_number column to training_forms table.

This script safely adds the invoice_number column to existing databases.
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add the parent directory to the path so we can import from the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def add_invoice_number_column():
    """Add invoice_number column to training_forms table if it doesn't exist."""
    
    db_path = "training_forms.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found. No migration needed.")
        return
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(training_forms)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'invoice_number' in columns:
            print("invoice_number column already exists. No migration needed.")
            conn.close()
            return
        
        print("Adding invoice_number column to training_forms table...")
        
        # Add the new column
        cursor.execute("""
            ALTER TABLE training_forms 
            ADD COLUMN invoice_number TEXT
        """)
        
        # Commit the changes
        conn.commit()
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(training_forms)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'invoice_number' in columns:
            print("✓ Successfully added invoice_number column to training_forms table")
        else:
            print("✗ Failed to add invoice_number column")
            
        conn.close()
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return False
    
    return True

def main():
    """Main migration function."""
    print("=" * 60)
    print("Invoice Number Column Migration")
    print("=" * 60)
    print(f"Started at: {datetime.now()}")
    print()
    
    success = add_invoice_number_column()
    
    print()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
    print(f"Finished at: {datetime.now()}")
    print("=" * 60)

if __name__ == "__main__":
    main() 