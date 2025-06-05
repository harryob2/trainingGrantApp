# Training Form Application - Maintenance System

## Overview
Simple automated maintenance system that runs daily at 3:00 AM to keep the application running smoothly.

## What It Does
- **Database Backup**: Creates daily backups (keeps 180 days)
- **Record Cleanup**: Permanently deletes soft-deleted records older than 180 days

## Files Created
- `scripts/maintenance.py` - Main maintenance script
- `scripts/manage_maintenance.ps1` - PowerShell management interface
- `backups/` - Database backups folder (created automatically)

## Management Commands

### Via Batch File
```batch
manage_app.bat maintenance-install   # Install the scheduled task
manage_app.bat maintenance-status    # Check task status
manage_app.bat maintenance-run       # Run maintenance now
```

### Via PowerShell
```powershell
powershell -ExecutionPolicy Bypass -File "scripts\manage_maintenance.ps1" -Action install
powershell -ExecutionPolicy Bypass -File "scripts\manage_maintenance.ps1" -Action status
powershell -ExecutionPolicy Bypass -File "scripts\manage_maintenance.ps1" -Action run
```

## How It Works
1. **Environment Check**: Only runs when `FLASK_ENV=production`
2. **Database Backup**: 
   - SQLite: Copies database file
   - MariaDB: Uses mysqldump to create SQL backup
3. **Record Cleanup**: Deletes old soft-deleted records and their files
 4. **Cleanup**: Removes backups older than 180 days

## Installation
The maintenance task is automatically installed during production deployment. If needed, install manually:
```batch
manage_app.bat maintenance-install
```

## Scheduling
- Runs daily at 3:00 AM via Windows Task Scheduler
- Runs as NT AUTHORITY\SYSTEM for proper permissions
- Will restart automatically if it fails

## Safety Features
- Only runs in production environment
- Database operations use transactions
- Comprehensive error handling
- Simple logging to console

## Monitoring
Check the maintenance task status:
```batch
manage_app.bat maintenance-status
```

This shows:
- Task state (Ready/Running/Disabled)
- Last run time and result
- Next scheduled run time

---

The maintenance system is designed to be simple, reliable, and safe. It handles the essential tasks of backing up data and cleaning up old records without unnecessary complexity. 