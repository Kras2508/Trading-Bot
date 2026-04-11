@echo off
echo ========================================
echo Restart Trading Bot Backend Server
echo ========================================
echo.

echo Stopping any running server...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Starting server...
echo Server will be available at: http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python run.py

pause

