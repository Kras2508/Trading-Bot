@echo off
echo ========================================
echo   Dong Tat Ca Ngrok Processes
echo ========================================
echo.

echo Dang dong tat ca ngrok...
taskkill /F /IM ngrok.exe >nul 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [OK] Da dong tat ca ngrok processes
) else (
    echo [INFO] Khong co ngrok nao dang chay
)

echo.
echo Doi 2 giay...
timeout /t 2 /nobreak >nul

echo.
echo Ban co the chay: CHAY_NGROK_NHANH.bat
echo.

pause

