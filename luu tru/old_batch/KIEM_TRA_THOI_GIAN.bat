@echo off
echo ========================================
echo   Kiem Tra Thoi Gian May Tinh
echo ========================================
echo.

echo [1/3] Thoi gian may tinh:
powershell -Command "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"
echo.

echo [2/3] Windows Time service status:
sc query w32time | findstr "STATE"
echo.

echo [3/3] Thoi gian tu NTP server (time.windows.com):
powershell -Command "try { $ntp = (Invoke-WebRequest -Uri 'http://worldtimeapi.org/api/timezone/Asia/Ho_Chi_Minh' -UseBasicParsing).Content | ConvertFrom-Json; Write-Host $ntp.datetime -ForegroundColor Green } catch { Write-Host 'Khong the lay thoi gian tu NTP' -ForegroundColor Red }"

echo.
echo ========================================
echo   Ghi Chu
echo ========================================
echo.
echo Neu thoi gian khac nhau hon 1 giay, can sync:
echo    SYNC_THOI_GIAN.bat
echo.
pause

