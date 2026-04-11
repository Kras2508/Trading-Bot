@echo off
echo ========================================
echo   Cai Dat Ngrok
echo ========================================
echo.

REM Kiểm tra ngrok đã có chưa
where ngrok >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Ngrok da duoc cai dat!
    ngrok version
    echo.
    echo Ban co the chay: CHAY_NGROK_NHANH.bat
    pause
    exit /b 0
)

echo Ngrok chua duoc cai dat.
echo.
echo ========================================
echo   Cach 1: Download Thủ Công
echo ========================================
echo.
echo 1. Truy cap: https://ngrok.com/download
echo 2. Download file ngrok.exe cho Windows
echo 3. Dat ngrok.exe vao thu muc nay:
echo    %CD%
echo 4. Chay lai: CHAY_NGROK_NHANH.bat
echo.
echo ========================================
echo   Cach 2: Dung Chocolatey (Neu co)
echo ========================================
echo.
echo choco install ngrok
echo.
echo ========================================
echo   Cach 3: Dung Scoop (Neu co)
echo ========================================
echo.
echo scoop install ngrok
echo.
echo ========================================
echo   Sau khi cai dat
echo ========================================
echo.
echo 1. Dang ky tai khoan: https://dashboard.ngrok.com/signup
echo 2. Lay Authtoken: https://dashboard.ngrok.com/get-started/your-authtoken
echo 3. Chay lenh:
echo    ngrok config add-authtoken YOUR_TOKEN
echo.
echo ========================================
echo.

REM Thử tìm ngrok.exe trong thư mục hiện tại
if exist "ngrok.exe" (
    echo Tim thay ngrok.exe trong thu muc hien tai!
    echo.
    echo Ban co the chay truc tiep:
    echo   ngrok.exe http 3000
    echo.
    echo Hoac them vao PATH de su dung tu bat ky dau.
    pause
    exit /b 0
)

echo Khong tim thay ngrok.exe trong thu muc hien tai.
echo Vui long download va dat vao day.
echo.
pause

