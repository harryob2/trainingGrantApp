# Training Form Application Environment Switcher
# Usage: .\switch_environment.ps1 [development|production]

param(
    [Parameter(Position=0)]
    [ValidateSet("development", "production", "")]
    [string]$Environment
)

function Show-Usage {
    Write-Host "Usage: .\switch_environment.ps1 [development|production]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Current environment files:" -ForegroundColor Cyan
    
    if (Test-Path ".env.development") {
        Write-Host "  - .env.development [EXISTS]" -ForegroundColor Green
    } else {
        Write-Host "  - .env.development [MISSING]" -ForegroundColor Red
    }
    
    if (Test-Path ".env.production") {
        Write-Host "  - .env.production [EXISTS]" -ForegroundColor Green
    } else {
        Write-Host "  - .env.production [MISSING]" -ForegroundColor Red
    }
    
    if (Test-Path ".env") {
        Write-Host "  - .env [CURRENT]" -ForegroundColor Green
    } else {
        Write-Host "  - .env [NOT SET]" -ForegroundColor Yellow
    }
}

if (-not $Environment) {
    Show-Usage
    exit 1
}

switch ($Environment) {
    "development" {
        if (-not (Test-Path ".env.development")) {
            Write-Host "Error: .env.development file not found" -ForegroundColor Red
            Write-Host "Run: python scripts/setup_environment.py" -ForegroundColor Yellow
            exit 1
        }
        
        Copy-Item ".env.development" ".env" -Force
        $env:FLASK_ENV = "development"
        
        Write-Host "Switched to DEVELOPMENT environment" -ForegroundColor Green
        Write-Host "Database: SQLite" -ForegroundColor Cyan
        Write-Host "Debug: Enabled" -ForegroundColor Cyan
    }
    
    "production" {
        if (-not (Test-Path ".env.production")) {
            Write-Host "Error: .env.production file not found" -ForegroundColor Red
            Write-Host "Run: python scripts/setup_environment.py" -ForegroundColor Yellow
            exit 1
        }
        
        Copy-Item ".env.production" ".env" -Force
        $env:FLASK_ENV = "production"
        
        Write-Host "Switched to PRODUCTION environment" -ForegroundColor Green
        Write-Host "Database: MariaDB" -ForegroundColor Cyan
        Write-Host "Debug: Disabled" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "WARNING: Make sure MariaDB is set up and accessible!" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Environment variables set for current session." -ForegroundColor Cyan
Write-Host "To start the application: python main.py" -ForegroundColor Green 