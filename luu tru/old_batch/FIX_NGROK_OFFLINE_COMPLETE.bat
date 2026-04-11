@echo off
echo ========================================
echo   Fix Ngrok Offline - Complete
echo ========================================
echo.

REM Bước 1: Đóng ngrok cũ
echo [1/4] Dong ngrok cu...
taskkill /F /IM ngrok.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo    [OK] Da dong ngrok cu

REM Bước 2: Kiểm tra Frontend
echo [2/4] Kiem tra Frontend...
netstat -ano | findstr :3000 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo    [X] Frontend KHONG chay
    echo    Dang khoi dong Frontend...
    cd frontend
    start "Frontend" cmd /k "npm run dev"
    cd ..
    echo    Doi 5 giay de frontend khoi dong...
    timeout /t 5 /nobreak >nul
    echo    [OK] Frontend da khoi dong
) else (
    echo    [OK] Frontend dang chay
    echo    Restart frontend de ap dung config moi...
    taskkill /F /IM node.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
    cd frontend
    start "Frontend" cmd /k "npm run dev"
    cd ..
    echo    Doi 5 giay...
    timeout /t 5 /nobreak >nul
)

REM Bước 3: Kiểm tra Backend
echo [3/4] Kiem tra Backend...
curl -s http://127.0.0.1:8000/health >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo    [X] Backend KHONG chay
    echo    Dang khoi dong Backend...
    start "Backend" cmd /k "python run.py"
    timeout /t 3 /nobreak >nul
) else (
    echo    [OK] Backend dang chay
)

REM Bước 4: Chạy ngrok mới
echo [4/4] Khoi dong Ngrok...
echo.

REM Tìm ngrok
set NGROK_CMD=

if exist "C:\ngrok\ngrok.exe" (
    set NGROK_CMD=C:\ngrok\ngrok.exe
) else if exist "ngrok.exe" (
    set NGROK_CMD=ngrok.exe
) else (
    where ngrok >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set NGROK_CMD=ngrok
    ) else (
        echo ERROR: Khong tim thay ngrok!
        pause
        exit /b 1
    )
)

echo ========================================
echo   Ngrok se chay trong terminal moi
echo ========================================
echo.
echo Sau khi ngrok chay, ban se thay URL cong khai
echo Dashboard: http://127.0.0.1:4040
echo.
echo Press Ctrl+C to stop ngrok
echo.

start "Ngrok" cmd /k "%NGROK_CMD% http 3000"

echo.
echo Ngrok da duoc khoi dong trong terminal moi.
echo Kiem tra terminal ngrok de lay URL.
echo.
pause

