#!/usr/bin/env powershell
# PowerShell script to export training catalog data

Write-Host "Exporting training catalog data from SQLite database..." -ForegroundColor Green

# Check if training_forms.db exists
if (-not (Test-Path "training_forms.db")) {
    Write-Host "Error: training_forms.db not found in current directory." -ForegroundColor Red
    Write-Host "Please run this script from the project root directory." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Try different Python commands
$pythonCommands = @("python", "py", "python3")
$success = $false

foreach ($cmd in $pythonCommands) {
    Write-Host "Trying $cmd..." -ForegroundColor Yellow
    try {
        $result = & $cmd "scripts/export_training_catalog.py" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host $result
            $success = $true
            break
        }
    }
    catch {
        continue
    }
}

if (-not $success) {
    Write-Host "Could not run Python script automatically." -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual options:" -ForegroundColor Yellow
    Write-Host "1. Try: python scripts/export_training_catalog.py"
    Write-Host "2. Use DB Browser for SQLite to export the training_catalog table"
    Write-Host "3. Use SQLite command line (see EXPORT_INSTRUCTIONS.md)"
    Write-Host ""
    Write-Host "The database has been renamed to:" -ForegroundColor Green
    Write-Host "- Production: training_tool_production" 
    Write-Host "- Staging: training_tool_staging"
    Write-Host ""
}
else {
    Write-Host ""
    Write-Host "Export completed successfully!" -ForegroundColor Green
    Write-Host "Files created:" -ForegroundColor Yellow
    Write-Host "- scripts/training_catalog_data.sql (SQL INSERT statements)"
    Write-Host "- scripts/training_catalog_export.csv (CSV backup)"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Green
    Write-Host "1. Run your MariaDB setup script (production or staging)"
    Write-Host "2. Then run: SOURCE scripts/training_catalog_data.sql;"
    Write-Host ""
}

Read-Host "Press Enter to exit" 