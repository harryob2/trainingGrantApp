# Training Catalog Data Export Instructions

This document explains how to export your local training catalog data for use in the MariaDB production and staging databases.

## Automated Export (Try First)

### Option 1: Run the Export Script
Try running the export script with any of these commands:

```batch
# Windows Command Prompt
python scripts/export_training_catalog.py

# Or try these alternatives:
py scripts/export_training_catalog.py
python3 scripts/export_training_catalog.py
uv run python scripts/export_training_catalog.py
```

### Option 2: Run the Batch Script
```batch
scripts\export_data.bat
```

If successful, this will create:
- `scripts/training_catalog_data.sql` - SQL INSERT statements for MariaDB
- `scripts/training_catalog_export.csv` - CSV backup file

## Manual Export (If Automated Fails)

### Method 1: Using SQLite Command Line

1. Open Command Prompt in your project directory
2. Run SQLite with your database:
```batch
sqlite3 training_forms.db
```

3. Export to CSV:
```sql
.headers on
.mode csv
.output scripts/training_catalog_export.csv
SELECT area, training_name, qty_staff_attending, training_desc, 
       challenge_lvl, skill_impact, evaluation_method, ida_class, 
       training_type, training_hours, supplier_name, course_cost
FROM training_catalog 
ORDER BY id;
.quit
```

### Method 2: Using DB Browser for SQLite

1. Download and install [DB Browser for SQLite](https://sqlitebrowser.org/)
2. Open your `training_forms.db` file
3. Go to the "Browse Data" tab
4. Select the `training_catalog` table
5. Click "File" → "Export" → "Table(s) as CSV"
6. Export the data to `scripts/training_catalog_export.csv`

## Converting CSV to SQL

Once you have the CSV file, you can convert it to SQL INSERT statements:

1. Open the CSV file in Excel or a text editor
2. Create SQL INSERT statements manually, or 
3. Use the template in `scripts/training_catalog_data_template.sql`

## Updated Database Setup

The MariaDB setup scripts have been updated:

### Production Database: `scripts/setup_mariadb_production.sql`
- Database name: `training_tool_production`
- Includes placeholder for training catalog data

### Staging Database: `scripts/setup_mariadb_staging.sql`
- Database name: `training_tool_staging`
- Includes placeholder for training catalog data

## Running the Setup

1. **First**, run the main setup script:
   ```sql
   SOURCE scripts/setup_mariadb_production.sql;
   -- or
   SOURCE scripts/setup_mariadb_staging.sql;
   ```

2. **Then**, import the training catalog data:
   ```sql
   SOURCE scripts/training_catalog_data.sql;
   ```

## Database Names Summary

- **Production**: `training_tool_production`
- **Staging**: `training_tool_staging`

Both databases will have identical structure and training catalog data. 