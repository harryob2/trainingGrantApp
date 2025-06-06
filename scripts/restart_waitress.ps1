# Simple script to restart Flask with Waitress production server
param([switch]$Status)

$RootDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RootDir

if ($Status) {
    # Just check if service is running
    $listening = netstat -ano | Where-Object { $_ -match ":5000.*LISTENING" }
    if ($listening) {
        Write-Host "[OK] Service running on port 5000" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] No service on port 5000" -ForegroundColor Red
    }
    exit 0
}

Write-Host "Restarting Flask with Waitress..." -ForegroundColor Yellow

# Stop existing processes on port 5000
$procs = netstat -ano | Where-Object { $_ -match ":5000.*LISTENING" }
if ($procs) {
    $processIds = ($procs | ForEach-Object { ($_ -split '\s+')[-1] }) | Sort-Object -Unique
    foreach ($pid in $processIds) {
        if ($pid -match '^\d+$') {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        }
    }
    Start-Sleep -Seconds 2
}

# Start with Waitress
$env:FLASK_ENV = "production"
$env:DEBUG = "False"
Start-Process python -ArgumentList "scripts\start_production.py" -WindowStyle Hidden

Write-Host "[OK] Service restarted with Waitress" -ForegroundColor Green
Write-Host "Use: .\scripts\restart_waitress.ps1 -Status to check status" 