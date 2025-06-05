@echo off
setlocal enabledelayedexpansion

if "%1"=="" (
    echo Usage: manage_app.bat [command]
    echo.
    echo Available commands:
    echo   dev                    - Start development server
    echo   prod                   - Start production service
    echo   stop                   - Stop production service
    echo   restart                - Restart production service
    echo   logs                   - View production service logs
    echo   status                 - Check production service status
    echo   setup                  - Setup database and environment
    echo   backup                 - Create database backup
    echo   maintenance-status     - Check maintenance task status
    echo   maintenance-run        - Run maintenance task now
    echo   maintenance-install    - Install maintenance task
    echo.
    exit /b 1
)

set COMMAND=%1

if "%COMMAND%"=="dev" (
    echo Starting development server...
    python app.py
)

if "%COMMAND%"=="prod" (
    echo Starting production service...
    powershell -ExecutionPolicy Bypass -File "scripts\manage_production_service.ps1" -Action start
)

if "%COMMAND%"=="stop" (
    echo Stopping production service...
    powershell -ExecutionPolicy Bypass -File "scripts\manage_production_service.ps1" -Action stop
)

if "%COMMAND%"=="restart" (
    echo Restarting production service...
    powershell -ExecutionPolicy Bypass -File "scripts\manage_production_service.ps1" -Action restart
)

if "%COMMAND%"=="logs" (
    echo Viewing production service logs...
    powershell -ExecutionPolicy Bypass -File "scripts\manage_production_service.ps1" -Action logs
)

if "%COMMAND%"=="status" (
    echo Checking production service status...
    powershell -ExecutionPolicy Bypass -File "scripts\manage_production_service.ps1" -Action status
)

if "%COMMAND%"=="setup" (
    echo Setting up database and environment...
    python setup_db.py
)

if "%COMMAND%"=="backup" (
    echo Creating database backup...
    python -c "from scripts.maintenance import backup_database; backup_database()"
)

if "%COMMAND%"=="maintenance-status" (
    powershell -ExecutionPolicy Bypass -File "scripts\manage_maintenance.ps1" -Action status
)

if "%COMMAND%"=="maintenance-run" (
    powershell -ExecutionPolicy Bypass -File "scripts\manage_maintenance.ps1" -Action run
)

if "%COMMAND%"=="maintenance-install" (
    powershell -ExecutionPolicy Bypass -File "scripts\manage_maintenance.ps1" -Action install
)

echo Done. 