#!/usr/bin/env python
"""
Simple daily maintenance for Training Form Application
- Database backup
- Permanent deletion of soft-deleted records older than 180 days
"""

import os
import sys
import shutil
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    # dotenv not available, continue without it
    pass

# Configure file logging
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "maintenance.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)  # Also log to console for manual runs
    ]
)

logger = logging.getLogger(__name__)

def log(message):
    """Log message both to file and console"""
    logger.info(message)

def should_run():
    """Only run in production"""
    env = os.environ.get('FLASK_ENV', 'development')
    if env != 'production':
        log(f"Skipping maintenance in {env} environment")
        return False
    return True

def backup_database():
    """Create database backup"""
    log("Starting database backup...")
    
    # Create backup directory
    backup_dir = "C:\TrainingAppData\Backups"
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Check if using SQLite or MariaDB
    use_sqlite = os.environ.get('USE_SQLITE', 'False').lower() == 'true'
    
    if not use_sqlite:
        # MariaDB backup
        db_host = os.environ.get("DB_HOST")
        db_name = os.environ.get("DB_NAME")
        db_user = os.environ.get("DB_USER")
        db_password = os.environ.get("DB_PASSWORD")
        
        # Check that all required environment variables are set
        if not all([db_host, db_name, db_user, db_password]):
            log("ERROR: Missing MariaDB environment variables (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)")
            return False
        
        backup_file = backup_dir / f"backup_{timestamp}.sql"
        
        cmd = [
            'mysqldump',
            f'--host={db_host}',
            f'--port={os.environ.get("DB_PORT", "3306")}',
            f'--user={db_user}',
            f'--password={db_password}',
            '--single-transaction',
            db_name
        ]
        
        try:
            with open(backup_file, 'w') as f:
                subprocess.run(cmd, stdout=f, check=True, timeout=300)
            log(f"MariaDB backup created: {backup_file.name}")
        except Exception as e:
            log(f"Backup failed: {e}")
            return False
    
    # Clean up old backups (keep last 180 days)
    cutoff = datetime.now() - timedelta(days=180)
    for old_backup in backup_dir.glob("backup_*"):
        if datetime.fromtimestamp(old_backup.stat().st_mtime) < cutoff:
            old_backup.unlink()
            log(f"Removed old backup: {old_backup.name}")
    
    return True

def permanent_delete_old_records():
    """Delete soft-deleted records older than 180 days"""
    log("Starting permanent deletion...")
    
    try:
        from models import db_session, TrainingForm
        
        cutoff_date = datetime.now() - timedelta(days=180)
        
        with db_session() as session:
            old_forms = session.query(TrainingForm).filter(
                TrainingForm.deleted == True,
                TrainingForm.deleted_datetimestamp < cutoff_date
            ).all()
            
            if not old_forms:
                log("No old records to delete")
                return True
            
            log(f"Deleting {len(old_forms)} old records")
            
            for form in old_forms:
                # Delete associated files
                form_folder = project_root / "uploads" / f"form_{form.id}"
                if form_folder.exists():
                    shutil.rmtree(form_folder)
                
                # Delete record
                session.delete(form)
            
            session.commit()
            log(f"Permanently deleted {len(old_forms)} records")
            return True
            
    except Exception as e:
        log(f"Permanent deletion failed: {e}")
        return False

def main():
    """Main maintenance function"""
    if not should_run():
        return
    
    log("=== Starting daily maintenance ===")
    
    # Task 1: Database backup
    backup_success = backup_database()
    
    # Task 2: Permanent deletion
    delete_success = permanent_delete_old_records()
    
    if backup_success and delete_success:
        log("=== Maintenance completed successfully ===")
    else:
        log("=== Maintenance completed with errors ===")
        sys.exit(1)

if __name__ == "__main__":
    main() 