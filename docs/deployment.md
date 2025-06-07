# Deployment and Migration Guide

## Overview

This guide covers the GitHub Actions deployment pipeline and database migration system for the Training Form Application. The system supports automated deployment to development, staging, and production environments with comprehensive testing, **automatic schema change detection**, and database migrations.

## Deployment Pipeline Architecture

The deployment pipeline follows a three-tier approach:

1. **Development** (Local): SQLite-based development environment on your local machine with local `uploads/` folder
2. **Staging** (Server): MariaDB-based staging environment that mirrors production for testing with local `uploads_staging/` folder using Waitress WSGI server
3. **Production** (Server): MariaDB-based production environment for live application with dedicated `c:/TrainingAppData/Uploads/` folder using Waitress WSGI server

### Upload Folder Strategy

The application uses environment-specific upload folders to prevent deployment issues:

- **Development**: Uses local `uploads/` folder within the project directory
- **Staging**: Uses local `uploads_staging/` folder for testing
- **Production**: Uses dedicated `c:/TrainingAppData/Uploads/` folder outside the project directory

**Key Benefits**:
- Prevents production deployments from overwriting uploaded files
- Development files stay local and don't interfere with deployments
- Clean separation between environments
- No risk of losing uploaded attachments during deployments

### Deployment Flow

```
Code Push → Unit Tests → Schema Validation → Staging Deployment → Integration Tests → Production Deployment
```

**Key Safety Features**:
- **Production Protection**: Cannot deploy directly to production
- **Staging Gate**: Production deployment only happens after successful staging deployment
- **Schema Change Detection**: **NEW!** Automatically detects when you've modified models without creating migrations
- **Migration Validation**: Ensures all database changes have corresponding migration scripts
- **Comprehensive Testing**: Integration tests run in staging environment before production
- **Automated Rollback**: Backup and rollback capabilities for failed deployments

## Enhanced Migration Detection System

### The Problem This Solves

**Your Question**: *"I've forgotten to run the flask migrate command... will this deployment pipeline pick up on that and fail the deployment?"*

**Answer**: **YES!** The enhanced deployment pipeline now includes automatic schema change detection that will:

1. **Detect Model Changes**: Compare your current `models.py` with the database schema
2. **Fail the Deployment**: Stop the deployment if schema changes are detected without corresponding migrations
3. **Provide Clear Instructions**: Tell you exactly how to fix the issue
4. **Prevent Data Loss**: Ensure staging and production databases stay in sync with your code

**Recent Example**: The soft delete functionality added `deleted` and `deleted_datetimestamp` columns to the `training_forms` table. The migration script `2927b5fcd043_add_soft_delete_columns_to_training_.py` was created to handle this schema change safely across all environments.

### How Schema Detection Works

#### 1. Automatic Detection in CI/CD Pipeline

The staging deployment now includes a **schema validation step**:

```yaml
- name: Check for pending schema changes
  run: |
    echo "Checking for pending database schema changes..."
    python scripts/schema_validator.py --check-changes
```

This step:
- Analyzes your SQLAlchemy models to create a "schema fingerprint"
- Compares the models with the actual database schema
- **Fails the deployment** if mismatches are detected
- Provides detailed error messages explaining what to do

#### 2. Flask-Migrate Integration

The system now includes Flask-Migrate for automatic migration generation:

```powershell
# Initialize migrations (one-time setup)
python -m alembic init alembic

# Detect if you have pending schema changes
python -m alembic check

# Create a migration for your model changes
python -m alembic revision --autogenerate -m "Add new field to training form"

# Check migration status
python -m alembic current
```

#### 3. What Happens When You Forget a Migration

**Scenario**: You modify `models.py` (add a field, change a column, etc.) but forget to create a migration.

**Before Enhancement**: The deployment would succeed, but the database wouldn't match your models, leading to runtime errors.

**After Enhancement**: The deployment **fails in staging** with clear error messages:

```
❌ SCHEMA MISMATCH DETECTED!
Your model definitions don't match the database schema.
This usually means:
  1. You modified models.py but didn't create a migration
  2. You didn't run migrations after modifying models
  3. There are pending migrations that haven't been applied

To fix this:
  1. Create a migration: python -m alembic revision --autogenerate -m "Describe your changes"
  2. Review the generated migration file
  3. Test the migration locally
  4. Commit the migration file and redeploy
```

### Migration Workflow Enhancement

#### Development Workflow

