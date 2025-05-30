# Database Migrations with Alembic

This directory contains the Alembic migration system for the Flask Survey Form application.

## Quick Start

Use Alembic directly for all migration operations:

### Common Commands

```bash
# Check current migration status
python -m alembic current -v

# Create a new migration (auto-detects changes to models.py)
python -m alembic revision --autogenerate -m "Add new field to training forms"

# Apply all pending migrations
python -m alembic upgrade head

# Rollback to a specific revision
python -m alembic downgrade <revision_id>

# View migration history
python -m alembic history -v

# Mark current schema as baseline (for existing databases)
python -m alembic stamp head
```

## Migration Workflow

### 1. Making Model Changes
1. Edit your models in `models.py`
2. Create a migration: `python -m alembic revision --autogenerate -m "Describe your changes"`
3. Review the generated migration file in `alembic/versions/`
4. Apply the migration: `python -m alembic upgrade head`

### 2. Deployment
The GitHub Actions workflow automatically:
- Checks migration status before deployment
- Applies pending migrations during deployment
- Validates the database is up-to-date after deployment

## Migration Files

Migration files are stored in `alembic/versions/` and contain:
- **upgrade()** function: applies the migration
- **downgrade()** function: rolls back the migration

## Environment Configuration

Alembic is configured to:
- Use your existing `config.py` for database connection
- Work with your SQLAlchemy models in `models.py`
- Support both SQLite (development) and MariaDB (production)

## Troubleshooting

### Database Out of Sync
If your database schema doesn't match your models:
```bash
# Check what migrations are pending
python -m alembic current -v

# Apply missing migrations
python -m alembic upgrade head
```

### Manual Schema Changes
If you made manual database changes:
```bash
# Create a migration to match your changes
python -m alembic revision --autogenerate -m "Manual schema changes"
# Edit the generated migration file to match your manual changes
python -m alembic upgrade head
```

### Reset Migration History (Dangerous)
Only for development environments:
```bash
# This will mark current schema as baseline - USE WITH CAUTION
python -m alembic stamp head
```

## Common Alembic Commands

```bash
# View current revision
python -m alembic current

# View migration history
python -m alembic history

# Upgrade to specific revision
python -m alembic upgrade <revision_id>

# Downgrade to specific revision
python -m alembic downgrade <revision_id>

# Show all available heads
python -m alembic heads
``` 