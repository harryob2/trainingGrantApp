# Simple maintenance task manager for Training Form Application

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("status", "run", "install")]
    [string]$Action
)

$TaskName = "TrainingFormMaintenance"

function Install-MaintenanceTask {
    Write-Host "Installing maintenance scheduled task..."
    
    # Remove existing task
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    
    # Get paths
    $pythonExe = (Get-Command python).Path
    $scriptPath = Join-Path (Get-Location) "scripts\maintenance.py"
    
    # Verify script exists
    if (-not (Test-Path $scriptPath)) {
        Write-Host "ERROR: Maintenance script not found" -ForegroundColor Red
        exit 1
    }
    
    # Create task
    $action = New-ScheduledTaskAction -Execute $pythonExe -Argument "`"$scriptPath`"" -WorkingDirectory (Get-Location)
    $trigger = New-ScheduledTaskTrigger -Daily -At "03:00"
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -StartWhenAvailable
    $principal = New-ScheduledTaskPrincipal -UserID "NT AUTHORITY\SYSTEM" -LogonType ServiceAccount -RunLevel Highest
    
    # Register task
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Daily maintenance at 3:00 AM"
    
    Write-Host "Maintenance task installed successfully" -ForegroundColor Green
    Write-Host "Will run daily at 3:00 AM"
}

function Get-MaintenanceStatus {
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    
    if ($task) {
        $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
        
        Write-Host ""
        Write-Host "=== MAINTENANCE TASK STATUS ===" -ForegroundColor Green
        Write-Host "State: $($task.State)"
        Write-Host "Last Run: $($taskInfo.LastRunTime)"
        Write-Host "Last Result: $($taskInfo.LastTaskResult)"
        Write-Host "Next Run: $($taskInfo.NextRunTime)"
    } else {
        Write-Host "MAINTENANCE TASK NOT FOUND" -ForegroundColor Red
        Write-Host "Use: manage_app.bat maintenance-install"
    }
}

function Start-MaintenanceTask {
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    
    if (-not $task) {
        Write-Host "Task not found. Installing first..." -ForegroundColor Yellow
        Install-MaintenanceTask
    }
    
    Start-ScheduledTask -TaskName $TaskName
    Write-Host "Maintenance task started" -ForegroundColor Green
}

# Main execution
switch ($Action.ToLower()) {
    "install" { Install-MaintenanceTask }
    "status" { Get-MaintenanceStatus }
    "run" { Start-MaintenanceTask }
} 