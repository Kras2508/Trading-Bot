@echo off
echo ========================================
echo   Trading Bot Backend - Port 80
echo ========================================
echo.
echo WARNING: Port 80 requires Administrator privileges!
echo.
echo Press Ctrl+C to stop the server
echo.

REM Chuyển đến thư mục chứa script
cd /d "%~dp0"

REM Kiểm tra quyền Administrator
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: This script requires Administrator privileges!
    echo.
    echo Please:
    echo   1. Right-click this file
    echo   2. Select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo Starting backend on port 80...
echo Backend will be available at:
echo   - http://localhost
echo   - http://0.0.0.0
echo   - http://YOUR_IP_ADDRESS
echo.
echo API Docs: http://localhost/docs
echo Health: http://localhost/health
echo.

python run_port80.py

pause

