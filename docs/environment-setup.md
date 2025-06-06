# Environment Setup Guide

## Overview

The Training Form Application supports both development and production environments with different database configurations:

- **Development**: SQLite database (file-based, no server required)
- **Production**: MariaDB database (server-based, better performance and scalability)

## Quick Setup

### 1. Run the Setup Script (Legacy - Now Archived)

**Note**: The automated setup script has been moved to `scripts/archive/environment/setup_environment.py` for reference. For new setups, follow the manual setup process below.

### 2. Manual Setup (Recommended)

Follow these steps for a clean setup:

#### Install Dependencies
```powershell
pip install -r requirements.txt
```

#### Create Environment Files
Copy the environment template and create your configuration files:

```powershell
# For development (SQLite)
cp env.example .env.development

# For production (MariaDB)
cp env.example .env.production
```

## Environment Configuration

### Upload Folder Configuration

The application uses environment-specific upload folders to prevent deployment issues:

- **Development**: Uses local `uploads/` folder within the project directory
- **Production**: Uses dedicated `c:/TrainingAppFormUploads/` folder outside the project

This design prevents production deployments from overwriting uploaded files, as the local development `uploads/` folder is excluded from git (via `.gitignore`) and won't affect production storage.

**Key Benefits**:
- Development files stay local and don't interfere with deployments
- Production files are preserved outside the project directory
- No risk of losing uploaded attachments during deployments
- Clean separation between environments

### Development Environment (.env.development)

```bash
# Flask settings
DEBUG=True
SECRET_KEY=dev-secret-key-change-for-production

# Database settings (SQLite)
USE_SQLITE=True
DB_PATH=training_forms.db

# File upload settings (Environment-specific)
# Development: Local uploads folder within project
UPLOAD_FOLDER=uploads

# LDAP Configuration
LDAP_HOST=limdc02.strykercorp.com
LDAP_PORT=3268
LDAP_BASE_DN=DC=strykercorp,DC=com
LDAP_DOMAIN=strykercorp.com
LDAP_USE_SSL=False

# Environment
FLASK_ENV=development
```

### Production Environment (.env.production)

```bash
# Flask settings
DEBUG=False
SECRET_KEY=your-super-secure-secret-key-here

# Database settings (MariaDB)
USE_SQLITE=False
DB_HOST=azulimpbi01
DB_PORT=3306
DB_NAME=training_tool
DB_USER=admin
DB_PASSWORD=your-secure-password

# File upload settings (Environment-specific)
# Production: Dedicated folder outside project directory
UPLOAD_FOLDER=c:/TrainingAppFormUploads
NETWORK_STORAGE_PATH=\\strykercorp.com\lim\Engineering_DOG\5. Automation & Controls\01. Projects\Training Form Invoices

# LDAP Configuration
LDAP_HOST=limdc02.strykercorp.com
LDAP_PORT=3268
LDAP_BASE_DN=DC=strykercorp,DC=com
LDAP_DOMAIN=strykercorp.com
LDAP_USE_SSL=False

# Environment
FLASK_ENV=production
```

## Environment specific settings

## Database Setup

### Development Database (SQLite)

SQLite is used automatically in development. The database file `training_forms.db` is created automatically when you first run the application.

To initialize the database:
```powershell
python setup_db.py
```

### Production Database (MariaDB)

#### 1. Run the MariaDB Setup Script

**Note**: The setup scripts have been moved to `scripts/archive/database/` for reference. You can use them as templates:

Connect to your MariaDB server and run the setup script:

```sql
mysql -u root -p < scripts/archive/database/setup_mariadb_production.sql
```

This script will:
- Create the `training_tool_production` database
- Create all required tables with proper indexes
- Insert default admin users
- Set up foreign key relationships

#### 2. Create Application User (Optional but Recommended)

For better security, create a dedicated user for the application:

```sql
-- Connect as root user
mysql -u root -p

-- Create application user
CREATE USER 'training_app'@'%' IDENTIFIED BY 'SecurePassword123!';
GRANT ALL PRIVILEGES ON training_tool.* TO 'training_app'@'%';
FLUSH PRIVILEGES;
```

