@echo off
echo ========================================
echo   Expose Frontend Ra Internet
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo.

REM Tìm ngrok
set NGROK_CMD=

REM Kiểm tra trong PATH
where ngrok >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set NGROK_CMD=ngrok
    goto :found
)

REM Kiểm tra C:\ngrok\ngrok.exe
if exist "C:\ngrok\ngrok.exe" (
    set NGROK_CMD=C:\ngrok\ngrok.exe
    goto :found
)

REM Kiểm tra trong thư mục hiện tại
if exist "ngrok.exe" (
    set NGROK_CMD=ngrok.exe
    goto :found
)

REM Không tìm thấy
echo ERROR: Khong tim thay ngrok!
echo.
echo Tim kiem tai:
echo   - PATH
echo   - C:\ngrok\ngrok.exe
echo   - Thu muc hien tai
echo.
pause
exit /b 1

:found
echo Tim thay ngrok: %NGROK_CMD%
echo.

REM Kill ngrok cũ nếu có
taskkill /F /IM ngrok.exe >nul 2>&1

echo Starting Ngrok...
echo.
echo Sau khi ngrok chay, ban se thay URL cong khai
echo Dashboard: http://127.0.0.1:4040
echo.
echo Press Ctrl+C to stop
echo.

%NGROK_CMD% http 3000

