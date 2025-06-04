# Training Form Application Service Management

This document explains how to manage the Training Form Flask application as a Windows service.

## Automatic Deployment

When you commit to GitHub, the application will automatically:
1. Deploy to the target server
2. Install as a Windows Scheduled Task
3. Start automatically on system boot
4. Run persistently in the background

## Manual Service Management

### Using the Batch File (Easiest)

```cmd
# Check application status
manage_app.bat status

# Start the application
manage_app.bat start

# Stop the application
manage_app.bat stop

# Restart the application
manage_app.bat restart
```

### Using PowerShell Directly

```powershell
# Check application status
powershell -ExecutionPolicy Bypass -File "scripts\manage_production_service.ps1" -Action status

# Start the application
powershell -ExecutionPolicy Bypass -File "scripts\manage_production_service.ps1" -Action start

# Stop the application
powershell -ExecutionPolicy Bypass -File "scripts\manage_production_service.ps1" -Action stop

# Restart the application
powershell -ExecutionPolicy Bypass -File "scripts\manage_production_service.ps1" -Action restart

# Install as Windows service
powershell -ExecutionPolicy Bypass -File "scripts\manage_production_service.ps1" -Action install

# Uninstall the Windows service
powershell -ExecutionPolicy Bypass -File "scripts\manage_production_service.ps1" -Action uninstall
```

### Using Python Directly (Emergency)

If the service management fails, you can start the application directly:

```cmd
python scripts\start_production.py
```

Or with the original main.py:

```cmd
python main.py --host 0.0.0.0 --port 5000 --no-debug
```

## Application Access

After deployment, the application will be accessible at:
- `http://localhost:5000` (local access)
- `http://azulimpbi01:5000` (network access)
- `http://[SERVER-IP]:5000` (IP access)

## Service Details

The application runs as:
- **Service Name**: TrainingFormApp
- **Type**: Windows Scheduled Task
- **Startup**: Automatic (runs at system boot)
- **User**: NT AUTHORITY\SYSTEM
- **Port**: 5000
- **Log File**: `production.log`
- **PID File**: `production_flask.pid`

## Troubleshooting

### Application Won't Start

1. Check the service status:
   ```cmd
   manage_app.bat status
   ```

2. Check the log file:
   ```cmd
   type production.log
   ```

3. Check if port 5000 is in use:
   ```cmd
   netstat -ano | findstr :5000
   ```

4. Restart the service:
   ```cmd
   manage_app.bat restart
   ```

### Port 5000 Already in Use

1. Stop any existing processes:
   ```cmd
   manage_app.bat stop
   ```

2. Kill processes manually if needed:
   ```cmd
   netstat -ano | findstr :5000
   taskkill /PID [PID_NUMBER] /F
   ```

3. Start the service:
   ```cmd
   manage_app.bat start
   ```

### Service Won't Install

1. Run as Administrator:
   - Right-click Command Prompt → "Run as administrator"
   - Run: `manage_app.bat install`

2. Check Windows Task Scheduler:
   - Open Task Scheduler (taskschd.msc)
   - Look for "TrainingFormApp" task

### Firewall Issues

If the application is not accessible from other machines:

1. Check Windows Firewall rules:
   ```powershell
   Get-NetFirewallRule -DisplayName "Flask Training App Port 5000"
   ```

2. Add firewall rule manually:
   ```powershell
   New-NetFirewallRule -DisplayName "Flask Training App Port 5000" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
   ```

## Logs and Monitoring

- **Application Log**: `production.log`
- **Process ID**: Stored in `production_flask.pid`
- **Windows Event Log**: Check Application and System logs
- **Task Scheduler**: View task history and status

## Support

For issues with the service management:
1. Check the logs first
2. Try restarting the service
3. Verify the database connection
4. Check for port conflicts
5. Ensure proper file permissions 