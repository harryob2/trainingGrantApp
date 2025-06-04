import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from sqlalchemy.orm import sessionmaker
from models import TrainingCatalog, DATABASE_URL
from sqlalchemy import create_engine

EXCEL_PATH = os.path.join(os.path.dirname(__file__), '../attached_assets/limerick IDA .xlsx')
SHEET_NAME = '2_Training Cost'


def get_training_days_lookup():
    print(f"Reading Excel file from: {EXCEL_PATH}")
    df = pd.read_excel(
        EXCEL_PATH,
        sheet_name=SHEET_NAME,
        usecols=[1, 3],  # B and D columns (0-indexed)
        skiprows=8,      # B9 is row 8 (0-indexed)
        nrows=180,       # 188-9+1 = 180
        header=None
    )
    print(f"Excel DataFrame shape: {df.shape}")
    print(f"First 5 rows:\n{df.head()}")
    lookup = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
    return lookup


def get_training_type_supplier_cost_lookup():
    # Read columns B-E (1-4) and rows 197-376 (skip 196, nrows=180)
    df = pd.read_excel(
        EXCEL_PATH,
        sheet_name=SHEET_NAME,
        usecols=[1, 2, 3, 4],  # B, C, D, E columns (0-indexed)
        skiprows=196,          # B197 is row 196 (0-indexed)
        nrows=180,             # 376-197+1 = 180
        header=None
    )
    print(f"Second table DataFrame shape: {df.shape}")
    print(f"First 5 rows of second table:\n{df.head()}")
    lookup = {}
    for idx, row in df.iterrows():
        training_name = row[1]
        supplier_name = row[2]
        training_type_val = row[3]
        course_cost = row[4]
        if pd.isna(training_name):
            continue
        if training_type_val == "Internal":
            lookup[training_name] = {
                "training_type": "Internal Training",
                "supplier_name": None,
                "course_cost": None,
            }
        elif training_type_val == "External-Eligible":
            lookup[training_name] = {
                "training_type": "External Training",
                "supplier_name": supplier_name if pd.notna(supplier_name) else None,
                "course_cost": float(course_cost) if pd.notna(course_cost) else None,
            }
    return lookup


def populate_training_hours_and_details():
    days_lookup = get_training_days_lookup()
    details_lookup = get_training_type_supplier_cost_lookup()
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        catalogs = session.query(TrainingCatalog).all()
        print(f"Found {len(catalogs)} training catalog entries.")
        updated = 0
        for catalog in catalogs:
            name = catalog.training_name
            # Update training_hours
            days = days_lookup.get(name)
            print(f"Catalog: {name}, Days found: {days}")
            if days is not None:
                try:
                    hours = float(days) * 8
                except Exception as e:
                    print(f"Error converting days to hours for {name}: {e}")
                    hours = None
                catalog.training_hours = hours
            # Update training_type, supplier_name, course_cost
            details = details_lookup.get(name)
            if details:
                catalog.training_type = details["training_type"]
                catalog.supplier_name = details["supplier_name"]
                catalog.course_cost = details["course_cost"]
                print(f"Updated details for {name}: {details}")
            updated += 1
        session.commit()
        print(f"Updated training_hours and details for {updated} catalog entries.")
    except Exception as e:
        print(f"Error during DB update: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    populate_training_hours_and_details() 