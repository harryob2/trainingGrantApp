#!/usr/bin/env python3
"""
Migration script to move trainees data from JSON in trainees_data column
to the new normalized Trainee table.

Since the trainees_data column has been removed, this script will read
from a backup database or existing data if available.
"""

import json
import logging
import sqlite3
from models import (
    db_session, 
    TrainingForm, 
    Trainee, 
    create_tables
)

logging.basicConfig(level=logging.INFO)

def migrate_trainees_from_backup():
    """Migrate trainees data from backup database if available"""
    print("Starting trainee data migration...")
    
    # First, create all tables including the new Trainee table
    create_tables()
    print("Tables created/updated successfully")
    
    # Check if backup database exists
    backup_files = [
        "training_forms_backup_20250527_171208.db",
        "training_forms_backup_20250528_204609.db", 
        "training_forms_backup_20250528_211940.db"
    ]
    
    backup_db = None
    for backup_file in backup_files:
        try:
            conn = sqlite3.connect(backup_file)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='training_forms';")
            if cursor.fetchone():
                # Check if trainees_data column exists
                cursor.execute("PRAGMA table_info(training_forms);")
                columns = [row[1] for row in cursor.fetchall()]
                if 'trainees_data' in columns:
                    backup_db = backup_file
                    print(f"Found backup database: {backup_file}")
                    break
            conn.close()
        except Exception:
            continue
    
    if not backup_db:
        print("No backup database with trainees_data found. Creating sample data for testing...")
        create_sample_trainees()
        return
    
    # Migrate from backup
    migrated_count = 0
    error_count = 0
    
    try:
        # Connect to backup database
        backup_conn = sqlite3.connect(backup_db)
        backup_cursor = backup_conn.cursor()
        
        # Get forms with trainees_data
        backup_cursor.execute("""
            SELECT id, trainees_data 
            FROM training_forms 
            WHERE trainees_data IS NOT NULL 
            AND trainees_data != '' 
            AND trainees_data != '[]'
        """)
        
        backup_forms = backup_cursor.fetchall()
        print(f"Found {len(backup_forms)} forms with trainees_data in backup")
        
        with db_session() as session:
            for form_id, trainees_data in backup_forms:
                try:
                    # Check if this form exists in current database
                    current_form = session.query(TrainingForm).filter_by(id=form_id).first()
                    if not current_form:
                        print(f"Skipping form {form_id} - not found in current database")
                        continue
                    
                    # Check if trainees already migrated
                    existing_trainees = session.query(Trainee).filter_by(form_id=form_id).count()
                    if existing_trainees > 0:
                        print(f"Skipping form {form_id} - trainees already migrated")
                        continue
                    
                    # Parse JSON trainees data
                    trainees_json = json.loads(trainees_data)
                    if not isinstance(trainees_json, list):
                        continue
                    
                    # Insert trainees
                    for trainee_data in trainees_json:
                        if isinstance(trainee_data, dict):
                            trainee = Trainee(
                                form_id=form_id,
                                name=trainee_data.get("name", trainee_data.get("email", "").split("@")[0]),
                                email=trainee_data.get("email", ""),
                                department=trainee_data.get("department", "Engineering")
                            )
                            session.add(trainee)
                    
                    session.flush()
                    migrated_count += 1
                    print(f"Migrated {len(trainees_json)} trainees for form {form_id}")
                    
                except Exception as e:
                    error_count += 1
                    logging.error(f"Error migrating trainees for form {form_id}: {e}")
                    session.rollback()
                    continue
        
        backup_conn.close()
        
    except Exception as e:
        logging.error(f"Error accessing backup database: {e}")
        create_sample_trainees()
        return
    
    print(f"\nMigration completed!")
    print(f"Successfully migrated: {migrated_count} forms")
    print(f"Errors: {error_count} forms")
    
    # Verify the migration
    with db_session() as session:
        total_trainees = session.query(Trainee).count()
        print(f"Total trainees in new table: {total_trainees}")

def create_sample_trainees():
    """Create sample trainee data for testing"""
    print("Creating sample trainee data for testing...")
    
    with db_session() as session:
        # Get a few forms to add sample trainees to
        forms = session.query(TrainingForm).limit(3).all()
        
        for i, form in enumerate(forms):
            # Check if trainees already exist
            existing_trainees = session.query(Trainee).filter_by(form_id=form.id).count()
            if existing_trainees > 0:
                continue
                
            # Add sample trainees
            sample_trainees = [
                {"name": f"John.Doe{i}", "email": f"john.doe{i}@company.com", "department": "Engineering"},
                {"name": f"Jane.Smith{i}", "email": f"jane.smith{i}@company.com", "department": "Quality"},
            ]
            
            for trainee_data in sample_trainees:
                trainee = Trainee(
                    form_id=form.id,
                    name=trainee_data["name"],
                    email=trainee_data["email"],
                    department=trainee_data["department"]
                )
                session.add(trainee)
            
            print(f"Added sample trainees for form {form.id}")
    
    print("Sample data creation completed!")

if __name__ == "__main__":
    migrate_trainees_from_backup() 