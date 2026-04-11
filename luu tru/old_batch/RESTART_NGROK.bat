@echo off
echo ========================================
echo   Restart Ngrok
echo ========================================
echo.

REM Kill ngrok cũ
echo Dang dong ngrok cu...
taskkill /F /IM ngrok.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Kiểm tra frontend
echo Kiem tra Frontend...
netstat -ano | findstr :3000 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [X] Frontend KHONG chay!
    echo Dang khoi dong Frontend...
    cd frontend
    start "Frontend" cmd /k "npm run dev"
    cd ..
    echo Doi 5 giay...
    timeout /t 5 /nobreak >nul
) else (
    echo [OK] Frontend dang chay
)

echo.
echo Dang khoi dong Ngrok...
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

echo Chay: %NGROK_CMD% http 3000
echo.
echo Sau khi ngrok chay, ban se thay URL cong khai
echo Dashboard: http://127.0.0.1:4040
echo.
echo Press Ctrl+C to stop
echo.

%NGROK_CMD% http 3000

