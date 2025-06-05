# Production Troubleshooting Script
# This script helps diagnose and fix common production deployment issues

param(
    [string]$Action = "all",
    [string]$WorkingDir = (Get-Location).Path
)

$ErrorActionPreference = "Continue"

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host $Title.ToUpper() -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
}

function Test-PythonEnvironment {
    Write-Section "Testing Python Environment"
    
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✓ Python version: $pythonVersion" -ForegroundColor Green
        
        $pythonPath = (Get-Command python).Path
        Write-Host "✓ Python executable: $pythonPath" -ForegroundColor Green
        
        # Test Python can import basic modules
        $testImport = python -c "import sys, os, flask; print('Basic imports OK')" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Basic Python imports working" -ForegroundColor Green
        } else {
            Write-Host "✗ Python import test failed: $testImport" -ForegroundColor Red
        }
        
    } catch {
        Write-Host "✗ Python not found or not working: $_" -ForegroundColor Red
    }
}

function Test-FileStructure {
    Write-Section "Testing File Structure"
    
    $currentDir = Get-Location
    Write-Host "Current directory: $currentDir"
    
    $requiredFiles = @(
        "app.py",
        "config.py", 
        "models.py",
        "forms.py",
        "auth.py",
        "setup_db.py",
        "requirements.txt",
        ".env",
        "scripts\start_production.py",
        "scripts\manage_production_service.ps1"
    )
    
    $missingFiles = @()
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-Host "✓ $file" -ForegroundColor Green
        } else {
            Write-Host "✗ $file - MISSING" -ForegroundColor Red
            $missingFiles += $file
        }
    }
    
    if ($missingFiles.Count -gt 0) {
        Write-Host "`nMissing files: $($missingFiles -join ', ')" -ForegroundColor Red
        return $false
    } else {
        Write-Host "`nAll required files found!" -ForegroundColor Green
        return $true
    }
}

function Test-EnvironmentVariables {
    Write-Section "Testing Environment Variables"
    
    # Check if .env file exists and load it
    if (Test-Path ".env") {
        Write-Host "✓ .env file found" -ForegroundColor Green
        
        # Read .env file contents
        $envContent = Get-Content ".env"
        Write-Host "Environment file contents:"
        foreach ($line in $envContent) {
            if ($line -match "PASSWORD|SECRET") {
                $displayLine = $line -replace "=.*", "=***"
                Write-Host "  $displayLine" -ForegroundColor Yellow
            } else {
                Write-Host "  $line" -ForegroundColor Gray
            }
        }
    } else {
        Write-Host "✗ .env file not found" -ForegroundColor Red
    }
    
    # Check important environment variables
    $importantVars = @("FLASK_ENV", "SECRET_KEY", "DEBUG", "USE_SQLITE", "DB_HOST")
    foreach ($var in $importantVars) {
        $value = [Environment]::GetEnvironmentVariable($var)
        if ($value) {
            if ($var -match "PASSWORD|SECRET") {
                Write-Host "✓ $var is set (***)" -ForegroundColor Green
            } else {
                Write-Host "✓ $var = $value" -ForegroundColor Green
            }
        } else {
            Write-Host "⚠ $var is not set" -ForegroundColor Yellow
        }
    }
}

function Test-PythonDiagnostics {
    Write-Section "Running Python Diagnostics"
    
    if (Test-Path "scripts\diagnose_production.py") {
        Write-Host "Running diagnostic script..."
        python scripts\diagnose_production.py
    } else {
        Write-Host "✗ Diagnostic script not found" -ForegroundColor Red
    }
}

function Test-ManualFlaskStart {
    Write-Section "Testing Manual Flask Start"
    
    Write-Host "Testing if Flask app can be imported and started manually..."
    
    # Test import first
    $importTest = python -c "import sys, os; os.chdir('.'); sys.path.insert(0, '.'); from app import app; print('Flask import successful')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Flask app can be imported" -ForegroundColor Green
        Write-Host $importTest
    } else {
        Write-Host "✗ Flask app import failed: $importTest" -ForegroundColor Red
        return $false
    }
    
    # Test production script
    if (Test-Path "scripts\start_production.py") {
        Write-Host "`nTesting production start script (will run for 10 seconds)..."
        
        # Start the script in background
        $job = Start-Job -ScriptBlock {
            param($WorkDir)
            Set-Location $WorkDir
            python scripts\start_production.py
        } -ArgumentList (Get-Location)
        
        # Wait a few seconds
        Start-Sleep -Seconds 10
        
        # Check if job is still running
        if ($job.State -eq "Running") {
            Write-Host "✓ Production script started successfully" -ForegroundColor Green
            Stop-Job $job
            Remove-Job $job
            return $true
        } else {
            Write-Host "✗ Production script failed to start" -ForegroundColor Red
            Receive-Job $job
            Remove-Job $job
            return $false
        }
    } else {
        Write-Host "✗ Production start script not found" -ForegroundColor Red
        return $false
    }
}

