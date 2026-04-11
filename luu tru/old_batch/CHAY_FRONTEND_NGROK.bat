@echo off
echo ========================================
echo   Trading Bot - Frontend + Ngrok
echo ========================================
echo.
echo Backend chay local, Frontend se proxy den backend
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
    echo   4. Dang ky tai khoan: https://dashboard.ngrok.com/signup
    echo   5. Chay: ngrok config add-authtoken YOUR_TOKEN
    echo.
    pause
    exit /b 1
)

REM Kiểm tra backend đang chạy chưa
echo Checking if backend is running...
curl -s http://127.0.0.1:8000/health >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Backend chua chay!
    echo Dang khoi dong backend...
    start "Backend Server" cmd /k "python run.py"
    echo Waiting for backend to start...
    timeout /t 5 /nobreak >nul
) else (
    echo Backend is running OK!
)

cd frontend

REM Kiểm tra node_modules
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
)

REM Chạy frontend trong background
echo.
echo Starting Frontend Server...
start "Frontend Server" cmd /k "npm run dev"

REM Đợi frontend khởi động
echo Waiting for frontend to start...
timeout /t 5 /nobreak >nul

REM Chạy ngrok
echo.
echo ========================================
echo   Starting Ngrok for Frontend
echo ========================================
echo.
echo Frontend se duoc expose ra internet qua ngrok
echo Backend chay local, frontend se proxy den backend
echo.
echo Dashboard: http://127.0.0.1:4040
echo.
echo Press Ctrl+C to stop ngrok
echo.

ngrok http 3000

pause

