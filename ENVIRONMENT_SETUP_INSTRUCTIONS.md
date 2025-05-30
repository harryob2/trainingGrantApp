# Environment Setup Instructions

## Overview

Your codebase has been updated to support both development and production environments:

- **Development**: SQLite database (current setup)
- **Production**: MariaDB database (new setup)

## Files Created/Updated

### 1. Updated Files
- ✅ `config.py` - Now supports environment-based configuration
- ✅ `models.py` - Updated to use dynamic database configuration  
- ✅ `requirements.txt` - Added `python-dotenv` for environment file support

### 2. New Files Created
- ✅ `env.example` - Template for environment configuration
- ✅ `scripts/setup_mariadb_production.sql` - MariaDB database setup script
- ✅ `scripts/setup_environment.py` - Automated environment setup
- ✅ `scripts/switch_environment.cmd` - Windows batch file for switching environments
- ✅ `scripts/switch_environment.ps1` - PowerShell script for switching environments
- ✅ `docs/environment-setup.md` - Detailed documentation

## Manual Setup Steps

### Step 1: Install Dependencies

```powershell
pip install python-dotenv==1.0.0
```

### Step 2: Create Environment Files

Create these files manually in your project root:

#### `.env.development` (for SQLite development)
```env
# Flask settings
DEBUG=True
SECRET_KEY=dev-secret-key-change-for-production

# Database settings (SQLite)
USE_SQLITE=True
DB_PATH=training_forms.db

# File upload settings
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

#### `.env.production` (for MariaDB production)
```env
# Flask settings
DEBUG=False
SECRET_KEY=your-super-secure-secret-key-here

# Database settings (MariaDB)
USE_SQLITE=False
DB_HOST=azulimpbi01
DB_PORT=3306
DB_NAME=training_tool
DB_USER=admin
DB_PASSWORD=Mfg#13579

# File upload settings
UPLOAD_FOLDER=uploads
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

#### `.env` (current environment - copy from development)
Copy the contents of `.env.development` to `.env` for now.

### Step 3: Set Up MariaDB Database

1. **Connect to your MariaDB server** (azulimpbi01)
2. **Run the setup script**:
   ```sql
   mysql -u root -p < scripts/setup_mariadb_production.sql
   ```

This will:
- Create the `training_tool` database
- Create all required tables with proper structure
- Add indexes for performance
- Insert default admin users

### Step 4: Test the Setup

#### Test Development Environment (SQLite)
```powershell
# Ensure you're using development environment
copy .env.development .env

# Test the application
python -c "from config import DATABASE_URL, USE_SQLITE; print(f'Database: {DATABASE_URL}'); print(f'SQLite: {USE_SQLITE}')"

# Start the application
python main.py
```

#### Test Production Environment (MariaDB)
```powershell
# Switch to production environment
copy .env.production .env

# Update the password in .env.production first!
# Edit .env.production and change DB_PASSWORD to the correct value

# Test the connection
python -c "from config import DATABASE_URL, USE_SQLITE; print(f'Database: {DATABASE_URL.replace('Mfg#13579', '***')}'); print(f'SQLite: {USE_SQLITE}')"

# Start the application
python main.py
```

## How It Works

### Environment Detection
The application now automatically detects which environment to use:

1. **Environment Files**: Loads `.env.{FLASK_ENV}` first, then falls back to `.env`
2. **Database Selection**: Uses `USE_SQLITE` environment variable to choose database
3. **Configuration**: All settings come from environment variables with sensible defaults

### Database URLs
- **Development**: `sqlite:///training_forms.db`
- **Production**: `mysql+pymysql://admin:password@azulimpbi01:3306/training_tool`

### Switching Environments
```powershell
# Switch to development
copy .env.development .env
set FLASK_ENV=development

# Switch to production  
copy .env.production .env
set FLASK_ENV=production
```

## Important Security Notes

1. **Never commit `.env` files** to version control (already in .gitignore)
2. **Change the SECRET_KEY** in production to a strong, unique value
3. **Update database passwords** with actual secure passwords
4. **Use HTTPS** in production environments

## Database Differences

### SQLite (Development)
- ✅ File-based, no server required
- ✅ Easy to backup and move
- ❌ Single-user, limited performance
- ❌ No advanced features

### MariaDB (Production)  
- ✅ Multi-user, better performance
- ✅ Advanced features and scalability
- ✅ Better backup and recovery options
- ❌ Requires server setup and maintenance

## Troubleshooting

### Common Issues

1. **"No module named 'config'"**
   - Make sure you're in the correct directory
   - Ensure config.py exists

2. **Database connection failed**
   - Check environment variables are set correctly
   - For MariaDB: ensure server is accessible and credentials are correct
   - For SQLite: ensure file permissions are correct

3. **Environment file not loading**
   - Ensure python-dotenv is installed: `pip install python-dotenv`
   - Check file encoding is UTF-8
   - Verify file syntax (no spaces around =)

### Testing Database Connectivity

```powershell
# Test SQLite
python -c "import sqlite3; print('SQLite available:', sqlite3.sqlite_version)"

# Test MariaDB connection  
python -c "import pymysql; conn = pymysql.connect(host='azulimpbi01', user='admin', password='your_password', database='training_tool'); print('MariaDB connection successful'); conn.close()"
```

## Next Steps

1. ✅ **Create environment files** (manual step above)
2. ✅ **Test development environment** with SQLite
3. ✅ **Set up MariaDB database** using the provided SQL script
4. ✅ **Test production environment** with MariaDB
5. ✅ **Deploy to production** server with correct environment settings

Your codebase is now ready for both development and production environments! 