# Training Form Application Service Manager
# This script manages the Flask application as a Windows Scheduled Task

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "status", "install", "uninstall")]
    [string]$Action,
    
    [string]$WorkingDir = (Get-Location).Path,
    [string]$TaskName = "TrainingFormApp"
)

$ErrorActionPreference = "Stop"

# Set up error handling and verbose output
$VerbosePreference = "Continue"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message"
}

function Install-Service {
    Write-Log "Installing Training Form Application as scheduled task..."
    
    # Remove existing task if it exists
    try {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
        Write-Log "Removed existing task"
    } catch {
        Write-Log "No existing task to remove"
    }
    
    # Ensure we have absolute paths
    $absoluteWorkingDir = (Resolve-Path $WorkingDir).Path
    $pythonExe = (Get-Command python).Path
    $scriptPath = Join-Path $absoluteWorkingDir "scripts\start_production.py"
    
    Write-Log "Python executable: $pythonExe"
    Write-Log "Script path: $scriptPath"
    Write-Log "Working directory: $absoluteWorkingDir"
    
    # Verify script exists
    if (-not (Test-Path $scriptPath)) {
        Write-Log "ERROR: Start script not found at $scriptPath"
        throw "Start script not found"
    }
    
    # Create environment variables for the task
    $envVars = @{
        "FLASK_ENV" = "production"
        "PYTHONUNBUFFERED" = "1"
    }
    
    # Create task action with environment variables
    $action = New-ScheduledTaskAction -Execute $pythonExe -Argument "`"$scriptPath`"" -WorkingDirectory $absoluteWorkingDir
    
    # Create task trigger (at startup)
    $trigger = New-ScheduledTaskTrigger -AtStartup
    
    # Create task settings with better configuration
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -DontStopOnIdleEnd -ExecutionTimeLimit (New-TimeSpan -Days 365) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5)
    
    # Create task principal (run as SYSTEM with highest privileges)
    $principal = New-ScheduledTaskPrincipal -UserID "NT AUTHORITY\SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    
    # Register the task
    try {
        Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Training Form Flask Application"
        Write-Log "Task '$TaskName' installed successfully"
        
        # Verify the task was created
        $verifyTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($verifyTask) {
            Write-Log "Task verification successful - State: $($verifyTask.State)"
        } else {
            throw "Task was not created properly"
        }
        
        Write-Log "Python path: $pythonExe"
        Write-Log "Script path: $scriptPath"  
        Write-Log "Working directory: $absoluteWorkingDir"
        Write-Log "The application will start automatically on system boot"
        
    } catch {
        Write-Log "ERROR: Failed to register scheduled task: $($_.Exception.Message)"
        Write-Log "Full error: $_"
        throw $_
    }
}

function Uninstall-Service {
    Write-Log "Uninstalling Training Form Application service..."
    
    try {
        # Stop the task first
        Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        
        # Unregister the task
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Log "Service uninstalled successfully"
    } catch {
        Write-Log "Error uninstalling service: $_"
    }
}

function Start-Service {
    Write-Log "Starting Training Form Application..."
    
    try {
        # Check if task exists
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if (-not $task) {
            Write-Log "Task not found. Installing first..."
            Install-Service
        }
        
        # Start the task
        Start-ScheduledTask -TaskName $TaskName
        Write-Log "Service start command sent"
        
        # Wait a moment and check status
        Start-Sleep -Seconds 5
        Get-ServiceStatus
        
    } catch {
        Write-Log "Error starting service: $_"
    }
}

function Stop-Service {
    Write-Log "Stopping Training Form Application..."
    
    try {
        # Stop the scheduled task
        Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        
        # Also kill any Python processes running our script
        $processes = Get-WmiObject Win32_Process | Where-Object { 
            $_.CommandLine -and $_.CommandLine -match "start_production.py" 
        }
        
        foreach ($proc in $processes) {
            Write-Log "Stopping process PID: $($proc.ProcessId)"
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
        
        Write-Log "Service stopped"
        
    } catch {
        Write-Log "Error stopping service: $_"
    }
}

function Get-ServiceStatus {
    Write-Log "Checking Training Form Application status..."
    
    try {
        # Check scheduled task status
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task) {
            Write-Log "Scheduled Task Status: $($task.State)"
        } else {
            Write-Log "Scheduled Task: Not installed"
        }
        
        # Check if process is running
        $processes = Get-WmiObject Win32_Process | Where-Object { 
            $_.CommandLine -and $_.CommandLine -match "start_production.py" 
        }
        
        if ($processes) {
            foreach ($proc in $processes) {
                Write-Log "Flask Process: Running (PID: $($proc.ProcessId))"
            }
        } else {
            Write-Log "Flask Process: Not running"
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
        
    } catch {
        Write-Log "Error checking status: $_"
    }
}

function Restart-Service {
    Write-Log "Restarting Training Form Application..."
    Stop-Service
    Start-Sleep -Seconds 3
    Start-Service
}

# Main execution
switch ($Action.ToLower()) {
    "install" { Install-Service }
    "uninstall" { Uninstall-Service }
    "start" { Start-Service }
    "stop" { Stop-Service }
    "restart" { Restart-Service }
    "status" { Get-ServiceStatus }
}

Write-Log "Operation '$Action' completed" 