1. **Make Model Changes** in `models.py`
   ```python
   # Example: Add a new field
   class TrainingForm(Base):
       # ... existing fields ...
       new_field = Column(String(255))  # Your new field
   ```

2. **Create Migration** (Alembic detects changes automatically)
   ```powershell
   python -m alembic revision --autogenerate -m "Add new_field to training forms"
   ```

3. **Review Migration** (edit if needed)
   - Migration file is created in `alembic/versions/`
   - Review the auto-generated SQL to ensure it's correct
   - Make manual adjustments if needed

4. **Test Locally**
   ```powershell
   # Test in development
   set FLASK_ENV=development
   python -m alembic upgrade head
   
   # Test your application
   python main.py
   ```

5. **Commit and Deploy**
   ```bash
   git add alembic/versions/xxx_add_new_field.py
   git commit -m "Add new_field to training forms with migration"
   git push origin main  # Triggers deployment
   ```

#### What the Pipeline Does

1. **Staging Deployment**:
   - Checks for schema changes ✅
   - Applies migrations automatically ✅
   - Runs integration tests ✅
   - Validates schema consistency ✅

2. **Production Deployment** (only if staging passes):
   - Creates backup ✅
   - Applies migrations ✅
   - Validates deployment ✅
   - Runs health checks ✅

## Database Migration System

### Migration Workflow Across Environments

#### Development → Staging → Production Flow

1. **Develop Migration Locally**
   ```powershell
   # Make changes to models.py
   # Create migration
   python -m alembic revision --autogenerate -m "describe your changes"
   
   # Test migration in development
   set FLASK_ENV=development
   python -m alembic upgrade head
   ```

2. **Push to Staging**
   ```bash
   git add alembic/versions/
   git commit -m "Add migration for new feature"
   git push origin main  # Triggers staging deployment
   ```

3. **Automatic Staging Testing**
   - GitHub Actions deploys to staging
   - **Schema validation** ensures models match database
   - Runs migrations on staging database
   - Executes integration tests
   - Validates migration success

4. **Automatic Production Deployment**
   - If staging tests pass, deploys to production
   - Runs migrations on production database
   - Creates backup before deployment
   - Validates production deployment

### Environment-Specific Migration Commands

#### Check Migration Status
```powershell
# Development (SQLite)
set FLASK_ENV=development
python -m alembic current

# Staging (MariaDB staging)
set FLASK_ENV=staging
python -m alembic current

# Production (MariaDB production)
set FLASK_ENV=production
python -m alembic current
```

#### Run Migrations
```powershell
# Development
set FLASK_ENV=development
python -m alembic upgrade head

# Staging (happens automatically in CI/CD)
set FLASK_ENV=staging
python -m alembic upgrade head

# Production (happens automatically in CI/CD)
set FLASK_ENV=production
python -m alembic upgrade head
```

#### Create Migrations for Model Changes
```powershell
# Detect if you have pending changes
python -m alembic check

# Create a migration for detected changes
python -m alembic revision --autogenerate -m "Description of your changes"

# Validate deployment readiness
python -m alembic current
```

## GitHub Actions Deployment

### Repository Setup

1. **Set up your GitHub repository** with the application code
2. **Configure a self-hosted runner** for deployment
3. **Set up GitHub Secrets** for all environment variables
4. **Create environment configurations** in GitHub
5. **Set up staging and production databases** on MariaDB server

### GitHub Secrets Configuration

Navigate to your repository settings → Secrets and variables → Actions, and add these secrets:

#### Development Environment Secrets
- `DEV_SECRET_KEY` - Secret key for development environment

#### Staging Environment Secrets
- `STAGING_SECRET_KEY` - Secret key for staging environment
- `STAGING_DB_HOST` - Staging MariaDB hostname (usually same as production)
- `STAGING_DB_PORT` - Staging database port (usually 3306)
- `STAGING_DB_NAME` - Staging database name (`training_tool_staging`)
- `STAGING_DB_USER` - Staging database username
- `STAGING_DB_PASSWORD` - Staging database password
- `STAGING_NETWORK_STORAGE_PATH` - Network storage path for staging uploads

#### Production Environment Secrets
- `PROD_SECRET_KEY` - Strong secret key for production
- `PROD_DB_HOST` - Production MariaDB hostname
- `PROD_DB_PORT` - Production database port (usually 3306)
- `PROD_DB_NAME` - Production database name (`training_tool`)
- `PROD_DB_USER` - Production database username
- `PROD_DB_PASSWORD` - Production database password
- `PROD_NETWORK_STORAGE_PATH` - Network storage path for file uploads

