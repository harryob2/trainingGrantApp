@echo off
REM Training Form Application Environment Switcher
REM Usage: switch_environment.cmd [development|production]

if "%1"=="" (
    echo Usage: switch_environment.cmd [development^|production]
    echo.
    echo Current environment files:
    if exist .env.development echo   - .env.development [EXISTS]
    if not exist .env.development echo   - .env.development [MISSING]
    if exist .env.production echo   - .env.production [EXISTS]  
    if not exist .env.production echo   - .env.production [MISSING]
    if exist .env echo   - .env [CURRENT]
    if not exist .env echo   - .env [NOT SET]
    exit /b 1
)

if "%1"=="development" (
    if not exist .env.development (
        echo Error: .env.development file not found
        echo Run: python scripts/setup_environment.py
        exit /b 1
    )
    copy .env.development .env >nul
    set FLASK_ENV=development
    echo Switched to DEVELOPMENT environment
    echo Database: SQLite
    echo Debug: Enabled
    goto end
)

if "%1"=="production" (
    if not exist .env.production (
        echo Error: .env.production file not found
        echo Run: python scripts/setup_environment.py
        exit /b 1
    )
    copy .env.production .env >nul
    set FLASK_ENV=production
    echo Switched to PRODUCTION environment
    echo Database: MariaDB
    echo Debug: Disabled
    echo.
    echo WARNING: Make sure MariaDB is set up and accessible!
    goto end
)

echo Error: Invalid environment "%1"
echo Valid options: development, production
exit /b 1

:end
echo.
echo Environment variables set for current session.
echo To start the application: python main.py 