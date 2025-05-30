@echo off
REM Database Management Script for Training Form Application
REM Usage: db_manager.cmd [command] [options]

if "%1"=="" (
    echo Training Form Database Manager
    echo.
    echo Usage: db_manager.cmd [command] [options]
    echo.
    echo Commands:
    echo   migrate                    - Run all pending migrations
    echo   status                     - Show migration status
    echo   create [migration_name]    - Create a new migration template
    echo   force-version [number]     - Force set the current version
    echo   setup                      - Set up initial database
    echo   backup                     - Create database backup
    echo   help                       - Show this help message
    echo.
    echo Examples:
    echo   db_manager.cmd migrate
    echo   db_manager.cmd create add_new_column
    echo   db_manager.cmd status
    echo   db_manager.cmd force-version 3
    exit /b 1
)

if "%1"=="migrate" (
    echo Running database migrations...
    python scripts/migrate_database.py
    goto end
)

if "%1"=="status" (
    echo Checking migration status...
    python scripts/migrate_database.py --status
    goto end
)

if "%1"=="create" (
    if "%2"=="" (
        echo Error: Migration name required
        echo Usage: db_manager.cmd create [migration_name]
        exit /b 1
    )
    echo Creating migration template: %2
    python scripts/migrate_database.py --create %2
    goto end
)

if "%1"=="force-version" (
    if "%2"=="" (
        echo Error: Version number required
        echo Usage: db_manager.cmd force-version [number]
        exit /b 1
    )
    echo Setting database version to %2
    python scripts/migrate_database.py --force-version %2
    goto end
)

if "%1"=="setup" (
    echo Setting up initial database...
    python setup_db.py
    goto end
)

if "%1"=="backup" (
    echo Creating database backup...
    set timestamp=%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
    set timestamp=%timestamp: =0%
    
    if exist training_forms.db (
        copy training_forms.db "training_forms_backup_%timestamp%.db"
        echo SQLite backup created: training_forms_backup_%timestamp%.db
    )
    
    if exist uploads (
        mkdir "uploads_backup_%timestamp%" 2>nul
        xcopy uploads "uploads_backup_%timestamp%\" /e /i /y >nul
        echo Uploads backup created: uploads_backup_%timestamp%
    )
    goto end
)

if "%1"=="help" (
    %0
    goto end
)

echo Unknown command: %1
echo Run 'db_manager.cmd help' for usage information
exit /b 1

:end
echo.
echo Database management completed. 