#### Shared Environment Secrets
- `LDAP_HOST` - LDAP server hostname
- `LDAP_PORT` - LDAP server port (usually 3268)
- `LDAP_BASE_DN` - LDAP base DN (e.g., `DC=strykercorp,DC=com`)
- `LDAP_DOMAIN` - LDAP domain (e.g., `strykercorp.com`)

#### Azure Integration Secrets
- `AZURE_CLIENT_ID` - Azure App Registration client ID for Microsoft Graph API access
- `AZURE_CLIENT_SECRET` - Azure App Registration client secret
- `AZURE_TENANT_ID` - Azure tenant ID for authentication

### Database Setup for Staging and Production

#### 1. Set up Staging Database

Connect to your MariaDB server and run the staging setup script:

```sql
mysql -u root -p < scripts/setup_mariadb_staging.sql
```

This creates:
- `training_tool_staging` database
- All required tables and indexes
- Sample data for testing
- Default admin users

#### 2. Set up Production Database

Connect to your MariaDB server and run the production setup script:

```sql
mysql -u root -p < scripts/setup_mariadb_production.sql
```

This creates:
- `training_tool` database (production)
- All required tables and indexes
- Default admin users

#### 3. Create Dedicated Database Users (Recommended)

For better security, create separate users for staging and production:

```sql
-- Staging user
CREATE USER 'training_staging'@'%' IDENTIFIED BY 'StagingPassword123!';
GRANT ALL PRIVILEGES ON training_tool_staging.* TO 'training_staging'@'%';

-- Production user
CREATE USER 'training_app'@'%' IDENTIFIED BY 'ProductionPassword456!';
GRANT ALL PRIVILEGES ON training_tool.* TO 'training_app'@'%';

FLUSH PRIVILEGES;
```

### Workflow Configuration

The deployment workflow (`.github/workflows/deploy.yml`) includes:

#### Trigger Events
- **Push to develop branch** → Development deployment (local)
- **Push to main branch** → Schema validation → Staging deployment → Production deployment (if staging passes)
- **Pull requests to main** → Unit testing only
- **Manual workflow dispatch** → Choose specific environment

#### Maintenance System Integration
The deployment pipeline ensures proper configuration for the automated maintenance system, which includes:
- Database backup operations
- Data cleanup processes
- Employee data synchronization from Microsoft Graph API
- All maintenance tasks run nightly at 3 AM in production environment

#### Jobs Pipeline

1. **Unit Tests Job**
   - Runs on all triggers
   - Sets up Python environment with SQLite for testing
   - Installs dependencies and runs unit tests
   - Validates basic application functionality

2. **Deploy Development Job** (develop branch)
   - Triggers on develop branch pushes
   - Deploys to local SQLite-based development environment
   - Quick validation for development work

3. **Deploy Staging Job** (main branch)
   - Triggers on main branch pushes
   - **NEW: Schema Validation Step** - Detects pending schema changes
   - **Production Gatekeeper**: Must pass before production deployment
   - Creates MariaDB-based staging environment
   - Runs comprehensive integration tests
   - Validates database connectivity and migrations
   - Tests application functionality in server environment

4. **Deploy Production Job** (main branch, after staging)
   - **Only runs after successful staging deployment**
   - Creates production backup before deployment
   - Deploys to production MariaDB environment
   - Runs production health checks
   - Validates production deployment

### Enhanced Integration Testing in Staging

The staging environment runs comprehensive integration tests:

#### Schema Validation Tests
- **Model-Database Consistency**: Ensures your models match the database schema
- **Migration Status**: Verifies all migrations have been applied
- **Schema Change Detection**: Alerts if model changes don't have corresponding migrations

#### Application Health Tests
- Basic HTTP response validation
- Database connectivity through API endpoints
- Migration status verification
- Admin access validation

#### Database Integration Tests
- Connection to staging database
- Migration execution and validation
- Data model functionality
- Relationship integrity checks

#### Test Coverage
```python
# Integration tests run in staging
- Schema validation and migration checks  # NEW!
- Application startup and response
- Database connection and queries
- API endpoint functionality  
- Admin user access
- File upload directory creation
- Environment configuration validation
```

## Error Scenarios and Solutions

### Common Migration Issues

