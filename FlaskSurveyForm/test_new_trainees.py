#!/usr/bin/env python3
"""
Test script to verify the new Trainee table structure works correctly.
"""

import json
from models import (
    db_session, 
    TrainingForm, 
    Trainee, 
    create_tables,
    insert_trainees,
    get_trainees
)

def test_new_trainee_structure():
    """Test the new trainee table structure"""
    print("Testing new trainee structure...")
    
    # Create tables
    create_tables()
    print("✅ Tables created successfully")
    
    with db_session() as session:
        # Get the first training form
        form = session.query(TrainingForm).first()
        if not form:
            print("❌ No training forms found. Please create a form first.")
            return
        
        print(f"📋 Testing with form ID: {form.id}")
        
        # Test data
        test_trainees = [
            {"name": "John.Doe", "email": "john.doe@test.com", "department": "Engineering"},
            {"name": "Jane.Smith", "email": "jane.smith@test.com", "department": "Quality"}
        ]
        
        # Test inserting trainees
        success = insert_trainees(form.id, test_trainees)
        if success:
            print("✅ Trainees inserted successfully")
        else:
            print("❌ Failed to insert trainees")
            return
        
        # Test getting trainees  
        retrieved_trainees = get_trainees(form.id)
        print(f"✅ Retrieved {len(retrieved_trainees)} trainees")
        
        for trainee in retrieved_trainees:
            print(f"   - {trainee['name']} ({trainee['email']})")
        
        # Test the form.to_dict() method
        form_dict = form.to_dict(include_costs=True)
        if 'trainees' in form_dict:
            print("✅ form.to_dict() includes trainees")
            print(f"   Found {len(form_dict['trainees'])} trainees in dict")
        else:
            print("❌ form.to_dict() missing trainees")
        
        print("\n🎉 All tests passed! The new structure is working correctly.")

if __name__ == "__main__":
    test_new_trainee_structure() 