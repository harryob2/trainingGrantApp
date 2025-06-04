@echo off
REM Training Form Application Management Script
REM Usage: manage_app.bat [start|stop|restart|status]

if "%1"=="" (
    echo Usage: manage_app.bat [start^|stop^|restart^|status]
    echo.
    echo Commands:
    echo   start   - Start the application service
    echo   stop    - Stop the application service  
    echo   restart - Restart the application service
    echo   status  - Check application status
    echo.
    pause
    exit /b 1
)

set ACTION=%1

echo Training Form Application Management
echo Action: %ACTION%
echo.

powershell.exe -ExecutionPolicy Bypass -File "scripts\manage_production_service.ps1" -Action %ACTION%

if errorlevel 1 (
    echo.
    echo ERROR: Operation failed
    pause
    exit /b 1
) else (
    echo.
    echo Operation completed successfully
    if "%ACTION%"=="status" pause
    exit /b 0
) 