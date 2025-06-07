import csv
import os
import logging
from models import TrainingCatalog, engine # Import the engine from models instead of creating our own
from sqlalchemy.orm import Session
from datetime import datetime

# Configure logging if not already configured by the main app
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO)

# Cache for employee data to avoid reading CSV on every call
_employee_cache = None
_training_catalog_cache = None # Cache for training catalog data
_cache_timestamp = None
CACHE_EXPIRE_HOURS = 24

def is_cache_expired():
    if not _cache_timestamp:
        return True
    return (datetime.now() - _cache_timestamp).hours > CACHE_EXPIRE_HOURS

def get_lookup_data(entity_type: str):
    """
    Fetches lookup data for a given entity type.
    Supports 'employees' and 'trainings'.
    """
    global _employee_cache, _training_catalog_cache

    if entity_type == "employees":
        if _employee_cache is not None:
            logger.debug("Returning cached employee data.")
            return _employee_cache

        logger.info("Loading employee data from database")
        try:
            from models import get_all_employees
            employees = get_all_employees()
            
            # Cache the results
            _employee_cache = employees
            logger.info(f"Loaded and cached {len(employees)} employees from database.")
            return employees
        except Exception as e:
            logger.error(f"Error loading employee data from database: {str(e)}")
            
            # Fallback to CSV if database fails
            logger.info("Attempting fallback to CSV file")
            try:
                employees = []
                csv_path = os.path.join(os.path.dirname(__file__), "..", "attached_assets", "EmployeeListFirstLastDept.csv")

                if not os.path.exists(csv_path):
                    alt_csv_path = os.path.join("attached_assets", "EmployeeListFirstLastDept.csv")
                    if os.path.exists(alt_csv_path):
                        csv_path = alt_csv_path
                    else:
                        logger.error(f"Employee list CSV not found at {csv_path} or {alt_csv_path}")
                        return []

                logger.info(f"Loading employee data from CSV fallback: {csv_path}")
                with open(csv_path, "r", encoding="utf-8-sig") as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        first_name = row.get("FirstName", "").strip()
                        last_name = row.get("LastName", "").strip()
                        email = row.get("UserPrincipalName", "").strip()
                        department = row.get("Department", "").strip()

                        if first_name and last_name and email:
                            display_name = f"{first_name} {last_name}"
                            employees.append(
                                {
                                    "displayName": display_name,
                                    "email": email,
                                    "name": display_name,
                                    "department": department,
                                    "firstName": first_name,
                                    "lastName": last_name,
                                }
                            )
                _employee_cache = employees
                logger.info(f"Loaded and cached {len(employees)} employees from CSV fallback.")
                return employees
            except Exception as csv_error:
                logger.error(f"Error loading employee data from CSV fallback: {str(csv_error)}")
                return []

    elif entity_type == "trainings":
        if _training_catalog_cache is not None:
            logger.debug("Returning cached training catalog data.")
            return _training_catalog_cache
        
        trainings = []
        try:
            # Use the engine from models.py which reads the correct environment configuration
            with Session(engine) as session:
                catalog_items = session.query(TrainingCatalog).all()
                for item in catalog_items:
                    training_data = {
                        "id": item.id,
                        "training_name": item.training_name, # Frontend expects 'training_name'
                        "name": item.training_name, # Keep 'name' for backwards compatibility
                        "area": item.area,         # Key for subtitle/secondary info
                        "training_desc": item.training_desc,  # Add training description for form population
                        # Add other fields if needed by frontend, but keep it minimal for lookup
                        "ida_class": item.ida_class,
                        "training_type": item.training_type,
                        "supplier_name": item.supplier_name,  # Add supplier name for External Training
                        "training_hours": item.training_hours,  # Add training hours
                        "course_cost": item.course_cost
                    }
                    trainings.append(training_data)
                    
                # Debug: Log the first few training items to check data structure
                if trainings:
                    logger.info(f"Sample training data (first item): {trainings[0]}")
                    
            _training_catalog_cache = trainings
            logger.info(f"Loaded and cached {len(trainings)} training catalog items.")
            return trainings
        except Exception as e:
            logger.error(f"Error loading training catalog data: {str(e)}")
            return []
    
    logger.warning(f"Unknown entity type for lookup: {entity_type}")
    return []

def clear_training_catalog_cache():
    """Clear the training catalog cache to force reload of data."""
    global _training_catalog_cache
    _training_catalog_cache = None
    logger.info("Training catalog cache cleared.")

def clear_employee_cache():
    """Clear the employee cache to force reload of data."""
    global _employee_cache
    _employee_cache = None
    logger.info("Employee cache cleared.")

if __name__ == '__main__':
    # For testing the module directly
    print("Testing get_lookup_data('employees'):")
    employee_data = get_lookup_data('employees')
    if employee_data:
        print(f"Found {len(employee_data)} employees. First 3:")
        for emp in employee_data[:3]:
            print(emp)
    else:
        print("No employee data found.")

    print("\nTesting get_lookup_data('trainings'):")
    training_data = get_lookup_data('trainings')
    if training_data:
        print(f"Found {len(training_data)} training items. First 3:")
        for tr in training_data[:3]:
            print(tr)
    else:
        print("No training data found.")

    print("\nTesting get_lookup_data('unknown_type'):")
    unknown_data = get_lookup_data('unknown_type')
    print(unknown_data) 