#### 1. Forgot to Create Migration
**Error**: Schema changes detected but no migration created
```
❌ SCHEMA MISMATCH DETECTED!
Your model definitions don't match the database schema.
```

**Solution**:
```powershell
# Create the missing migration
python -m alembic revision --autogenerate -m "Describe what you changed"

# Review and test the migration
set FLASK_ENV=development
python -m alembic upgrade head

# Commit and redeploy
git add alembic/versions/
git commit -m "Add missing migration"
git push origin main
```

#### 2. Created Migration but Didn't Commit It
**Error**: Local migration exists but not in repository
```
⚠️ Migration version mismatch between local and remote
```

**Solution**:
```bash
# Add the migration file to git
git add alembic/versions/xxx_your_migration.py
git commit -m "Add migration for model changes"
git push origin main
```

#### 3. Migration Fails in Staging
**Error**: Migration syntax error or constraint violation
```
❌ Failed to apply migrations in staging
```

**Solution**:
```powershell
# Fix the migration file locally
# Edit alembic/versions/xxx_migration.py

# Test the fix in development
set FLASK_ENV=development
python -m alembic upgrade head

# Commit the fix
git add alembic/versions/xxx_migration.py
git commit -m "Fix migration issue"
git push origin main
```

## Manual Deployment Override

### Emergency Production Deployment

In case you need to deploy directly to production (emergency situations):

```yaml
# Use workflow dispatch with production environment
# This still requires staging to pass, but you can run it manually
```

### Manual Environment Testing

Test specific environments manually:

```powershell
# Test staging environment
copy .env.staging .env
python main.py  # Runs on port 5000

# Test production environment (be careful!)
copy .env.production .env
python main.py  # Runs on port 5000
```

## Deployment Monitoring and Validation

### Enhanced Staging Environment Validation

The staging deployment includes comprehensive validation:

#### Automated Checks
- **Schema consistency validation** (NEW!)
- **Migration status verification** (NEW!)
- Database connection and migration status
- Application startup and basic functionality
- API endpoint responsiveness
- Admin user access verification
- File system and directory creation

#### Integration Test Results
```
✅ Schema changes validation passed
✅ Migration status verified
✅ Staging application is responding
✅ Staging database connectivity test passed
✅ Database models loaded successfully
✅ Connected to staging database: training_tool_staging
✅ Database operations working correctly
✅ All staging tests completed successfully
```

### Production Environment Validation

Production deployment includes additional safety checks:

#### Pre-deployment Checks
- Production database connectivity
- Backup creation and verification
- Migration validation

#### Post-deployment Validation
```
✅ Production health check passed
✅ Production deployment validated
✅ Connected to production database: training_tool
✅ Admin access verified
```

## Rollback Procedures

### Staging Rollback

If staging deployment fails:
```powershell
# Staging issues are typically resolved by fixing code and re-deploying
# No production impact since production deployment is blocked
```

### Production Rollback

If production deployment fails:

#### Automatic Rollback Triggers
- Health check failures
- Database connection issues
- Migration failures

#### Manual Rollback
```powershell
# Stop production service
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Training Form App - Production"

# Restore from backup
copy "production_backup_TIMESTAMP\training_forms.db" training_forms.db
xcopy "production_backup_TIMESTAMP\uploads\" uploads\ /e /i /y

# Reset migration version if needed
python -m alembic current

# Restart application
python main.py
```

## Environment Configuration Summary

### Development (.env.development)
```bash
DEBUG=True
USE_SQLITE=True
DB_PATH=training_forms.db
UPLOAD_FOLDER=uploads
FLASK_ENV=development
```

### Staging (.env.staging)
```bash
DEBUG=False
USE_SQLITE=False
DB_HOST=azulimpbi01
DB_NAME=training_tool_staging
DB_USER=training_staging
UPLOAD_FOLDER=uploads_staging
FLASK_ENV=staging
```

### Production (.env.production)
```bash
DEBUG=False
USE_SQLITE=False
DB_HOST=azulimpbi01
DB_NAME=training_tool
DB_USER=training_app
UPLOAD_FOLDER=c:/TrainingAppData/Uploads
FLASK_ENV=production
```

## Best Practices

### Enhanced Deployment Safety
1. **Never bypass staging** - Always test in staging first
2. **Always create migrations** - Use Flask-Migrate for model changes
3. **Test migrations locally** - Verify migrations work before pushing
4. **Monitor staging tests** - Ensure all integration tests pass
5. **Review staging results** - Check staging logs before production
6. **Have rollback plan** - Always be ready to rollback production
7. **Validate production** - Monitor production deployment carefully
8. **Use production WSGI server** - Waitress is used instead of Flask's development server

