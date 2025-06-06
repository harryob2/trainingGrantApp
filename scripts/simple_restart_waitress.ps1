# Simple PowerShell script to restart production service with Waitress
param(
    [switch]$Status
)

Write-Host "Production Service Restart with Waitress" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

# Get root directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
Set-Location $RootDir

Write-Host "Working directory: $(Get-Location)" -ForegroundColor Cyan

if ($Status) {
    Write-Host "`nChecking service status..." -ForegroundColor Yellow
    
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
    exit 0
}

Write-Host "`nStopping existing services..." -ForegroundColor Yellow

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

Start-Sleep -Seconds 3

Write-Host "`nStarting production service with Waitress..." -ForegroundColor Yellow

# Set environment variables
$env:FLASK_ENV = "production"
$env:DEBUG = "False"
$env:PYTHONUNBUFFERED = "1"

$pythonExe = (Get-Command python).Path
$startScript = "scripts\start_production.py"

Write-Host "Python: $pythonExe"
Write-Host "Script: $startScript"

try {
    # Start in background
    $proc = Start-Process -FilePath $pythonExe -ArgumentList $startScript -WorkingDirectory (Get-Location) -WindowStyle Hidden -PassThru
    
    if ($proc) {
        Write-Host "[OK] Service started with PID: $($proc.Id)" -ForegroundColor Green
        $proc.Id | Out-File -FilePath "production_waitress.pid" -Force
        
        Write-Host "Waiting for service to start..."
        Start-Sleep -Seconds 15
        
        # Test connectivity
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:5000" -UseBasicParsing -TimeoutSec 10
            Write-Host "[OK] Service is responding (Status: $($response.StatusCode))" -ForegroundColor Green
            Write-Host "`n[SUCCESS] Production service restarted successfully with Waitress!" -ForegroundColor Green
            Write-Host "The Flask development server warning should no longer appear." -ForegroundColor Green
        } catch {
            Write-Host "[WARNING] Service started but not yet responding: $_" -ForegroundColor Yellow
            Write-Host "Give it a few more moments to fully initialize"
        }
    } else {
        Write-Host "[FAIL] Failed to start service" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[FAIL] Error starting service: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`nService Management Commands:" -ForegroundColor Cyan
Write-Host "  Status: .\scripts\simple_restart_waitress.ps1 -Status"
Write-Host "  Restart: .\scripts\simple_restart_waitress.ps1" 