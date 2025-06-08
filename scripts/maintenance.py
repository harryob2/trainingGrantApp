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
import csv
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
import requests
import json

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
    backup_dir = Path("C:/TrainingAppData/Backups")
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
        
        # Use the specific mysqldump path
        mysqldump_exe = 'C:/Program Files/MySQL/MySQL Workbench 8.0 CE/mysqldump.exe'
        
        # Verify the command exists
        try:
            result = subprocess.run([mysqldump_exe, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                log(f"ERROR: mysqldump at {mysqldump_exe} is not working properly")
                return False
            log(f"Using mysqldump at: {mysqldump_exe}")
        except (subprocess.SubprocessError, FileNotFoundError, OSError) as e:
            log(f"ERROR: Cannot access mysqldump at {mysqldump_exe}: {e}")
            return False
        
        cmd = [
            mysqldump_exe,
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
        except subprocess.TimeoutExpired:
            log("Backup failed: Command timed out after 5 minutes")
            return False
        except subprocess.CalledProcessError as e:
            log(f"Backup failed: mysqldump returned error code {e.returncode}")
            if e.stderr:
                log(f"Error output: {e.stderr}")
            return False
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

def update_employee_list():
    """Update employee CSV file using Microsoft Graph API"""
    log("Starting employee list update...")
    
    try:
        # Get Azure credentials from environment
        client_id = os.environ.get('AZURE_CLIENT_ID')
        client_secret = os.environ.get('AZURE_CLIENT_SECRET')
        tenant_id = os.environ.get('AZURE_TENANT_ID')
        
        if not all([client_id, client_secret, tenant_id]):
            log("ERROR: Missing Azure credentials (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID)")
            return False
        
        # Log credentials (masked for security)
        log(f"Using tenant_id: {tenant_id}")
        log(f"Using client_id: {client_id[:8]}...")
        log(f"Client secret length: {len(client_secret) if client_secret else 0}")
        
        # Get access token using client credentials flow
        token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        token_data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'https://graph.microsoft.com/.default',
            'grant_type': 'client_credentials'
        }
        
        log("Acquiring access token...")
        log(f"Token URL: {token_url}")
        
        try:
            token_response = requests.post(token_url, data=token_data, timeout=30)
            
            # Log response details for debugging
            log(f"Token response status: {token_response.status_code}")
            
            if token_response.status_code != 200:
                log(f"Token request failed with status {token_response.status_code}")
                try:
                    error_details = token_response.json()
                    log(f"Error details: {error_details}")
                except:
                    log(f"Raw error response: {token_response.text}")
                return False
            
            token_response.raise_for_status()
            token_json = token_response.json()
            
            if 'access_token' not in token_json:
                log("ERROR: No access token in response")
                log(f"Response keys: {list(token_json.keys())}")
                return False
                
            access_token = token_json['access_token']
            log("Successfully acquired access token")
            
        except requests.exceptions.RequestException as e:
            log(f"Network error during token acquisition: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    log(f"Detailed error: {error_details}")
                except:
                    log(f"Raw error response: {e.response.text}")
            return False
        
        # Set up Graph API headers
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Filter criteria
        site = "Limerick, Limerick Raheen Business Park"
        domain = "@stryker.com"
        
        # Get users from Graph API
        log("Fetching users from Microsoft Graph...")
        users_url = "https://graph.microsoft.com/v1.0/users"
        params = {
            '$select': 'givenName,surname,userPrincipalName,department,officeLocation',
            '$top': 999  # Get maximum per request
        }
        
        all_users = []
        next_link = users_url
        
        while next_link:
            try:
                if next_link == users_url:
                    response = requests.get(next_link, headers=headers, params=params, timeout=60)
                else:
                    response = requests.get(next_link, headers=headers, timeout=60)
                
                if response.status_code != 200:
                    log(f"Graph API request failed with status {response.status_code}")
                    try:
                        error_details = response.json()
                        log(f"Graph API error details: {error_details}")
                    except:
                        log(f"Raw Graph API error response: {response.text}")
                    return False
                
                response.raise_for_status()
                data = response.json()
                
                # Filter users by site and domain
                filtered_users = [
                    user for user in data.get('value', [])
                    if (user.get('officeLocation') == site and 
                        user.get('userPrincipalName', '').lower().endswith(domain.lower()))
                ]
                
                all_users.extend(filtered_users)
                next_link = data.get('@odata.nextLink')
                
                log(f"Fetched {len(data.get('value', []))} users, filtered to {len(filtered_users)} matching users")
                
            except requests.exceptions.RequestException as e:
                log(f"Error fetching users from Graph API: {e}")
                return False
        
        log(f"Total matching users found: {len(all_users)}")
        
        if not all_users:
            log("WARNING: No users found matching criteria")
            return False
        
        # Prepare employee data for database
        employees_data = []
        csv_data = []  # Keep CSV data for backup file
        
        for user in all_users:
            # Handle None values from Microsoft Graph API by converting to empty strings
            first_name = user.get('givenName') or ''
            last_name = user.get('surname') or ''
            email = user.get('userPrincipalName') or ''
            department = user.get('department') or ''
            
            employee_data = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'department': department
            }
            employees_data.append(employee_data)
            
            # Also prepare CSV format for backup file
            csv_data.append({
                'FirstName': first_name,
                'LastName': last_name,
                'UserPrincipalName': email,
                'Department': department
            })
        
        # Sort by last name, then first name (with safe null handling)
        employees_data.sort(key=lambda x: ((x['last_name'] or '').lower(), (x['first_name'] or '').lower()))
        csv_data.sort(key=lambda x: ((x['LastName'] or '').lower(), (x['FirstName'] or '').lower()))
        
        # Update database first
        try:
            from models import replace_all_employees
            
            if replace_all_employees(employees_data):
                log(f"Successfully updated employee database: {len(employees_data)} employees")
            else:
                log("ERROR: Failed to update employee database")
                return False
                
        except Exception as e:
            log(f"Error updating employee database: {e}")
            return False
        
        # Write CSV file as backup
        csv_path = project_root / "attached_assets" / "EmployeeListFirstLastDept.csv"
        temp_file = None
        
        try:
            # Create temporary file in same directory as target
            with tempfile.NamedTemporaryFile(
                mode='w', 
                newline='', 
                suffix='.csv', 
                dir=csv_path.parent,
                delete=False,
                encoding='utf-8'
            ) as temp_file:
                writer = csv.DictWriter(
                    temp_file, 
                    fieldnames=['FirstName', 'LastName', 'UserPrincipalName', 'Department']
                )
                writer.writeheader()
                writer.writerows(csv_data)
                temp_file_path = temp_file.name
            
            # Test that file was written successfully
            if not os.path.exists(temp_file_path):
                log("ERROR: Temporary CSV file was not created")
                return False
            
            # Check file size
            temp_size = os.path.getsize(temp_file_path)
            if temp_size < 1000:  # Less than 1KB suggests a problem
                log(f"WARNING: Generated CSV file is very small ({temp_size} bytes)")
                os.unlink(temp_file_path)
                return False
            
            # Replace the original file
            if csv_path.exists():
                backup_path = csv_path.with_suffix('.csv.backup')
                shutil.copy2(csv_path, backup_path)
                log(f"Created CSV backup: {backup_path.name}")
            
            shutil.move(temp_file_path, csv_path)
            log(f"Employee CSV backup updated: {len(csv_data)} employees")
            log(f"CSV file size: {os.path.getsize(csv_path)} bytes")
            
            return True
            
        except Exception as e:
            log(f"Error writing CSV file: {e}")
            if temp_file and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            return False
            
    except requests.exceptions.RequestException as e:
        log(f"Network error during employee list update: {e}")
        return False
    except Exception as e:
        log(f"Employee list update failed: {e}")
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
    
    # Task 3: Employee list update
    employee_success = update_employee_list()
    
    if backup_success and delete_success and employee_success:
        log("=== Maintenance completed successfully ===")
    else:
        log("=== Maintenance completed with errors ===")
        sys.exit(1)

if __name__ == "__main__":
    main() 