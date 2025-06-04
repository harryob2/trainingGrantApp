# Scripts Archive Documentation

## Overview

The `scripts/archive/` folder contains legacy and utility scripts that are no longer part of the active deployment pipeline but are preserved for reference, one-time operations, and historical purposes.

## Archive Structure

```
scripts/archive/
├── data/                    # Data import/export utilities
├── database/               # Database setup scripts  
├── environment/            # Environment configuration scripts
└── migrations/             # Pre-Alembic migration scripts
```

## Archive Categories

### Data Management (`scripts/archive/data/`)

**Purpose**: Tools for importing and exporting training data, particularly useful for:
- Initial data setup
- Data migration between environments
- One-time data imports from Excel files
- Backup and restore operations

**Key Files**:
- `export_training_catalog.py` - Export training catalog to SQL format
- `import_trainings.py` - Import training data from Excel files
- `training_catalog_data.sql` - Pre-generated training catalog data
- `export_data_manual.sql` - Manual export commands for SQLite
- `EXPORT_INSTRUCTIONS.md` - Detailed export procedures

**When to Use**:
- Setting up a new environment with training catalog data
- Migrating from legacy Excel-based systems
- Creating data backups for disaster recovery

### Database Setup (`scripts/archive/database/`)

**Purpose**: Database initialization scripts for different environments.

**Key Files**:
- `setup_mariadb_production.sql` - Production database schema and initial data
- `setup_mariadb_staging.sql` - Staging database schema and initial data
- `create_production_db.py` - Python script for database creation

**When to Use**:
- Initial database setup for new environments
- Recreating databases after major schema changes
- Setting up test environments that mirror production

### Environment Configuration (`scripts/archive/environment/`)

**Purpose**: Legacy environment setup and switching utilities.

**Key Files**:
- `setup_environment.py` - Automated environment configuration
- `setup_staging_environment.py` - Staging-specific setup
- `switch_environment.cmd` / `switch_environment.ps1` - Environment switchers

**When to Use**:
- Reference for manual environment setup
- Understanding legacy configuration approaches
- Troubleshooting environment-related issues

### Database Migrations (`scripts/archive/migrations/`)

**Purpose**: Pre-Alembic migration scripts used before the current migration system.

**Key Files**:
- `add_*_migration.py` - Various column addition migrations
- `remove_food_cost_migration.py` - Column removal example
- `add_travel_expenses_migration.py` - Table creation example

**When to Use**:
- Reference for understanding database evolution
- Learning migration patterns and techniques
- Emergency manual database modifications

## Current vs. Archive

### Active Scripts (in `scripts/`)
- `start_production.py` - Production application startup
- `start_staging.py` - Staging application startup  
- `manage_production_service.ps1` - Service management

### Archived Scripts (in `scripts/archive/`)
- All data import/export utilities
- Database setup scripts
- Environment configuration tools
- Legacy migration scripts

## Migration from Archive

If you need to use an archived script:

1. **Copy to main scripts folder**:
   ```powershell
   copy scripts\archive\data\export_training_catalog.py scripts\
   ```

2. **Review and update**:
   - Check for outdated paths or configurations
   - Ensure compatibility with current database schema
   - Update any hardcoded values

3. **Test thoroughly**:
   - Test in development environment first
   - Verify data integrity
   - Check for any breaking changes

4. **Clean up after use**:
   - Remove temporary scripts if they're one-time use
   - Document any permanent additions

## Best Practices

### Using Archive Scripts

1. **Always backup data** before running any archive scripts
2. **Test in development** before using in production
3. **Review the code** to understand what it does
4. **Update paths and configs** as needed for current environment

### Maintaining the Archive

1. **Keep useful scripts** that might be needed again
2. **Remove truly obsolete** scripts to avoid confusion
3. **Document any changes** in commit messages
4. **Preserve context** with README files and comments

## Migration Guidelines

### From Legacy to Current System

The application has evolved from manual script management to an automated deployment pipeline:

**Old Way** (now archived):
- Manual database setup scripts
- Environment switching scripts
- Manual migration scripts
- Data import/export utilities run manually

**New Way** (current):
- Alembic for database migrations
- GitHub Actions for deployment
- Environment-specific configuration files
- Automated service management

### When Archive Scripts Are Still Useful

1. **One-time data migrations** - when moving from legacy systems
2. **Database recovery** - when automated tools fail
3. **Custom data exports** - for reporting or backup purposes
4. **Environment setup** - for completely new installations

## Support

If you need to use archive scripts:

1. **Check this documentation** first
2. **Review the script code** and comments
3. **Test in development** environment
4. **Create backups** before running in production
5. **Contact the development team** if you're unsure

Remember: Archive scripts are preserved for reference and special circumstances, but the active deployment pipeline should handle most routine operations automatically. 