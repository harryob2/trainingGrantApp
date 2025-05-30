#!/usr/bin/env python3
"""
Database Migration System for Training Form Application

This script handles database schema changes and migrations for both
SQLite (development) and MariaDB (production) environments.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import DATABASE_URL, USE_SQLITE, load_env_file
    from models import engine, db_session, Base
    from sqlalchemy import inspect, text, Column, Integer, String, Float, Date, Text, Boolean, ForeignKey, DateTime
    from sqlalchemy.sql import func
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this script from the application root directory")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseMigration:
    def __init__(self):
        self.migrations_dir = Path(__file__).parent / "migrations"
        self.migrations_dir.mkdir(exist_ok=True)
        self.version_file = self.migrations_dir / "version.json"
        self.engine = engine
        self.inspector = inspect(self.engine)
        
    def get_current_version(self):
        """Get the current database version"""
        if self.version_file.exists():
            with open(self.version_file, 'r') as f:
                data = json.load(f)
                return data.get('version', 0)
        return 0
    
    def set_current_version(self, version):
        """Set the current database version"""
        data = {
            'version': version,
            'last_migration': datetime.now().isoformat(),
            'database_type': 'sqlite' if USE_SQLITE else 'mariadb',
            'database_url': DATABASE_URL.replace(DATABASE_URL.split('@')[0].split('//')[-1].split(':')[-1], '***') if '@' in DATABASE_URL else DATABASE_URL
        }
        with open(self.version_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def table_exists(self, table_name):
        """Check if a table exists in the database"""
        return table_name in self.inspector.get_table_names()
    
    def column_exists(self, table_name, column_name):
        """Check if a column exists in a table"""
        if not self.table_exists(table_name):
            return False
        columns = [col['name'] for col in self.inspector.get_columns(table_name)]
        return column_name in columns
    
    def add_column_if_not_exists(self, table_name, column_name, column_definition):
        """Add a column to a table if it doesn't exist"""
        if not self.column_exists(table_name, column_name):
            try:
                with self.engine.connect() as conn:
                    if USE_SQLITE:
                        # SQLite syntax
                        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
                    else:
                        # MariaDB/MySQL syntax
                        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
                    
                    conn.execute(text(sql))
                    conn.commit()
                    logger.info(f"✅ Added column {column_name} to table {table_name}")
                    return True
            except Exception as e:
                logger.error(f"❌ Error adding column {column_name} to {table_name}: {e}")
                return False
        else:
            logger.info(f"ℹ️  Column {column_name} already exists in table {table_name}")
            return True
    
    def create_table_if_not_exists(self, table_name, create_sql):
        """Create a table if it doesn't exist"""
        if not self.table_exists(table_name):
            try:
                with self.engine.connect() as conn:
                    conn.execute(text(create_sql))
                    conn.commit()
                    logger.info(f"✅ Created table {table_name}")
                    return True
            except Exception as e:
                logger.error(f"❌ Error creating table {table_name}: {e}")
                return False
        else:
            logger.info(f"ℹ️  Table {table_name} already exists")
            return True
    
    def add_index_if_not_exists(self, index_name, table_name, columns):
        """Add an index if it doesn't exist"""
        try:
            indexes = self.inspector.get_indexes(table_name)
            existing_index_names = [idx['name'] for idx in indexes]
            
            if index_name not in existing_index_names:
                with self.engine.connect() as conn:
                    columns_str = ', '.join(columns)
                    sql = f"CREATE INDEX {index_name} ON {table_name} ({columns_str})"
                    conn.execute(text(sql))
                    conn.commit()
                    logger.info(f"✅ Created index {index_name} on {table_name}")
                    return True
            else:
                logger.info(f"ℹ️  Index {index_name} already exists")
                return True
        except Exception as e:
            logger.error(f"❌ Error creating index {index_name}: {e}")
            return False
    
    def migration_001_add_enhanced_fields(self):
        """Migration 001: Add enhanced fields to training_forms table"""
        logger.info("Running Migration 001: Add enhanced fields to training_forms")
        
        success = True
        
        # Add new columns to training_forms table
        new_columns = [
            ('training_name', 'VARCHAR(255) NOT NULL DEFAULT ""'),
            ('trainer_email', 'VARCHAR(255)'),
            ('invoice_number', 'VARCHAR(255)'),
            ('ida_class', 'VARCHAR(255)'),
            ('created_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP' if not USE_SQLITE else 'DATETIME DEFAULT (datetime("now"))'),
        ]
        
        for column_name, column_def in new_columns:
            if not self.add_column_if_not_exists('training_forms', column_name, column_def):
                success = False
        
        # Add indexes for better performance
        indexes = [
            ('idx_training_forms_training_name', 'training_forms', ['training_name']),
            ('idx_training_forms_trainer_email', 'training_forms', ['trainer_email']),
            ('idx_training_forms_invoice_number', 'training_forms', ['invoice_number']),
            ('idx_training_forms_ida_class', 'training_forms', ['ida_class']),
        ]
        
        for index_name, table_name, columns in indexes:
            if not self.add_index_if_not_exists(index_name, table_name, columns):
                success = False
        
        return success
    
    def migration_002_create_trainees_table(self):
        """Migration 002: Create trainees table"""
        logger.info("Running Migration 002: Create trainees table")
        
        if USE_SQLITE:
            create_sql = """
            CREATE TABLE IF NOT EXISTS trainees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                form_id INTEGER NOT NULL,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                department VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT (datetime("now")),
                FOREIGN KEY (form_id) REFERENCES training_forms(id) ON DELETE CASCADE
            )
            """
        else:
            create_sql = """
            CREATE TABLE IF NOT EXISTS trainees (
                id INT AUTO_INCREMENT PRIMARY KEY,
                form_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                department VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (form_id) REFERENCES training_forms(id) ON DELETE CASCADE
            )
            """
        
        success = self.create_table_if_not_exists('trainees', create_sql)
        
        # Add indexes
        indexes = [
            ('idx_trainees_form_id', 'trainees', ['form_id']),
            ('idx_trainees_email', 'trainees', ['email']),
            ('idx_trainees_department', 'trainees', ['department']),
        ]
        
        for index_name, table_name, columns in indexes:
            if not self.add_index_if_not_exists(index_name, table_name, columns):
                success = False
        
        return success
    
    def migration_003_create_travel_expenses_table(self):
        """Migration 003: Create travel_expenses table"""
        logger.info("Running Migration 003: Create travel_expenses table")
        
        if USE_SQLITE:
            create_sql = """
            CREATE TABLE IF NOT EXISTS travel_expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                form_id INTEGER NOT NULL,
                travel_date DATE NOT NULL,
                destination VARCHAR(255) NOT NULL,
                traveler_type VARCHAR(255) NOT NULL,
                traveler_email VARCHAR(255) NOT NULL,
                traveler_name VARCHAR(255) NOT NULL,
                travel_mode VARCHAR(255) NOT NULL,
                cost FLOAT,
                distance_km FLOAT,
                created_at DATETIME DEFAULT (datetime("now")),
                FOREIGN KEY (form_id) REFERENCES training_forms(id) ON DELETE CASCADE
            )
            """
        else:
            create_sql = """
            CREATE TABLE IF NOT EXISTS travel_expenses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                form_id INT NOT NULL,
                travel_date DATE NOT NULL,
                destination VARCHAR(255) NOT NULL,
                traveler_type VARCHAR(255) NOT NULL,
                traveler_email VARCHAR(255) NOT NULL,
                traveler_name VARCHAR(255) NOT NULL,
                travel_mode VARCHAR(255) NOT NULL,
                cost DECIMAL(10,2),
                distance_km DECIMAL(10,2),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (form_id) REFERENCES training_forms(id) ON DELETE CASCADE
            )
            """
        
        success = self.create_table_if_not_exists('travel_expenses', create_sql)
        
        # Add indexes
        indexes = [
            ('idx_travel_expenses_form_id', 'travel_expenses', ['form_id']),
            ('idx_travel_expenses_travel_date', 'travel_expenses', ['travel_date']),
            ('idx_travel_expenses_traveler_email', 'travel_expenses', ['traveler_email']),
        ]
        
        for index_name, table_name, columns in indexes:
            if not self.add_index_if_not_exists(index_name, table_name, columns):
                success = False
        
        return success
    
    def migration_004_create_material_expenses_table(self):
        """Migration 004: Create material_expenses table"""
        logger.info("Running Migration 004: Create material_expenses table")
        
        if USE_SQLITE:
            create_sql = """
            CREATE TABLE IF NOT EXISTS material_expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                form_id INTEGER NOT NULL,
                purchase_date DATE NOT NULL,
                supplier_name VARCHAR(255) NOT NULL,
                invoice_number VARCHAR(255) NOT NULL,
                material_cost FLOAT NOT NULL,
                created_at DATETIME DEFAULT (datetime("now")),
                FOREIGN KEY (form_id) REFERENCES training_forms(id) ON DELETE CASCADE
            )
            """
        else:
            create_sql = """
            CREATE TABLE IF NOT EXISTS material_expenses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                form_id INT NOT NULL,
                purchase_date DATE NOT NULL,
                supplier_name VARCHAR(255) NOT NULL,
                invoice_number VARCHAR(255) NOT NULL,
                material_cost DECIMAL(10,2) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (form_id) REFERENCES training_forms(id) ON DELETE CASCADE
            )
            """
        
        success = self.create_table_if_not_exists('material_expenses', create_sql)
        
        # Add indexes
        indexes = [
            ('idx_material_expenses_form_id', 'material_expenses', ['form_id']),
            ('idx_material_expenses_purchase_date', 'material_expenses', ['purchase_date']),
        ]
        
        for index_name, table_name, columns in indexes:
            if not self.add_index_if_not_exists(index_name, table_name, columns):
                success = False
        
        return success
    
    def migration_005_enhance_training_catalog(self):
        """Migration 005: Enhance training_catalog table"""
        logger.info("Running Migration 005: Enhance training_catalog table")
        
        success = True
        
        # Add new columns to training_catalog table
        new_columns = [
            ('training_hours', 'FLOAT DEFAULT 0'),
            ('course_cost', 'FLOAT DEFAULT 0' if USE_SQLITE else 'DECIMAL(10,2) DEFAULT 0'),
        ]
        
        for column_name, column_def in new_columns:
            if not self.add_column_if_not_exists('training_catalog', column_name, column_def):
                success = False
        
        # Add indexes
        indexes = [
            ('idx_training_catalog_training_name', 'training_catalog', ['training_name']),
            ('idx_training_catalog_area', 'training_catalog', ['area']),
            ('idx_training_catalog_training_type', 'training_catalog', ['training_type']),
        ]
        
        for index_name, table_name, columns in indexes:
            if not self.add_index_if_not_exists(index_name, table_name, columns):
                success = False
        
        return success
    
    def run_migrations(self):
        """Run all pending migrations"""
        current_version = self.get_current_version()
        logger.info(f"Current database version: {current_version}")
        logger.info(f"Database type: {'SQLite' if USE_SQLITE else 'MariaDB'}")
        logger.info(f"Database URL: {DATABASE_URL.replace(DATABASE_URL.split('@')[0].split('//')[-1].split(':')[-1], '***') if '@' in DATABASE_URL else DATABASE_URL}")
        
        # Define all migrations in order
        migrations = [
            (1, self.migration_001_add_enhanced_fields),
            (2, self.migration_002_create_trainees_table),
            (3, self.migration_003_create_travel_expenses_table),
            (4, self.migration_004_create_material_expenses_table),
            (5, self.migration_005_enhance_training_catalog),
        ]
        
        # Run migrations that haven't been applied yet
        for version, migration_func in migrations:
            if current_version < version:
                logger.info(f"🔄 Applying migration {version}...")
                try:
                    if migration_func():
                        self.set_current_version(version)
                        logger.info(f"✅ Migration {version} completed successfully")
                    else:
                        logger.error(f"❌ Migration {version} failed")
                        return False
                except Exception as e:
                    logger.error(f"❌ Migration {version} failed with error: {e}")
                    return False
            else:
                logger.info(f"⏭️  Migration {version} already applied")
        
        logger.info("🎉 All migrations completed successfully!")
        return True
    
    def create_migration_template(self, migration_name):
        """Create a new migration template file"""
        current_version = self.get_current_version()
        new_version = current_version + 1
        
        template = f'''def migration_{new_version:03d}_{migration_name}(self):
    """Migration {new_version:03d}: {migration_name.replace('_', ' ').title()}"""
    logger.info("Running Migration {new_version:03d}: {migration_name.replace('_', ' ').title()}")
    
    success = True
    
    # Add your migration logic here
    # Example: Add a new column
    # if not self.add_column_if_not_exists('table_name', 'column_name', 'VARCHAR(255)'):
    #     success = False
    
    # Example: Create a new table
    # create_sql = """
    # CREATE TABLE IF NOT EXISTS new_table (
    #     id INTEGER PRIMARY KEY AUTOINCREMENT,
    #     name VARCHAR(255) NOT NULL
    # )
    # """
    # if not self.create_table_if_not_exists('new_table', create_sql):
    #     success = False
    
    return success
'''
        
        migration_file = self.migrations_dir / f"migration_{new_version:03d}_{migration_name}.py"
        with open(migration_file, 'w') as f:
            f.write(template)
        
        logger.info(f"Created migration template: {migration_file}")
        return migration_file

def main():
    """Main migration runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Migration Tool')
    parser.add_argument('--create', type=str, help='Create a new migration template')
    parser.add_argument('--force-version', type=int, help='Force set the current version')
    parser.add_argument('--status', action='store_true', help='Show migration status')
    
    args = parser.parse_args()
    
    # Load environment configuration
    try:
        load_env_file()
    except:
        pass
    
    migrator = DatabaseMigration()
    
    if args.create:
        migrator.create_migration_template(args.create)
    elif args.force_version is not None:
        migrator.set_current_version(args.force_version)
        logger.info(f"Forced version to {args.force_version}")
    elif args.status:
        current_version = migrator.get_current_version()
        logger.info(f"Current database version: {current_version}")
        logger.info(f"Database type: {'SQLite' if USE_SQLITE else 'MariaDB'}")
        logger.info(f"Database URL: {DATABASE_URL}")
    else:
        # Run all pending migrations
        migrator.run_migrations()

if __name__ == "__main__":
    main() 