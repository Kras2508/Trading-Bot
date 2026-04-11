@echo off
echo ========================================
echo   Trading Bot - Backend + Ngrok
echo ========================================
echo.

REM Kiểm tra ngrok đã cài chưa
where ngrok >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Ngrok chua duoc cai dat!
    echo.
    echo Cai dat ngrok:
    echo   1. Download: https://ngrok.com/download
    echo   2. Dat ngrok.exe vao thu muc nay
    echo   3. Hoac them vao PATH
    echo.
    pause
    exit /b 1
)

REM Chạy backend trong background
echo Starting Backend Server...
start "Backend Server" cmd /k "python run.py"

REM Đợi backend khởi động
echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

REM Chạy ngrok
echo.
echo ========================================
echo   Starting Ngrok for Backend
echo ========================================
echo.
echo Backend will be available at ngrok URL
echo Dashboard: http://127.0.0.1:4040
echo.
echo Press Ctrl+C to stop ngrok
echo.

ngrok http 8000

pause

