#!/usr/bin/env python3
"""
Test script to verify course cost validation fix for internal training.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from forms import TrainingForm
from datetime import date

def test_internal_training_course_cost():
    """Test that internal training doesn't require course cost."""
    
    with app.app_context():
        # Create a form instance
        form = TrainingForm()
        
        # Set up form data for internal training
        form.training_type.data = "Internal Training"
        form.trainer_name.data = "Test Trainer"
        form.location_type.data = "Onsite"
        form.start_date.data = date.today()
        form.end_date.data = date.today()
        form.training_hours.data = 2.0
        form.training_description.data = "Test training description"
        form.ida_class.data = "Class A - QQI Certified L1-10"
        form.trainees_data.data = '[{"email": "test@example.com", "name": "Test User"}]'
        
        # Course cost should be optional for internal training
        form.course_cost.data = None  # This should not cause validation error
        
        # Test validation
        print("Testing internal training validation...")
        print(f"Training type: {form.training_type.data}")
        print(f"Course cost: {form.course_cost.data}")
        
        # Manually run the course cost validation
        try:
            form.validate_course_cost(form.course_cost)
            print("✓ Course cost validation passed for internal training")
        except Exception as e:
            print(f"✗ Course cost validation failed: {e}")
        
        # Test the DynamicRequiredIf validator
        from forms import DynamicRequiredIf
        validator = DynamicRequiredIf("training_type", "External Training")
        
        try:
            validator(form, form.course_cost)
            print("✓ DynamicRequiredIf validation passed for internal training")
        except Exception as e:
            print(f"✗ DynamicRequiredIf validation failed: {e}")
        
        # Test with empty string (common issue)
        form.course_cost.data = ""
        try:
            form.validate_course_cost(form.course_cost)
            print("✓ Course cost validation passed with empty string for internal training")
        except Exception as e:
            print(f"✗ Course cost validation failed with empty string: {e}")

def test_external_training_course_cost():
    """Test that external training requires course cost."""
    
    with app.app_context():
        # Create a form instance
        form = TrainingForm()
        
        # Set up form data for external training
        form.training_type.data = "External Training"
        form.supplier_name.data = "Test Supplier"
        form.location_type.data = "Onsite"
        form.start_date.data = date.today()
        form.end_date.data = date.today()
        form.training_hours.data = 2.0
        form.training_description.data = "Test training description"
        form.ida_class.data = "Class A - QQI Certified L1-10"
        form.trainees_data.data = '[{"email": "test@example.com", "name": "Test User"}]'
        
        print("\nTesting external training validation...")
        print(f"Training type: {form.training_type.data}")
        
        # Test without course cost (should fail)
        form.course_cost.data = None
        try:
            form.validate_course_cost(form.course_cost)
            print("✗ Course cost validation should have failed for external training without cost")
        except Exception as e:
            print(f"✓ Course cost validation correctly failed: {e}")
        
        # Test with valid course cost (should pass)
        form.course_cost.data = 100.0
        try:
            form.validate_course_cost(form.course_cost)
            print("✓ Course cost validation passed for external training with valid cost")
        except Exception as e:
            print(f"✗ Course cost validation failed unexpectedly: {e}")

if __name__ == "__main__":
    print("Testing course cost validation fixes...")
    test_internal_training_course_cost()
    test_external_training_course_cost()
    print("\nTest completed!") 