function Test-ServiceManagement {
    Write-Section "Testing Service Management"
    
    if (Test-Path "scripts\manage_production_service.ps1") {
        Write-Host "Testing service management script..."
        
        # Test script can be loaded
        try {
            . "scripts\manage_production_service.ps1" -Action status -WorkingDir (Get-Location)
        } catch {
            Write-Host "✗ Service management script failed: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "✗ Service management script not found" -ForegroundColor Red
    }
}

function Test-PortAvailability {
    Write-Section "Testing Port Availability"
    
    # Check if port 5000 is available
    try {
        $socket = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Any, 5000)
        $socket.Start()
        $socket.Stop()
        Write-Host "✓ Port 5000 is available" -ForegroundColor Green
    } catch {
        Write-Host "✗ Port 5000 is not available: $_" -ForegroundColor Red
        
        # Show what's using the port
        $processesOnPort = netstat -ano | Where-Object { $_ -match ":5000" }
        if ($processesOnPort) {
            Write-Host "Processes using port 5000:"
            $processesOnPort | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
        }
    }
}

function Fix-CommonIssues {
    Write-Section "Attempting to Fix Common Issues"
    
    # Stop any existing processes on port 5000
    Write-Host "Stopping any existing processes on port 5000..."
    $processesOnPort = netstat -ano | Where-Object { $_ -match ":5000.*LISTENING" }
    if ($processesOnPort) {
        $processIds = ($processesOnPort | ForEach-Object { ($_ -split '\s+')[-1] }) | Sort-Object -Unique
        foreach ($processId in $processIds) {
            if ($processId -match '^\d+$') {
                Write-Host "  Stopping process PID: $processId"
                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
            }
        }
    }
    
    # Remove any existing scheduled tasks
    Write-Host "Removing any existing scheduled tasks..."
    try {
        Unregister-ScheduledTask -TaskName "TrainingFormApp" -Confirm:$false -ErrorAction SilentlyContinue
        Write-Host "✓ Existing scheduled task removed" -ForegroundColor Green
    } catch {
        Write-Host "  No existing scheduled task found"
    }
    
    # Create uploads directory if missing
    if (!(Test-Path "uploads")) {
        Write-Host "Creating uploads directory..."
        New-Item -ItemType Directory -Path "uploads" -Force
        Write-Host "✓ Uploads directory created" -ForegroundColor Green
    }
    
    Write-Host "Common issue fixes completed"
}

function Show-Summary {
    Write-Section "Troubleshooting Summary"
    
    Write-Host "If you're still having issues, try these steps:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Manual Test:" -ForegroundColor White
    Write-Host "   python scripts\test_production_manual.py"
    Write-Host ""
    Write-Host "2. Direct Start (for testing):" -ForegroundColor White  
    Write-Host "   python scripts\start_production.py"
    Write-Host ""
    Write-Host "3. Service Management:" -ForegroundColor White
    Write-Host "   powershell -File scripts\manage_production_service.ps1 -Action status"
    Write-Host "   powershell -File scripts\manage_production_service.ps1 -Action restart"
    Write-Host ""
    Write-Host "4. Check logs:" -ForegroundColor White
    Write-Host "   Get-Content production.log -Tail 20"
    Write-Host ""
    Write-Host "5. Re-run deployment:" -ForegroundColor White
    Write-Host "   Use GitHub Actions to deploy again with the fixes"
}

# Main execution
switch ($Action.ToLower()) {
    "all" {
        Test-PythonEnvironment
        Test-FileStructure
        Test-EnvironmentVariables
        Test-PythonDiagnostics
        Test-PortAvailability
        Test-ManualFlaskStart
        Test-ServiceManagement
        Show-Summary
    }
    "python" { Test-PythonEnvironment }
    "files" { Test-FileStructure }
    "env" { Test-EnvironmentVariables }
    "diagnostics" { Test-PythonDiagnostics }
    "flask" { Test-ManualFlaskStart }
    "service" { Test-ServiceManagement }
    "port" { Test-PortAvailability }
    "fix" { Fix-CommonIssues }
    "summary" { Show-Summary }
    default {
        Write-Host "Usage: .\troubleshoot_production.ps1 -Action <all|python|files|env|diagnostics|flask|service|port|fix|summary>"
    }
} 