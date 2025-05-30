@echo off
echo Exporting training catalog data from SQLite database...

REM Try different Python commands that might be available
echo Trying python command...
python scripts/export_training_catalog.py
if %errorlevel% equ 0 goto success

echo Trying py command...
py scripts/export_training_catalog.py
if %errorlevel% equ 0 goto success

echo Trying python3 command...
python3 scripts/export_training_catalog.py
if %errorlevel% equ 0 goto success

echo Trying uv run python...
uv run python scripts/export_training_catalog.py
if %errorlevel% equ 0 goto success

echo.
echo Could not run Python script. Please try manually:
echo 1. Run: python scripts/export_training_catalog.py
echo 2. Or manually copy the data from training_forms.db
echo.
pause
goto end

:success
echo.
echo Export completed successfully!
echo Check scripts/training_catalog_data.sql for the SQL INSERT statements
echo Check scripts/training_catalog_export.csv for the CSV backup
echo.
pause

:end 