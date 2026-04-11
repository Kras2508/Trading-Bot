@echo off
echo ========================================
echo   Sync Thoi Gian May Tinh
echo ========================================
echo.

echo [1/4] Thoi gian hien tai:
echo.
powershell -Command "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"
echo.

echo [2/4] Dang kiem tra Windows Time service...
sc query w32time | findstr "STATE"
echo.

echo [3/4] Dang start Windows Time service...
net start w32time >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo    [OK] Windows Time service da duoc start
) else (
    echo    [!] Windows Time service da chay hoac can quyen Admin
)

echo.
echo [4/4] Dang sync thoi gian voi NTP server...
echo    CAN QUYEN ADMINISTRATOR!
echo.

powershell -Command "Start-Process powershell -ArgumentList '-Command', 'w32tm /resync; Write-Host \"Da sync thoi gian!\" -ForegroundColor Green; Write-Host \"\"; w32tm /query /status; pause' -Verb RunAs"

echo.
echo ========================================
echo   Huong Dan Thu Cong
echo ========================================
echo.
echo Neu script khong chay duoc, chay PowerShell as Administrator:
echo.
echo 1. Start Windows Time service:
echo    net start w32time
echo.
echo 2. Sync thoi gian:
echo    w32tm /resync
echo.
echo 3. Kiem tra status:
echo    w32tm /query /status
echo.
echo 4. Hoac sync voi server cu the:
echo    w32tm /config /manualpeerlist:"time.windows.com,time.nist.gov" /syncfromflags:manual /reliable:YES /update
echo    net stop w32time
echo    net start w32time
echo    w32tm /resync
echo.
pause

