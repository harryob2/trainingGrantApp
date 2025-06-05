# Unified Production Management Script
# Handles both Windows Scheduled Task services and direct Python processes

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "status")]
    [string]$Action,
    
    [string]$WorkingDir = (Get-Location).Path
)

$ErrorActionPreference = "Continue"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message"
}

function Get-UnifiedStatus {
    Write-Log "Checking Training Form Application status..."
    
    $isRunning = $false
    $method = "None"
    $processId = $null
    
    # Check scheduled task
    $task = Get-ScheduledTask -TaskName "TrainingFormApp" -ErrorAction SilentlyContinue
    if ($task) {
        Write-Log "Scheduled Task Status: $($task.State)"
        if ($task.State -eq "Running") {
            $method = "Scheduled Task"
            $isRunning = $true
        }
    } else {
        Write-Log "Scheduled Task: Not installed"
    }
    
    # Check direct process via PID file
    if (Test-Path "production_direct.pid") {
        $directPid = Get-Content "production_direct.pid" -ErrorAction SilentlyContinue
        if ($directPid) {
            $directProcess = Get-Process -Id $directPid -ErrorAction SilentlyContinue
            if ($directProcess) {
                Write-Log "Direct Process: Running (PID: $directPid)"
                $method = "Direct Process"
                $processId = $directPid
                $isRunning = $true
            } else {
                Write-Log "Direct Process: PID file exists but process not running"
            }
        }
    }
    
    # Check for any Python processes running our script
    $processes = Get-WmiObject Win32_Process | Where-Object { 
        $_.CommandLine -and $_.CommandLine -match "start_production.py" 
    }
    
    if ($processes) {
        foreach ($proc in $processes) {
            Write-Log "Flask Process Found: PID $($proc.ProcessId)"
            if (-not $isRunning) {
                $method = "Unknown Process"
                $processId = $proc.ProcessId
                $isRunning = $true
            }
        }
    }
    
    # Check port 5000
    $listening = netstat -ano | Where-Object { $_ -match ":5000.*LISTENING" }
    if ($listening) {
        Write-Log "Port 5000: Listening"
        $listening | ForEach-Object { Write-Log "  $_" }
    } else {
        Write-Log "Port 5000: Not listening"
    }
    
    # Test HTTP connectivity
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        Write-Log "HTTP Test: SUCCESS (Status: $($response.StatusCode))"
    } catch {
        Write-Log "HTTP Test: FAILED ($($_.Exception.Message))"
    }
    
    return @{
        IsRunning = $isRunning
        Method = $method
        ProcessId = $processId
    }
}

function Start-Application {
    Write-Log "Starting Training Form Application..."
    
    $status = Get-UnifiedStatus
    if ($status.IsRunning) {
        Write-Log "Application is already running via $($status.Method)"
        return
    }
    
    # Try scheduled task first
    $task = Get-ScheduledTask -TaskName "TrainingFormApp" -ErrorAction SilentlyContinue
    if ($task) {
        try {
            Start-ScheduledTask -TaskName "TrainingFormApp"
            Write-Log "Scheduled task started"
            Start-Sleep -Seconds 5
            $newStatus = Get-UnifiedStatus
            if ($newStatus.IsRunning) {
                Write-Log "SUCCESS: Application started via scheduled task"
                return
            }
        } catch {
            Write-Log "Failed to start scheduled task: $_"
        }
    }
    
    # Fallback to direct startup
    Write-Log "Starting application directly..."
    
    $pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Path
    if (-not $pythonExe) {
        Write-Log "ERROR: Python executable not found"
        return
    }
    
    $startScript = Join-Path $WorkingDir "scripts\start_production.py"
    if (-not (Test-Path $startScript)) {
        Write-Log "ERROR: Start script not found at $startScript"
        return
    }
    
    # Set environment variables
    $env:FLASK_ENV = "production"
    $env:PYTHONUNBUFFERED = "1"
    
    try {
        $proc = Start-Process -FilePath $pythonExe -ArgumentList "`"$startScript`"" -WorkingDirectory $WorkingDir -WindowStyle Hidden -PassThru
        
        if ($proc -and $proc.Id) {
            $proc.Id | Out-File -FilePath "production_direct.pid" -Force
            Write-Log "SUCCESS: Application started directly (PID: $($proc.Id))"
            
            Start-Sleep -Seconds 5
            $newStatus = Get-UnifiedStatus
            if ($newStatus.IsRunning) {
                Write-Log "Application is running and responding"
            } else {
                Write-Log "WARNING: Application may not have started properly"
            }
        } else {
            Write-Log "ERROR: Failed to start application process"
        }
    } catch {
        Write-Log "ERROR: Exception during startup: $_"
    }
}

function Stop-Application {
    Write-Log "Stopping Training Form Application..."
    
    # Stop scheduled task
    try {
        Stop-ScheduledTask -TaskName "TrainingFormApp" -ErrorAction SilentlyContinue
        Write-Log "Scheduled task stopped"
    } catch {
        Write-Log "No scheduled task to stop or failed to stop: $_"
    }
    
    # Stop direct process
    if (Test-Path "production_direct.pid") {
        $directPid = Get-Content "production_direct.pid" -ErrorAction SilentlyContinue
        if ($directPid) {
            $directProcess = Get-Process -Id $directPid -ErrorAction SilentlyContinue
            if ($directProcess) {
                Stop-Process -Id $directPid -Force -ErrorAction SilentlyContinue
                Write-Log "Direct process stopped (PID: $directPid)"
            }
        }
        Remove-Item "production_direct.pid" -ErrorAction SilentlyContinue
    }
    
    # Kill any Python processes running our script
    $processes = Get-WmiObject Win32_Process | Where-Object { 
        $_.CommandLine -and $_.CommandLine -match "start_production.py" 
    }
    
    foreach ($proc in $processes) {
        Write-Log "Stopping Flask process PID: $($proc.ProcessId)"
        Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
    }
    
    # Kill any processes on port 5000
    $netstatOutput = netstat -ano | Where-Object { $_ -match ":5000.*LISTENING" }
    if ($netstatOutput) {
        $processIds = ($netstatOutput | ForEach-Object { ($_ -split '\s+')[-1] }) | Sort-Object -Unique
        foreach ($processId in $processIds) {
            if ($processId -match '^\d+$') {
                Write-Log "Stopping process on port 5000, PID: $processId"
                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
            }
        }
    }
    
    Write-Log "Application stopped"
}

function Restart-Application {
    Write-Log "Restarting Training Form Application..."
    Stop-Application
    Start-Sleep -Seconds 3
    Start-Application
}

# Main execution
switch ($Action.ToLower()) {
    "start" { Start-Application }
    "stop" { Stop-Application }
    "restart" { Restart-Application }
    "status" { $status = Get-UnifiedStatus; Write-Log "Status check completed" }
}

Write-Log "Operation '$Action' completed" 