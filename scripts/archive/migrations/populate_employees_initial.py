#!/usr/bin/env python
"""
One-time migration script to populate the employees table from existing CSV file.
This script should be run once after the employee table is created via Alembic.
After running this script, it should be moved to scripts/archive/migrations/
"""

import os
import sys
import csv
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    # dotenv not available, continue without it
    pass

# Import models after path setup
from models import replace_all_employees

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def populate_employees_from_csv():
    """Populate the employees table from the existing CSV file."""
    
    # Path to the CSV file
    csv_path = project_root / "attached_assets" / "EmployeeListFirstLastDept.csv"
    
    if not csv_path.exists():
        logger.error(f"CSV file not found at {csv_path}")
        return False
    
    logger.info(f"Reading employee data from {csv_path}")
    
    employees_data = []
    
    try:
        with open(csv_path, "r", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                first_name = row.get("FirstName", "").strip()
                last_name = row.get("LastName", "").strip()
                email = row.get("UserPrincipalName", "").strip()
                department = row.get("Department", "").strip()
                
                # Skip rows with missing essential data
                if not first_name or not last_name or not email:
                    logger.warning(f"Skipping incomplete row: {row}")
                    continue
                
                employees_data.append({
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "department": department
                })
        
        logger.info(f"Loaded {len(employees_data)} employees from CSV")
        
        # Populate the database
        if replace_all_employees(employees_data):
            logger.info("Successfully populated employees table")
            return True
        else:
            logger.error("Failed to populate employees table")
            return False
            
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return False

def main():
    """Main function to run the population script."""
    logger.info("=== Starting employee table population ===")
    
    success = populate_employees_from_csv()
    
    if success:
        logger.info("=== Employee table population completed successfully ===")
        logger.info("This script can now be moved to scripts/archive/migrations/")
    else:
        logger.error("=== Employee table population failed ===")
        sys.exit(1)

if __name__ == "__main__":
    main() 