@echo off
echo ========================================
echo   Restart Frontend
echo ========================================
echo.

REM Kill frontend cũ
echo Dang dong frontend cu...
taskkill /F /IM node.exe >nul 2>&1
timeout /t 2 /nobreak >nul

cd frontend

echo Dang khoi dong Frontend...
echo.
echo Frontend se chay tai: http://localhost:3000
echo.
echo Press Ctrl+C to stop
echo.

npm run dev