### Enhanced Database Management
1. **Create migrations for all model changes** - No exceptions!
2. **Test migrations in development first** - Always test locally
3. **Review auto-generated migrations** - Flask-Migrate isn't perfect
4. **Use descriptive migration messages** - Help future developers
5. **Monitor migration performance** - Check migration execution time
6. **Backup before migrations** - Always create backups before changes
7. **Validate data integrity** - Ensure data consistency after migrations

### Enhanced Security Practices
1. **Separate credentials** - Use different passwords for staging/production
2. **Limit access** - Restrict database user privileges
3. **Rotate secrets** - Regularly update GitHub secrets
4. **Monitor access** - Track database and application access
5. **Validate schema changes** - Use automated schema validation

## Troubleshooting

### Enhanced Common Staging Issues

#### Schema Validation Failed
```powershell
# Check what changes were detected
python scripts/schema_validator.py --check-changes

# Create missing migration
python -m alembic revision --autogenerate -m "Fix detected changes"

# Test migration locally
set FLASK_ENV=development
python -m alembic upgrade head
```

#### Staging Database Connection Failed
```powershell
# Check staging database exists
mysql -u root -p -e "SHOW DATABASES LIKE 'training_tool_staging';"

# Verify staging user permissions
mysql -u training_staging -p training_tool_staging -e "SELECT 1;"
```

#### Staging Integration Tests Failed
- Check staging application logs
- Verify database connectivity
- Ensure all required tables exist
- Validate admin user setup
- **Check migration status**

### Enhanced Common Production Issues

#### Production Deployment Blocked
- **Check staging deployment status**
- **Review staging schema validation results**
- Review staging test results
- Fix staging issues before production

#### Production Health Check Failed
- Check production database connectivity
- Verify application configuration
- Review production logs
- Consider rollback if issues persist

### Enhanced Emergency Procedures

#### Emergency Production Access
```powershell
# Direct production database access (use carefully)
mysql -u training_app -p training_tool

# Emergency application restart
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Training Form App - Production"
python main.py
```

#### Emergency Migration Rollback
```powershell
# Check current migration status
python -m alembic current

# Rollback to previous migration (if needed)
# Note: This requires manual intervention
mysql -u training_app -p training_tool
```

## Production Server Improvements

### Waitress WSGI Server

The application now uses **Waitress** as the production WSGI server instead of Flask's built-in development server:

#### Benefits of Waitress
- **Production-Ready**: Designed specifically for production environments
- **Windows Compatible**: Works excellently on Windows servers
- **Multi-threaded**: Handles concurrent requests efficiently
- **No Development Warnings**: Clean production logs without "development server" warnings
- **Better Performance**: Optimized for production workloads

#### Server Configuration
```python
# Production server configuration (scripts/start_production.py)
from waitress import serve
serve(app, host='0.0.0.0', port=5000, threads=6, connection_limit=1000, cleanup_interval=30)

# Staging server configuration (scripts/start_staging.py)  
from waitress import serve
serve(app, host='0.0.0.0', port=5001, threads=4, connection_limit=500, cleanup_interval=30)
```

#### Management Tools
- **scripts/restart_waitress.ps1**: Simple PowerShell script for service management
- **scripts/test_waitress.py**: Validation script to test Waitress setup
- Enhanced configuration with proper DEBUG=False defaults

#### Usage
```powershell
# Check service status
.\scripts\restart_waitress.ps1 -Status

# Restart production service with Waitress
.\scripts\restart_waitress.ps1
```

## Summary

The enhanced deployment pipeline now provides **comprehensive protection** against database schema issues:

1. **✅ Automatic Detection**: Detects when you modify models without creating migrations
2. **✅ Clear Error Messages**: Tells you exactly what's wrong and how to fix it
3. **✅ Staging Protection**: Prevents problematic deployments from reaching production
4. **✅ Easy Migration Creation**: Flask-Migrate integration for automatic migration generation
5. **✅ Comprehensive Testing**: Validates schema consistency across all environments
6. **✅ Production WSGI Server**: Waitress replaces Flask's development server for better performance and security

**You can now confidently make model changes** knowing that the deployment pipeline will catch any missing migrations and prevent data inconsistencies! 