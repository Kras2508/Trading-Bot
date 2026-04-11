@echo off
echo ========================================
echo   Expose Frontend Ra Internet (Safe)
echo ========================================
echo.

REM Đóng tất cả ngrok cũ trước
echo 1. Dong ngrok cu (neu co)...
taskkill /F /IM ngrok.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Kiểm tra frontend
echo 2. Kiem tra Frontend...
netstat -ano | findstr :3000 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo    [X] Frontend KHONG chay tai port 3000
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
        echo ERROR: Ngrok chua duoc cai dat!
        echo Download: https://ngrok.com/download
        pause
        exit /b 1
    )
)

echo 3. Khoi dong Ngrok...
echo.
echo ========================================
echo   LUU Y: Free Plan chi cho phep 1 session
echo ========================================
echo.
echo Sau khi ngrok chay, ban se thay URL cong khai
echo Dashboard: http://127.0.0.1:4040
echo.
echo Press Ctrl+C to stop
echo.

%NGROK_CMD% http 3000

