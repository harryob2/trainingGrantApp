#!/usr/bin/env python3
"""
Migration script to add course_cost column to training_catalog table
and populate it with data from the Excel file.

This script safely adds the new column and populates it with course cost data
from cells E197:E376 in the '2_Training Cost' sheet of the limerick IDA.xlsx file.
"""

import os
import sys
import sqlite3
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import TrainingCatalog, db_session, DATABASE_URL
from sqlalchemy import create_engine

# File paths
EXCEL_PATH = os.path.join(os.path.dirname(__file__), '../attached_assets/limerick IDA .xlsx')
SHEET_NAME = '2_Training Cost'


def add_course_cost_column_to_catalog():
    """Add course_cost column to training_catalog table if it doesn't exist."""
    
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
        cursor.execute("PRAGMA table_info(training_catalog)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'course_cost' in columns:
            print("Column 'course_cost' already exists in training_catalog table.")
            conn.close()
            return True
        
        # Add the course_cost column
        print("Adding course_cost column to training_catalog table...")
        cursor.execute("ALTER TABLE training_catalog ADD COLUMN course_cost REAL DEFAULT 0")
        
        # Commit the changes
        conn.commit()
        print("Successfully added course_cost column.")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(training_catalog)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'course_cost' in columns:
            print("Column addition verified successfully!")
            conn.close()
            return True
        else:
            print("Error: Column was not added successfully.")
            conn.close()
            return False
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def extract_course_cost_data():
    """Extract course cost data from Excel file E197:E376."""
    
    if not os.path.exists(EXCEL_PATH):
        print(f"Excel file not found: {EXCEL_PATH}")
        return None
    
    try:
        print(f"Reading course cost data from: {EXCEL_PATH}")
        print(f"Sheet: {SHEET_NAME}, Range: E197:E376")
        
        # Read the specific range E197:E376 (column E is index 4, 0-based)
        # skiprows=196 to start from row 197 (0-indexed)
        # nrows=180 to read exactly 180 rows (E197:E376)
        df = pd.read_excel(
            EXCEL_PATH,
            sheet_name=SHEET_NAME,
            usecols=[4],        # Column E (0-indexed)
            skiprows=196,       # Start from row 197 (0-indexed)
            nrows=180,          # Read exactly 180 rows
            header=None
        )
        
        print(f"Excel DataFrame shape: {df.shape}")
        print(f"Sample course cost data (first 5 values): {df.iloc[:5, 0].tolist()}")
        print(f"Sample course cost data (last 5 values): {df.iloc[-5:, 0].tolist()}")
        
        # Extract the course cost values
        course_costs = df.iloc[:, 0].tolist()
        
        # Clean the data - convert to float, handle NaN values
        cleaned_costs = []
        for cost in course_costs:
            if pd.isna(cost):
                cleaned_costs.append(0.0)
            else:
                try:
                    cleaned_costs.append(float(cost))
                except (ValueError, TypeError):
                    print(f"Warning: Could not convert '{cost}' to float, using 0.0")
                    cleaned_costs.append(0.0)
        
        print(f"Extracted {len(cleaned_costs)} course cost values")
        return cleaned_costs
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None


def populate_course_cost_data(course_costs):
    """Populate the course_cost column with data from Excel file."""
    
    if not course_costs:
        print("No course cost data provided")
        return False
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with db_session() as session:
            # Get all training catalog entries ordered by ID to ensure consistent order
            catalogs = session.query(TrainingCatalog).order_by(TrainingCatalog.id).all()
            
            print(f"Found {len(catalogs)} training catalog entries")
            print(f"Have {len(course_costs)} course cost values")
            
            if len(catalogs) != len(course_costs):
                print(f"Warning: Mismatch between catalog entries ({len(catalogs)}) and cost data ({len(course_costs)})")
                print("Will populate up to the minimum of both lengths")
            
            # Populate course costs in order
            updated_count = 0
            min_length = min(len(catalogs), len(course_costs))
            
            for i in range(min_length):
                catalog = catalogs[i]
                cost = course_costs[i]
                
                # Update the course_cost
                catalog.course_cost = cost
                updated_count += 1
                
                if i < 5:  # Show first 5 updates for verification
                    print(f"  Updated '{catalog.training_name}' with cost: {cost}")
                elif i == 5:
                    print("  ... (showing first 5 updates)")
            
            session.commit()
            print(f"Successfully updated course_cost for {updated_count} training catalog entries")
            return True
            
    except Exception as e:
        print(f"Error updating database: {e}")
        return False


def migrate_catalog_course_cost():
    """Complete migration: add column and populate with Excel data."""
    
    print("Starting training_catalog course_cost migration...")
    
    # Step 1: Add the column
    if not add_course_cost_column_to_catalog():
        print("Failed to add course_cost column")
        return False
    
    # Step 2: Extract course cost data from Excel
    course_costs = extract_course_cost_data()
    if course_costs is None:
        print("Failed to extract course cost data from Excel")
        return False
    
    # Step 3: Populate the database
    if not populate_course_cost_data(course_costs):
        print("Failed to populate course cost data")
        return False
    
    print("Migration completed successfully!")
    return True


if __name__ == "__main__":
    print("Running training_catalog course_cost migration...")
    success = migrate_catalog_course_cost()
    
    if success:
        print("Migration completed successfully!")
        sys.exit(0)
    else:
        print("Migration failed!")
        sys.exit(1) 