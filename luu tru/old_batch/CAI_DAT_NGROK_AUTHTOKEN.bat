@echo off
echo ========================================
echo   Cai Dat Ngrok Authtoken
echo ========================================
echo.
echo Ngrok can authtoken de chay.
echo.
echo ========================================
echo   Buoc 1: Dang Ky Tai Khoan
echo ========================================
echo.
echo 1. Mo browser va truy cap:
echo    https://dashboard.ngrok.com/signup
echo.
echo 2. Dang ky tai khoan (mien phi)
echo.
echo ========================================
echo   Buoc 2: Lay Authtoken
echo ========================================
echo.
echo 1. Dang nhap vao: https://dashboard.ngrok.com
echo.
echo 2. Vao: https://dashboard.ngrok.com/get-started/your-authtoken
echo.
echo 3. Copy authtoken (chuoi ki tu dai)
echo.
echo ========================================
echo   Buoc 3: Cai Dat Authtoken
echo ========================================
echo.
set /p AUTHTOKEN="Nhap authtoken vua copy: "

if "%AUTHTOKEN%"=="" (
    echo.
    echo ERROR: Chua nhap authtoken!
    pause
    exit /b 1
)

echo.
echo Dang cai dat authtoken...

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
        echo Vui long dat ngrok.exe vao thu muc nay hoac C:\ngrok
        pause
        exit /b 1
    )
)

REM Cài đặt authtoken
%NGROK_CMD% config add-authtoken %AUTHTOKEN%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   THANH CONG!
    echo ========================================
    echo.
    echo Authtoken da duoc cai dat.
    echo.
    echo Ban co the chay: CHAY_NGROK_NHANH.bat
    echo.
) else (
    echo.
    echo ========================================
    echo   LOI!
    echo ========================================
    echo.
    echo Khong the cai dat authtoken.
    echo Kiem tra lai authtoken va thu lai.
    echo.
)

pause

