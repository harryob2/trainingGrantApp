#!/usr/bin/env python3
"""
Flask-Migrate Integration Helper for Training Form Application

This script provides Flask-Migrate integration to automatically detect
schema changes and create migrations when needed.
"""

import os
import sys
import logging
import argparse
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from flask import Flask
    from flask_migrate import Migrate, init as migrate_init, migrate as create_migration, upgrade as run_upgrade
    from config import load_env_file
    from models import db, Base
    import subprocess
    import tempfile
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you have installed all requirements: pip install -r requirements.txt")
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FlaskMigrateHelper:
    def __init__(self):
        self.migrations_dir = "migrations"
        self.app = None
        self.migrate = None
        self.setup_flask_app()
    
    def setup_flask_app(self):
        """Set up Flask app for migrations"""
        try:
            # Load environment configuration
            load_env_file()
        except:
            pass
        
        # Create Flask app
        self.app = Flask(__name__)
        
        # Configure the app
        from config import DATABASE_URL, SECRET_KEY
        self.app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['SECRET_KEY'] = SECRET_KEY
        
        # Initialize SQLAlchemy with app
        db.init_app(self.app)
        
        # Initialize Flask-Migrate
        self.migrate = Migrate(self.app, db, directory=self.migrations_dir)
        
        logger.info(f"Flask app configured with database: {DATABASE_URL}")
    
    def init_migrations(self):
        """Initialize migrations directory"""
        if os.path.exists(self.migrations_dir):
            logger.info(f"Migrations directory already exists: {self.migrations_dir}")
            return True
        
        try:
            with self.app.app_context():
                migrate_init(directory=self.migrations_dir)
            logger.info(f"✅ Migrations directory initialized: {self.migrations_dir}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize migrations: {e}")
            return False
    
    def detect_schema_changes(self):
        """Detect if there are pending schema changes"""
        try:
            with self.app.app_context():
                # Create a temporary migration to see if there are changes
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_migration_file = os.path.join(temp_dir, "temp_migration.py")
                    
                    # Try to create a migration (dry run)
                    result = subprocess.run([
                        sys.executable, "-c",
                        f"""
import os
import sys
sys.path.append('{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}')
from flask_migrate import migrate
from scripts.flask_migrate_helper import FlaskMigrateHelper
helper = FlaskMigrateHelper()
with helper.app.app_context():
    from flask_migrate.cli import db as migrate_cli
    import tempfile
    import io
    import contextlib
    
    # Capture output to check if changes detected
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            migrate(message='temp_check', directory='{self.migrations_dir}')
        output_text = output.getvalue()
        if 'No changes in schema detected' in output_text:
            print('NO_CHANGES')
        else:
            print('CHANGES_DETECTED')
    except Exception as e:
        print(f'ERROR: {{e}}')
"""
                    ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    
                    if result.returncode == 0:
                        output = result.stdout.strip()
                        if "NO_CHANGES" in output:
                            logger.info("✅ No schema changes detected")
                            return False
                        elif "CHANGES_DETECTED" in output:
                            logger.warning("⚠️ Schema changes detected!")
                            return True
                        else:
                            logger.warning(f"Unexpected output: {output}")
                            return True  # Assume changes to be safe
                    else:
                        logger.error(f"Error checking for changes: {result.stderr}")
                        return True  # Assume changes to be safe
                        
        except Exception as e:
            logger.error(f"Error detecting schema changes: {e}")
            return True  # Assume changes to be safe
    
    def create_migration(self, message="Auto-generated migration"):
        """Create a new migration"""
        try:
            with self.app.app_context():
                # Check if migrations directory exists
                if not os.path.exists(self.migrations_dir):
                    logger.info("Migrations directory not found, initializing...")
                    if not self.init_migrations():
                        return False
                
                # Create the migration
                result = subprocess.run([
                    sys.executable, "-c",
                    f"""
import os
import sys
sys.path.append('{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}')
from scripts.flask_migrate_helper import FlaskMigrateHelper
helper = FlaskMigrateHelper()
with helper.app.app_context():
    from flask_migrate import migrate
    migrate(message='{message}', directory='{self.migrations_dir}')
"""
                ], cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                
                if result.returncode == 0:
                    logger.info(f"✅ Migration created successfully: {message}")
                    return True
                else:
                    logger.error(f"❌ Failed to create migration")
                    return False
                    
        except Exception as e:
            logger.error(f"Error creating migration: {e}")
            return False
    
    def run_migrations(self):
        """Run pending migrations"""
        try:
            with self.app.app_context():
                result = subprocess.run([
                    sys.executable, "-c",
                    f"""
import os
import sys
sys.path.append('{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}')
from scripts.flask_migrate_helper import FlaskMigrateHelper
helper = FlaskMigrateHelper()
with helper.app.app_context():
    from flask_migrate import upgrade
    upgrade(directory='{self.migrations_dir}')
"""
                ], cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                
                if result.returncode == 0:
                    logger.info("✅ Migrations applied successfully")
                    return True
                else:
                    logger.error("❌ Failed to apply migrations")
                    return False
                    
        except Exception as e:
            logger.error(f"Error running migrations: {e}")
            return False
    
    def get_migration_status(self):
        """Get current migration status"""
        try:
            with self.app.app_context():
                result = subprocess.run([
                    sys.executable, "-c",
                    f"""
import os
import sys
sys.path.append('{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}')
from scripts.flask_migrate_helper import FlaskMigrateHelper
helper = FlaskMigrateHelper()
with helper.app.app_context():
    from flask_migrate import current, heads
    current_rev = current(directory='{self.migrations_dir}')
    head_rev = heads(directory='{self.migrations_dir}')
    print(f'Current: {{current_rev}}')
    print(f'Head: {{head_rev}}')
"""
                ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                
                if result.returncode == 0:
                    output_lines = result.stdout.strip().split('\n')
                    current_rev = output_lines[0].replace('Current: ', '') if len(output_lines) > 0 else None
                    head_rev = output_lines[1].replace('Head: ', '') if len(output_lines) > 1 else None
                    
                    logger.info(f"Current revision: {current_rev}")
                    logger.info(f"Head revision: {head_rev}")
                    
                    if current_rev == head_rev:
                        logger.info("✅ Database is up to date")
                        return True
                    else:
                        logger.warning("⚠️ Database is not up to date")
                        return False
                else:
                    logger.error(f"Error getting migration status: {result.stderr}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error getting migration status: {e}")
            return False
    
    def validate_deployment_readiness(self):
        """Check if deployment is ready"""
        logger.info("🔍 Checking deployment readiness...")
        
        issues = []
        
        # Check if migrations directory exists
        if not os.path.exists(self.migrations_dir):
            logger.warning("⚠️ Migrations directory not found")
            logger.info("Initializing migrations...")
            if not self.init_migrations():
                issues.append("Failed to initialize migrations")
        
        # Check for schema changes
        if self.detect_schema_changes():
            issues.append("Schema changes detected but no migration created")
            logger.error("❌ You have model changes that need a migration!")
            logger.error("Run the following commands:")
            logger.error("  1. python scripts/flask_migrate_helper.py --create-migration 'Describe your changes'")
            logger.error("  2. Review the generated migration file")
            logger.error("  3. Test the migration locally")
            logger.error("  4. Commit the migration file and redeploy")
        
        # Check migration status
        if not self.get_migration_status():
            issues.append("Database migration status check failed")
        
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
    parser = argparse.ArgumentParser(description='Flask-Migrate Helper')
    parser.add_argument('--init', action='store_true', 
                       help='Initialize migrations directory')
    parser.add_argument('--detect-changes', action='store_true',
                       help='Detect pending schema changes')
    parser.add_argument('--create-migration', metavar='MESSAGE',
                       help='Create a new migration with the given message')
    parser.add_argument('--run-migrations', action='store_true',
                       help='Run pending migrations')
    parser.add_argument('--status', action='store_true',
                       help='Show migration status')
    parser.add_argument('--validate-deployment', action='store_true',
                       help='Validate deployment readiness')
    
    args = parser.parse_args()
    
    helper = FlaskMigrateHelper()
    
    if args.init:
        success = helper.init_migrations()
        sys.exit(0 if success else 1)
    
    elif args.detect_changes:
        changes_detected = helper.detect_schema_changes()
        if changes_detected:
            logger.warning("Schema changes detected!")
            sys.exit(1)  # Exit with error to fail CI/CD
        else:
            logger.info("No schema changes detected")
            sys.exit(0)
    
    elif args.create_migration:
        success = helper.create_migration(args.create_migration)
        sys.exit(0 if success else 1)
    
    elif args.run_migrations:
        success = helper.run_migrations()
        sys.exit(0 if success else 1)
    
    elif args.status:
        success = helper.get_migration_status()
        sys.exit(0 if success else 1)
    
    elif args.validate_deployment:
        success = helper.validate_deployment_readiness()
        sys.exit(0 if success else 1)
    
    else:
        # Default: validate deployment
        success = helper.validate_deployment_readiness()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 