@echo off
echo ========================================
echo Restart Server and Test API
echo ========================================
echo.

echo Step 1: Stopping any running Python processes...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Step 2: Starting backend server...
start "Backend Server" cmd /k "python run.py"

echo Waiting for server to start...
timeout /t 5 /nobreak >nul

echo.
echo Step 3: Testing API...
python test_api.py

echo.
echo ========================================
echo Done!
echo ========================================
echo.
echo Server is running in a separate window.
echo You can close this window or press any key to exit.
pause

