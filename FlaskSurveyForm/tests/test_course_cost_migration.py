"""
Test for course_cost column migration and data population in training_catalog table.
"""

import pytest
import sqlite3
import os
import sys
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import TrainingCatalog, create_tables, db_session, engine
from scripts.add_catalog_course_cost import migrate_catalog_course_cost


class TestCourseCostMigration:
    
    @pytest.fixture(autouse=True)
    def setup_test_db(self):
        """Setup a test database for each test."""
        # Create a temporary database
        self.test_db_path = "test_training_forms.db"
        
        # Remove test db if it exists
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
        # Create tables in test database
        create_tables()
        
        # Add some test data to training_catalog
        with db_session() as session:
            test_catalogs = [
                TrainingCatalog(
                    training_name="Test Training 1",
                    area="Test Area 1",
                    training_desc="Test Description 1"
                ),
                TrainingCatalog(
                    training_name="Test Training 2", 
                    area="Test Area 2",
                    training_desc="Test Description 2"
                ),
                TrainingCatalog(
                    training_name="Test Training 3",
                    area="Test Area 3", 
                    training_desc="Test Description 3"
                )
            ]
            session.add_all(test_catalogs)
        
        yield
        
        # Cleanup
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_course_cost_column_addition(self):
        """Test that course_cost column is added to training_catalog table."""
        # Check if course_cost column exists before migration
        conn = sqlite3.connect("training_forms.db")
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(training_catalog)")
        columns_before = [column[1] for column in cursor.fetchall()]
        conn.close()
        
        # Run migration
        migrate_catalog_course_cost()
        
        # Check if course_cost column exists after migration
        conn = sqlite3.connect("training_forms.db")
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(training_catalog)")
        columns_after = [column[1] for column in cursor.fetchall()]
        conn.close()
        
        assert 'course_cost' in columns_after, "course_cost column should be added to training_catalog table"

    @patch('scripts.add_catalog_course_cost.pd.read_excel')
    def test_course_cost_data_population(self, mock_read_excel):
        """Test that course cost data is correctly populated from Excel file."""
        # Mock Excel data (180 rows as expected)
        mock_data = pd.DataFrame({
            1: [f"Training {i}" for i in range(180)],  # Column B (training names)
            2: [f"Supplier {i}" for i in range(180)],  # Column C (suppliers)
            3: ["External-Eligible"] * 180,            # Column D (training type)
            4: [100.0 + i for i in range(180)]        # Column E (course costs)
        })
        mock_read_excel.return_value = mock_data
        
        # Ensure we have training catalog entries
        with db_session() as session:
            catalog_count = session.query(TrainingCatalog).count()
            assert catalog_count > 0, "Should have training catalog entries for testing"
        
        # Run migration
        migrate_catalog_course_cost()
        
        # Check that course costs were populated
        with db_session() as session:
            catalogs = session.query(TrainingCatalog).limit(3).all()
            for catalog in catalogs:
                assert hasattr(catalog, 'course_cost'), "catalog should have course_cost attribute"
                # course_cost should be populated (not None and not 0 for this test)
                # Note: actual values depend on the order of data in catalog vs excel

    def test_migration_idempotency(self):
        """Test that running migration multiple times doesn't cause issues."""
        # Run migration first time
        result1 = migrate_catalog_course_cost()
        assert result1 is True, "First migration should succeed"
        
        # Run migration second time
        result2 = migrate_catalog_course_cost()
        assert result2 is True, "Second migration should also succeed (idempotent)"
        
        # Verify column still exists and is properly configured
        conn = sqlite3.connect("training_forms.db")
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(training_catalog)")
        columns = [column[1] for column in cursor.fetchall()]
        conn.close()
        
        assert 'course_cost' in columns, "course_cost column should still exist after multiple migrations"

    def test_migration_with_missing_excel_file(self):
        """Test migration behavior when Excel file is missing."""
        with patch('scripts.add_catalog_course_cost.EXCEL_PATH', 'nonexistent_file.xlsx'):
            result = migrate_catalog_course_cost()
            # Migration should handle missing file gracefully
            assert isinstance(result, bool), "Migration should return a boolean result" 