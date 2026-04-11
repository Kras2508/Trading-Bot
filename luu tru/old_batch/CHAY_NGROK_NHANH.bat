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

REM Kiểm tra trong thư mục hiện tại
if exist "ngrok.exe" (
    set NGROK_CMD=ngrok.exe
    goto :found
)

REM Kiểm tra trong C:\ngrok
if exist "C:\ngrok\ngrok.exe" (
    set NGROK_CMD=C:\ngrok\ngrok.exe
    goto :found
)

REM Kiểm tra trong C:\ngrok
if exist "C:\ngrok\ngrok.exe" (
    set NGROK_CMD=C:\ngrok\ngrok.exe
    goto :found
)

REM Kiểm tra trong Program Files
if exist "C:\Program Files\ngrok\ngrok.exe" (
    set NGROK_CMD="C:\Program Files\ngrok\ngrok.exe"
    goto :found
)

REM Không tìm thấy
echo ERROR: Ngrok chua duoc cai dat!
echo.
echo ========================================
echo   Huong Dan Cai Dat
echo ========================================
echo.
echo 1. Download: https://ngrok.com/download
echo 2. Dat ngrok.exe vao thu muc nay:
echo    %CD%
echo 3. Hoac chay: CAI_DAT_NGROK.bat
echo.
echo Sau khi cai dat, chay lai script nay.
echo.
pause
exit /b 1

:found

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

