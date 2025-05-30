#!/usr/bin/env python3
"""
Database Schema Validator for Training Form Application

This script validates that database schema changes have corresponding migrations.
It helps catch cases where model changes were made but migrations weren't created.
"""

import os
import sys
import logging
import argparse
from datetime import datetime
import hashlib
import json

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import DATABASE_URL, USE_SQLITE, load_env_file
    from models import Base, TrainingForm, Trainee, TravelExpense, MaterialExpense, Attachment, Admin, TrainingCatalog
    from sqlalchemy import inspect, MetaData, create_engine
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this script from the application root directory")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SchemaValidator:
    def __init__(self):
        self.schema_hash_file = "scripts/migrations/schema_hash.json"
        self.migrations_dir = "scripts/migrations"
        
        # Ensure migrations directory exists
        os.makedirs(self.migrations_dir, exist_ok=True)
        
    def get_current_model_schema(self):
        """Generate a hash of the current SQLAlchemy model definitions"""
        # Get all model classes
        models = [
            TrainingForm,
            Trainee, 
            TravelExpense,
            MaterialExpense,
            Attachment,
            Admin,
            TrainingCatalog
        ]
        
        schema_info = {}
        
        for model in models:
            table_name = model.__tablename__
            columns = {}
            
            # Get column information
            for column_name, column in model.__table__.columns.items():
                column_info = {
                    'type': str(column.type),
                    'nullable': column.nullable,
                    'primary_key': column.primary_key,
                    'default': str(column.default) if column.default else None,
                }
                columns[column_name] = column_info
            
            # Get foreign key information
            foreign_keys = {}
            for fk in model.__table__.foreign_keys:
                foreign_keys[fk.parent.name] = {
                    'references': f"{fk.column.table.name}.{fk.column.name}",
                    'ondelete': fk.ondelete
                }
            
            # Get index information
            indexes = {}
            for index in model.__table__.indexes:
                indexes[index.name] = [col.name for col in index.columns]
            
            schema_info[table_name] = {
                'columns': columns,
                'foreign_keys': foreign_keys,
                'indexes': indexes
            }
        
        # Generate hash of schema information
        schema_json = json.dumps(schema_info, sort_keys=True)
        schema_hash = hashlib.sha256(schema_json.encode()).hexdigest()
        
        return schema_hash, schema_info
    
    def get_database_schema(self):
        """Get the actual database schema"""
        try:
            engine = create_engine(DATABASE_URL)
            inspector = inspect(engine)
            
            db_schema_info = {}
            
            # Get all tables
            table_names = inspector.get_table_names()
            
            for table_name in table_names:
                columns = {}
                
                # Get column information
                for column in inspector.get_columns(table_name):
                    column_info = {
                        'type': str(column['type']),
                        'nullable': column['nullable'],
                        'primary_key': column.get('primary_key', False),
                        'default': str(column['default']) if column.get('default') else None,
                    }
                    columns[column['name']] = column_info
                
                # Get foreign key information
                foreign_keys = {}
                for fk in inspector.get_foreign_keys(table_name):
                    for local_col, remote_col in zip(fk['constrained_columns'], fk['referred_columns']):
                        foreign_keys[local_col] = {
                            'references': f"{fk['referred_table']}.{remote_col}",
                            'ondelete': fk.get('options', {}).get('ondelete')
                        }
                
                # Get index information  
                indexes = {}
                for index in inspector.get_indexes(table_name):
                    if not index['unique']:  # Skip unique constraints
                        indexes[index['name']] = index['column_names']
                
                db_schema_info[table_name] = {
                    'columns': columns,
                    'foreign_keys': foreign_keys,
                    'indexes': indexes
                }
            
            # Generate hash of database schema
            schema_json = json.dumps(db_schema_info, sort_keys=True)
            schema_hash = hashlib.sha256(schema_json.encode()).hexdigest()
            
            return schema_hash, db_schema_info
            
        except Exception as e:
            logger.error(f"Error getting database schema: {e}")
            return None, None
    
    def get_stored_schema_hash(self):
        """Get the previously stored schema hash"""
        if os.path.exists(self.schema_hash_file):
            try:
                with open(self.schema_hash_file, 'r') as f:
                    data = json.load(f)
                    return data.get('model_hash'), data.get('db_hash'), data.get('last_updated')
            except Exception as e:
                logger.warning(f"Error reading schema hash file: {e}")
        
        return None, None, None
    
    def store_schema_hash(self, model_hash, db_hash):
        """Store the current schema hash"""
        data = {
            'model_hash': model_hash,
            'db_hash': db_hash,
            'last_updated': datetime.now().isoformat(),
            'environment': os.environ.get('FLASK_ENV', 'development')
        }
        
        try:
            with open(self.schema_hash_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Schema hash stored: {self.schema_hash_file}")
        except Exception as e:
            logger.error(f"Error storing schema hash: {e}")
    
    def check_for_pending_changes(self):
        """Check if there are pending schema changes that need migrations"""
        logger.info("Checking for pending database schema changes...")
        
        # Get current model schema
        current_model_hash, current_model_schema = self.get_current_model_schema()
        logger.info(f"Current model schema hash: {current_model_hash}")
        
        # Get database schema
        current_db_hash, current_db_schema = self.get_database_schema()
        if current_db_hash is None:
            logger.error("❌ Could not connect to database to check schema")
            return False
        
        logger.info(f"Current database schema hash: {current_db_hash}")
        
        # Get stored hashes
        stored_model_hash, stored_db_hash, last_updated = self.get_stored_schema_hash()
        
        if stored_model_hash is None:
            logger.info("ℹ️  No previous schema hash found - initializing")
            self.store_schema_hash(current_model_hash, current_db_hash)
            return True
        
        # Check if models have changed since last check
        if current_model_hash != stored_model_hash:
            logger.warning("⚠️  Model definitions have changed since last deployment!")
            logger.warning("This suggests you may have modified models without creating a migration.")
            
            # Check if database is in sync with models
            if current_model_hash != current_db_hash:
                logger.error("❌ SCHEMA MISMATCH DETECTED!")
                logger.error("Your model definitions don't match the database schema.")
                logger.error("This usually means:")
                logger.error("  1. You modified models.py but didn't create a migration")
                logger.error("  2. You didn't run migrations after modifying models") 
                logger.error("  3. There are pending migrations that haven't been applied")
                logger.error("")
                logger.error("To fix this:")
                logger.error("  1. Create a migration: scripts\\db_manager.cmd create describe_your_changes")
                logger.error("  2. Edit the migration file to include your schema changes")
                logger.error("  3. Test the migration locally")
                logger.error("  4. Commit and redeploy")
                return False
            else:
                logger.info("✅ Models and database are in sync")
                # Update stored hash since models changed but are in sync
                self.store_schema_hash(current_model_hash, current_db_hash)
                return True
        
        # Check if database has changed without models changing
        if current_db_hash != stored_db_hash:
            logger.info("ℹ️  Database schema has changed (likely due to migrations)")
            if current_model_hash == current_db_hash:
                logger.info("✅ Models and database are in sync after migration")
                self.store_schema_hash(current_model_hash, current_db_hash)
                return True
            else:
                logger.warning("⚠️  Database changed but doesn't match models")
                return False
        
        logger.info("✅ No schema changes detected")
        return True
    
    def compare_schemas(self, schema1, schema2, name1="Schema 1", name2="Schema 2"):
        """Compare two schemas and show differences"""
        differences = []
        
        # Check for table differences
        tables1 = set(schema1.keys())
        tables2 = set(schema2.keys())
        
        # Tables only in schema1
        for table in tables1 - tables2:
            differences.append(f"Table '{table}' exists in {name1} but not in {name2}")
        
        # Tables only in schema2  
        for table in tables2 - tables1:
            differences.append(f"Table '{table}' exists in {name2} but not in {name1}")
        
        # Compare common tables
        for table in tables1 & tables2:
            table1 = schema1[table]
            table2 = schema2[table]
            
            # Compare columns
            cols1 = set(table1['columns'].keys())
            cols2 = set(table2['columns'].keys())
            
            for col in cols1 - cols2:
                differences.append(f"Column '{table}.{col}' exists in {name1} but not in {name2}")
            
            for col in cols2 - cols1:
                differences.append(f"Column '{table}.{col}' exists in {name2} but not in {name1}")
            
            # Compare column properties
            for col in cols1 & cols2:
                col1 = table1['columns'][col]
                col2 = table2['columns'][col]
                
                if col1['type'] != col2['type']:
                    differences.append(f"Column '{table}.{col}' type differs: {name1}={col1['type']}, {name2}={col2['type']}")
                
                if col1['nullable'] != col2['nullable']:
                    differences.append(f"Column '{table}.{col}' nullable differs: {name1}={col1['nullable']}, {name2}={col2['nullable']}")
        
        return differences
    
    def validate_deployment_readiness(self):
        """Comprehensive validation for deployment readiness"""
        logger.info("🔍 Validating deployment readiness...")
        
        issues = []
        
        # Check for pending schema changes
        if not self.check_for_pending_changes():
            issues.append("Schema validation failed - see errors above")
        
        # Check migration version consistency
        try:
            from scripts.migrate_database import DatabaseMigration
            migrator = DatabaseMigration()
            current_version = migrator.get_current_version()
            logger.info(f"Current migration version: {current_version}")
            
            if current_version == 0:
                logger.warning("⚠️  No migrations have been applied")
                logger.warning("This might be expected for a fresh database")
        except Exception as e:
            issues.append(f"Could not check migration status: {e}")
        
        # Final assessment
        if issues:
            logger.error("❌ Deployment readiness check FAILED")
            for issue in issues:
                logger.error(f"  - {issue}")
            return False
        else:
            logger.info("✅ Deployment readiness check PASSED")
            return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Database Schema Validator')
    parser.add_argument('--check-changes', action='store_true', 
                       help='Check for pending schema changes')
    parser.add_argument('--validate-deployment', action='store_true',
                       help='Validate deployment readiness')
    parser.add_argument('--update-hash', action='store_true',
                       help='Update stored schema hash')
    
    args = parser.parse_args()
    
    # Load environment configuration
    try:
        load_env_file()
    except:
        pass
    
    validator = SchemaValidator()
    
    if args.check_changes:
        success = validator.check_for_pending_changes()
        sys.exit(0 if success else 1)
    
    elif args.validate_deployment:
        success = validator.validate_deployment_readiness()
        sys.exit(0 if success else 1)
    
    elif args.update_hash:
        model_hash, _ = validator.get_current_model_schema()
        db_hash, _ = validator.get_database_schema()
        if db_hash:
            validator.store_schema_hash(model_hash, db_hash)
            logger.info("✅ Schema hash updated")
        else:
            logger.error("❌ Could not update schema hash")
            sys.exit(1)
    
    else:
        # Default: check for changes
        success = validator.check_for_pending_changes()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 