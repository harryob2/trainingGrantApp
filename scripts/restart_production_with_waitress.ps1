# PowerShell script to restart production service with Waitress
param(
    [switch]$Test,        # Run tests first
    [switch]$Install,     # Install Waitress if needed
    [switch]$Status       # Show status only
)

Write-Host "Production Service Restart with Waitress" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# Get current directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir

# Change to root directory
Set-Location $RootDir
Write-Host "Working directory: $(Get-Location)" -ForegroundColor Cyan

# Function to stop existing processes
function Stop-ExistingService {
    Write-Host "`nStopping existing production service..." -ForegroundColor Yellow
    
    # Stop processes using port 5000
    $procs = netstat -ano | Where-Object { $_ -match ":5000.*LISTENING" }
    if ($procs) {
        $processIds = ($procs | ForEach-Object { ($_ -split '\s+')[-1] }) | Sort-Object -Unique
        foreach ($processId in $processIds) {
            if ($processId -match '^\d+$') {
                Write-Host "Stopping process $processId using port 5000"
                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
            }
        }
    }
    
    # Also check for Flask processes
    $flaskProcesses = Get-WmiObject Win32_Process | Where-Object { 
        $_.CommandLine -and $_.CommandLine -match "start_production\.py"
    }
    
    if ($flaskProcesses) {
        Write-Host "Found Flask processes to stop:"
        $flaskProcesses | ForEach-Object { 
            Write-Host "  PID: $($_.ProcessId), Command: $($_.CommandLine)"
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        }
    }
    
    Start-Sleep -Seconds 3
    Write-Host "[OK] Service stop completed" -ForegroundColor Green
}

# Function to install Waitress
function Install-Waitress {
    Write-Host "`nInstalling Waitress..." -ForegroundColor Yellow
    try {
        pip install waitress==3.0.2
        Write-Host "[OK] Waitress installed successfully" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "[FAIL] Failed to install Waitress: $_" -ForegroundColor Red
        return $false
    }
}

# Function to test the setup
function Test-Setup {
    Write-Host "`nTesting Waitress setup..." -ForegroundColor Yellow
    
    try {
        $result = python "scripts\test_waitress.py"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Setup test passed" -ForegroundColor Green
            Write-Host $result
            return $true
        } else {
            Write-Host "[FAIL] Setup test failed" -ForegroundColor Red
            Write-Host $result
            return $false
        }
    } catch {
        Write-Host "[FAIL] Test script failed: $_" -ForegroundColor Red
        return $false
    }
}

# Function to start the service
function Start-ProductionService {
    Write-Host "`nStarting production service with Waitress..." -ForegroundColor Yellow
    
    # Set environment variables
    $env:FLASK_ENV = "production"
    $env:DEBUG = "False"
    $env:PYTHONUNBUFFERED = "1"
    
    $pythonExe = (Get-Command python).Path
    $startScript = "scripts\start_production.py"
    
    Write-Host "Python: $pythonExe"
    Write-Host "Script: $startScript"
    Write-Host "Environment: production"
    
    try {
        # Start in background
        $proc = Start-Process -FilePath $pythonExe -ArgumentList $startScript -WorkingDirectory (Get-Location) -WindowStyle Hidden -PassThru
        
        if ($proc) {
            Write-Host "[OK] Service started with PID: $($proc.Id)" -ForegroundColor Green
            $proc.Id | Out-File -FilePath "production_waitress.pid" -Force
            
            # Wait for service to start
            Write-Host "Waiting for service to start..."
            Start-Sleep -Seconds 15
            
            # Test connectivity
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:5000" -UseBasicParsing -TimeoutSec 10
                Write-Host "[OK] Service is responding (Status: $($response.StatusCode))" -ForegroundColor Green
                return $true
            } catch {
                Write-Host "[WARNING] Service started but not yet responding: $_" -ForegroundColor Yellow
                Write-Host "Give it a few more moments to fully initialize"
                return $true
            }
        } else {
            Write-Host "[FAIL] Failed to start service" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "[FAIL] Error starting service: $_" -ForegroundColor Red
        return $false
    }
}

# Function to show status
function Show-Status {
    Write-Host "`nProduction Service Status:" -ForegroundColor Cyan
    
    # Check for PID file
    if (Test-Path "production_waitress.pid") {
        $processId = Get-Content "production_waitress.pid"
        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "[OK] Service running (PID: $processId)" -ForegroundColor Green
        } else {
            Write-Host "[FAIL] PID file exists but process not running" -ForegroundColor Red
        }
    } else {
        Write-Host "- No PID file found" -ForegroundColor Yellow
    }
    
    # Check port 5000
    $listening = netstat -ano | Where-Object { $_ -match ":5000.*LISTENING" }
    if ($listening) {
        Write-Host "[OK] Port 5000 is listening" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Port 5000 is not listening" -ForegroundColor Red
    }
    
    # Test connectivity
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000" -UseBasicParsing -TimeoutSec 5
        Write-Host "[OK] Service responding (Status: $($response.StatusCode))" -ForegroundColor Green
    } catch {
        Write-Host "[FAIL] Service not responding: $_" -ForegroundColor Red
    }
}

# Main execution
try {
    if ($Status) {
        Show-Status
        exit 0
    }
    
    if ($Install) {
        $installResult = Install-Waitress
        if (-not $installResult) {
            Write-Host "Installation failed. Exiting." -ForegroundColor Red
            exit 1
        }
    }
    
    if ($Test) {
        $testResult = Test-Setup
        if (-not $testResult) {
            Write-Host "Tests failed. Please fix issues before proceeding." -ForegroundColor Red
            exit 1
        }
    }
    
    # Stop existing service
    Stop-ExistingService
    
    # Start new service
    $startResult = Start-ProductionService
    
    if ($startResult) {
        Write-Host "`n[SUCCESS] Production service restarted successfully with Waitress!" -ForegroundColor Green
        Write-Host "The Flask development server warning should no longer appear." -ForegroundColor Green
        Write-Host "`nService Management:" -ForegroundColor Cyan
        Write-Host "  Status: .\scripts\restart_production_with_waitress.ps1 -Status"
        Write-Host "  Restart: .\scripts\restart_production_with_waitress.ps1"
        Write-Host "  Test: .\scripts\restart_production_with_waitress.ps1 -Test"
    } else {
        Write-Host "`n❌ Failed to restart production service" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
} 