Then update your `.env.production` file:
```bash
DB_USER=training_app
DB_PASSWORD=SecurePassword123!
```

## Running the Application

### Development Mode

```powershell
# Set environment
set FLASK_ENV=development

# Or use the environment file directly
python main.py
```

### Production Mode

```powershell
# Set environment
set FLASK_ENV=production

# Run the application
python main.py
```

### Using Different Environment Files

You can explicitly specify which environment file to use:

```powershell
# Copy the desired environment file to .env
copy .env.development .env
python main.py

# Or
copy .env.production .env
python main.py
```

## Environment Variable Priority

The application loads configuration in this order:

1. System environment variables (highest priority)
2. `.env.{FLASK_ENV}` file (e.g., `.env.production`)
3. `.env` file
4. Default values in `config.py` (lowest priority)

## Database Migration

### From Development to Production

To migrate data from SQLite to MariaDB:

1. **Export data from SQLite** (use archived scripts as reference):
   ```powershell
   # Legacy export scripts are available in scripts/archive/data/ for reference
   # For training catalog data export:
   python scripts/archive/data/export_training_catalog.py
   
   # Or manually export using the SQL template:
   sqlite3 training_forms.db < scripts/archive/data/export_data_manual.sql
   ```

2. **Import data to MariaDB**:
   ```sql
   # Use the generated SQL file
   mysql -u root -p training_tool_production < scripts/archive/data/training_catalog_data.sql
   ```

**Note**: Data migration scripts are preserved in `scripts/archive/data/` for reference and can be copied to the main scripts folder if needed for one-time migrations.

### Database Schema Updates

When updating the database schema:

1. **Update models.py** with new fields/tables
2. **Create migration script** in `scripts/` directory
3. **Run migration** on both development and production databases

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

**SQLite Issues**:
- Check if the database file exists and is writable
- Ensure the application has write permissions to the directory

**MariaDB Issues**:
- Verify the database server is running
- Check connection details (host, port, username, password)
- Ensure the `training_tool` database exists
- Test network connectivity to the database server

#### 2. Environment Variables Not Loading

- Check if `.env` files exist and have correct syntax
- Verify `python-dotenv` is installed: `pip install python-dotenv`
- Check file encoding (should be UTF-8)

#### 3. LDAP Authentication Issues

- Verify LDAP server connectivity
- Check LDAP configuration values
- Test with bypass accounts for development

### Database Connection Testing

Test your database connections:

```powershell
# Test current configuration
python -c "from models import engine; print('Database connection:', engine.connect())"

# Test specific environment
set FLASK_ENV=production
python -c "from models import engine; print('Production DB:', engine.connect())"
```

### Debug Mode

Enable detailed logging by setting `DEBUG=True` in your environment file. This will show:
- Database connection details
- Environment loading information
- SQL queries (if enabled)

## Security Considerations

### Development Security
- Use different secret keys for development and production
- Don't commit `.env` files to version control
- Use test/bypass accounts for development authentication

### Production Security
- Use strong, unique secret keys
- Secure database credentials
- Enable SSL/TLS for database connections in production
- Use dedicated database users with minimal privileges
- Regular security updates for the database server

## File Organization

```
├── .env.development      # Development environment config
├── .env.production       # Production environment config
├── .env                  # Current environment (copy of one above)
├── env.example          # Template for environment files
├── config.py            # Application configuration
├── models.py            # Database models
├── scripts/
│   ├── setup_mariadb_production.sql    # MariaDB setup script
│   └── setup_environment.py            # Environment setup helper
└── docs/
    └── environment-setup.md             # This documentation
```

## Next Steps

After completing the environment setup:

1. **Review configuration files** and update passwords/secrets
2. **Test the application** in both development and production modes
3. **Set up backup procedures** for production database
4. **Configure monitoring** for production environment
5. **Document deployment procedures** for your team 