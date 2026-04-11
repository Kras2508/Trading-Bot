@echo off
echo ========================================
echo   Restart Frontend (Force)
echo ========================================
echo.

REM Kill tất cả node processes
echo Dang dong tat ca frontend processes...
taskkill /F /IM node.exe >nul 2>&1
timeout /t 3 /nobreak >nul

cd frontend

echo Dang khoi dong Frontend voi config moi...
echo.
echo Frontend se chay tai: http://localhost:3000
echo Config da duoc cap nhat de cho phep ngrok hosts
echo.
echo Press Ctrl+C to stop
echo.

npm run dev

