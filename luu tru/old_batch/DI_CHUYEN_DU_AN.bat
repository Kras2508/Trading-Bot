@echo off
echo ========================================
echo Move Project to Fix Python Issue
echo ========================================
echo.
echo Current location has Python configuration conflict.
echo This script will help you move the project.
echo.

set NEW_LOCATION=C:\TradingBot

echo New location: %NEW_LOCATION%
echo.
set /p confirm="Create project at %NEW_LOCATION%? (Y/N): "

if /i not "%confirm%"=="Y" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo Creating directory...
if not exist "%NEW_LOCATION%" mkdir "%NEW_LOCATION%"

echo Copying files...
xcopy /E /I /Y "%~dp0*" "%NEW_LOCATION%\"

if errorlevel 1 (
    echo ERROR: Failed to copy files!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Project moved successfully!
echo ========================================
echo.
echo New location: %NEW_LOCATION%
echo.
echo Next steps:
echo 1. cd %NEW_LOCATION%
echo 2. Run: GIAI_PHAP_DON_GIAN.bat
echo    OR: python -m pip install -r requirements.txt --user
echo    Then: python run.py
echo.
pause

