@echo off
REM SGII Project Cleanup Script for Windows
REM This batch file runs the Python cleanup script with various options

echo SGII Project Cleanup Utility
echo ============================
echo.

:menu
echo Select cleanup option:
echo 1. Dry run (show what would be cleaned without deleting)
echo 2. Clean Python cache files only
echo 3. Clean all including database
echo 4. Clean all including static and media files
echo 5. Exit
echo.

set /p choice=Enter your choice (1-5): 

if "%choice%"=="1" goto dryrun
if "%choice%"=="2" goto basic
if "%choice%"=="3" goto withdb
if "%choice%"=="4" goto full
if "%choice%"=="5" goto end

echo Invalid choice. Please try again.
echo.
goto menu

:dryrun
echo.
echo Running dry run...
python "%~dp0cleanup_project.py" --dry-run
goto pause

:basic
echo.
echo Cleaning Python cache files...
python "%~dp0cleanup_project.py"
goto pause

:withdb
echo.
echo Cleaning all including database...
echo WARNING: This will delete the SQLite database!
set /p confirm=Are you sure? (y/n): 
if /i "%confirm%"=="y" (
    python "%~dp0cleanup_project.py" --include-db
) else (
    echo Cancelled.
)
goto pause

:full
echo.
echo Cleaning all including static and media files...
echo WARNING: This will delete database, static files, and media files!
set /p confirm=Are you sure? (y/n): 
if /i "%confirm%"=="y" (
    python "%~dp0cleanup_project.py" --include-db --include-static --include-media
) else (
    echo Cancelled.
)
goto pause

:pause
echo.
pause
echo.
goto menu

:end
echo.
echo Cleanup utility closed.
pause
