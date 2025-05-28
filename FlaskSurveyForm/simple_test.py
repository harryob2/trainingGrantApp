#!/usr/bin/env python3
"""
Simple test to verify course cost validation logic.
"""

class MockField:
    def __init__(self, data):
        self.data = data

class MockForm:
    def __init__(self, training_type, course_cost):
        self.training_type = MockField(training_type)
        self.course_cost = MockField(course_cost)

def validate_course_cost(form, field):
    """Replicate the validate_course_cost method logic."""
    if form.training_type.data == "External Training":
        if field.data is None or str(field.data).strip() == "" or field.data < 0:
            raise ValueError("Course Cost is required for external training and cannot be negative.")
    # For Internal Training, ensure the field has a valid default value
    elif form.training_type.data == "Internal Training":
        if field.data is None or str(field.data).strip() == "":
            field.data = 0

def test_course_cost_validation():
    print("Testing course cost validation logic...")
    
    # Test 1: Internal Training with None
    print("\n1. Internal Training with None course cost:")
    form = MockForm("Internal Training", None)
    try:
        validate_course_cost(form, form.course_cost)
        print(f"   ✓ Passed - Course cost set to: {form.course_cost.data}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test 2: Internal Training with empty string
    print("\n2. Internal Training with empty string course cost:")
    form = MockForm("Internal Training", "")
    try:
        validate_course_cost(form, form.course_cost)
        print(f"   ✓ Passed - Course cost set to: {form.course_cost.data}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test 3: Internal Training with valid value
    print("\n3. Internal Training with valid course cost:")
    form = MockForm("Internal Training", 50.0)
    try:
        validate_course_cost(form, form.course_cost)
        print(f"   ✓ Passed - Course cost remains: {form.course_cost.data}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Test 4: External Training with None (should fail)
    print("\n4. External Training with None course cost:")
    form = MockForm("External Training", None)
    try:
        validate_course_cost(form, form.course_cost)
        print(f"   ✗ Should have failed but passed")
    except Exception as e:
        print(f"   ✓ Correctly failed: {e}")
    
    # Test 5: External Training with empty string (should fail)
    print("\n5. External Training with empty string course cost:")
    form = MockForm("External Training", "")
    try:
        validate_course_cost(form, form.course_cost)
        print(f"   ✗ Should have failed but passed")
    except Exception as e:
        print(f"   ✓ Correctly failed: {e}")
    
    # Test 6: External Training with valid value (should pass)
    print("\n6. External Training with valid course cost:")
    form = MockForm("External Training", 100.0)
    try:
        validate_course_cost(form, form.course_cost)
        print(f"   ✓ Passed - Course cost: {form.course_cost.data}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")

if __name__ == "__main__":
    test_course_cost_validation()
    print("\nTest completed!") 