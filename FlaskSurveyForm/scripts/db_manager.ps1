# Database Management Script for Training Form Application
# Usage: .\db_manager.ps1 [command] [options]

param(
    [Parameter(Position=0)]
    [ValidateSet("migrate", "status", "create", "force-version", "setup", "backup", "help", "")]
    [string]$Command,
    
    [Parameter(Position=1)]
    [string]$Parameter
)

function Show-Help {
    Write-Host "Training Form Database Manager" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\db_manager.ps1 [command] [options]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Green
    Write-Host "  migrate                    - Run all pending migrations"
    Write-Host "  status                     - Show migration status"
    Write-Host "  create [migration_name]    - Create a new migration template"
    Write-Host "  force-version [number]     - Force set the current version"
    Write-Host "  setup                      - Set up initial database"
    Write-Host "  backup                     - Create database backup"
    Write-Host "  help                       - Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\db_manager.ps1 migrate"
    Write-Host "  .\db_manager.ps1 create add_new_column"
    Write-Host "  .\db_manager.ps1 status"
    Write-Host "  .\db_manager.ps1 force-version 3"
    Write-Host ""
}

function Invoke-Migration {
    Write-Host "Running database migrations..." -ForegroundColor Green
    python scripts/migrate_database.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Migrations completed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Migration failed" -ForegroundColor Red
        exit 1
    }
}

function Show-Status {
    Write-Host "Checking migration status..." -ForegroundColor Green
    python scripts/migrate_database.py --status
}

function New-Migration {
    param([string]$MigrationName)
    
    if (-not $MigrationName) {
        Write-Host "Error: Migration name required" -ForegroundColor Red
        Write-Host "Usage: .\db_manager.ps1 create [migration_name]" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "Creating migration template: $MigrationName" -ForegroundColor Green
    python scripts/migrate_database.py --create $MigrationName
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Migration template created successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create migration template" -ForegroundColor Red
        exit 1
    }
}

function Set-ForceVersion {
    param([string]$Version)
    
    if (-not $Version -or -not ($Version -match '^\d+$')) {
        Write-Host "Error: Valid version number required" -ForegroundColor Red
        Write-Host "Usage: .\db_manager.ps1 force-version [number]" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "Setting database version to $Version" -ForegroundColor Green
    python scripts/migrate_database.py --force-version $Version
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Version set successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to set version" -ForegroundColor Red
        exit 1
    }
}

function Initialize-Database {
    Write-Host "Setting up initial database..." -ForegroundColor Green
    python setup_db.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Database setup completed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Database setup failed" -ForegroundColor Red
        exit 1
    }
}

function New-Backup {
    Write-Host "Creating database backup..." -ForegroundColor Green
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    
    # Backup SQLite database
    if (Test-Path "training_forms.db") {
        $sqliteBackup = "training_forms_backup_$timestamp.db"
        Copy-Item "training_forms.db" $sqliteBackup
        Write-Host "✅ SQLite backup created: $sqliteBackup" -ForegroundColor Green
    }
    
    # Backup uploads directory
    if (Test-Path "uploads") {
        $uploadsBackup = "uploads_backup_$timestamp"
        Copy-Item "uploads" $uploadsBackup -Recurse
        Write-Host "✅ Uploads backup created: $uploadsBackup" -ForegroundColor Green
    }
    
    # Create migration backup info
    $backupInfo = @{
        timestamp = $timestamp
        database_backup = if (Test-Path "training_forms.db") { $sqliteBackup } else { $null }
        uploads_backup = if (Test-Path "uploads") { $uploadsBackup } else { $null }
        environment = $env:FLASK_ENV
    }
    
    $backupInfoFile = "backup_info_$timestamp.json"
    $backupInfo | ConvertTo-Json | Out-File $backupInfoFile
    Write-Host "✅ Backup info saved: $backupInfoFile" -ForegroundColor Green
}

# Main script logic
switch ($Command) {
    "migrate" {
        Invoke-Migration
    }
    "status" {
        Show-Status
    }
    "create" {
        New-Migration -MigrationName $Parameter
    }
    "force-version" {
        Set-ForceVersion -Version $Parameter
    }
    "setup" {
        Initialize-Database
    }
    "backup" {
        New-Backup
    }
    "help" {
        Show-Help
    }
    default {
        if (-not $Command) {
            Show-Help
        } else {
            Write-Host "Unknown command: $Command" -ForegroundColor Red
            Write-Host "Run '.\db_manager.ps1 help' for usage information" -ForegroundColor Yellow
            exit 1
        }
    }
}

Write-Host ""
Write-Host "Database management completed." -ForegroundColor Cyan 