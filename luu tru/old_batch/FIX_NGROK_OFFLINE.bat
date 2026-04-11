@echo off
echo ========================================
echo   Fix Ngrok Offline Error
echo ========================================
echo.

REM Kiểm tra frontend
echo 1. Kiem tra Frontend...
netstat -ano | findstr :3000 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo    [X] Frontend KHONG chay tai port 3000
    echo.
    echo    Dang khoi dong Frontend...
    cd frontend
    start "Frontend Server" cmd /k "npm run dev"
    cd ..
    echo    Doi 5 giay de frontend khoi dong...
    timeout /t 5 /nobreak >nul
) else (
    echo    [OK] Frontend dang chay
)

echo.

REM Kiểm tra ngrok
echo 2. Kiem tra Ngrok...
tasklist | findstr ngrok.exe >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo    [X] Ngrok KHONG chay
    echo.
    echo    Dang khoi dong Ngrok...
    call CHAY_NGROK_NHANH.bat
) else (
    echo    [OK] Ngrok dang chay
    echo.
    echo    Co the ngrok tunnel bi ngat.
    echo    Dang restart ngrok...
    taskkill /F /IM ngrok.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
    call CHAY_NGROK_NHANH.bat
)

echo.
echo ========================================
echo   Hoan Thanh!
echo ========================================
echo.
echo Kiem tra lai URL ngrok trong terminal ngrok
echo hoac mo: http://127.0.0.1:4040
echo.

