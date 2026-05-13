@echo off
cd /d "%~dp0"

echo ========================================
echo   Fix Timestamp Error - Binance
echo ========================================
echo.

echo Loi: "Timestamp for this request was 1000ms ahead"
echo.
echo Nguyen nhan: Thoi gian may tinh khong dong bo voi Binance server
echo.
echo ========================================
echo   Giai Phap
echo ========================================
echo.

echo Script nay CAN quyen Administrator.
echo.

net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
	echo [ERROR] Vui long click chuot phai file nay va chon "Run as administrator"
	echo.
	pause
	exit /b 1
)

echo [1/4] Thoi gian hien tai:
powershell -Command "Get-Date -Format 'yyyy-MM-dd HH:mm:ss.fff'"
echo.

echo [2/4] Khoi dong Windows Time service...
sc config w32time start= auto >nul 2>&1
net start w32time >nul 2>&1
if %ERRORLEVEL% EQU 0 (
	echo [OK] Windows Time service da san sang
) else (
	echo [INFO] Windows Time service da chay
)
echo.

echo [3/4] Sync thoi gian voi NTP server...
w32tm /resync /force
if %ERRORLEVEL% NEQ 0 (
	echo [ERROR] Khong the sync tu dong.
	echo Thu chay lan luot cac lenh sau trong CMD (Admin):
	echo   w32tm /config /manualpeerlist:"time.windows.com,time.nist.gov" /syncfromflags:manual /update
	echo   net stop w32time
	echo   net start w32time
	echo   w32tm /resync /force
	echo.
	pause
	exit /b 1
)

echo.
echo [4/4] Kiem tra trang thai dong bo:
w32tm /query /status

echo.
echo ========================================
echo   Sau Khi Sync
echo ========================================
echo.
echo 1. Restart backend:
echo    CHAY_SERVER.bat
echo.
echo 2. Test dat lenh lai
echo.
pause

