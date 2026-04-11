@echo off
echo ========================================
echo   Sync Thoi Gian - Fix Binance Error
echo ========================================
echo.

echo Thoi gian hien tai:
powershell -Command "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"
echo.

echo Dang sync thoi gian voi NTP server...
echo CAN QUYEN ADMINISTRATOR!
echo.

powershell -Command "Start-Process powershell -ArgumentList '-Command', 'Write-Host \"Dang sync thoi gian...\" -ForegroundColor Yellow; net start w32time 2>$null; w32tm /resync; if ($?) { Write-Host \"[OK] Da sync thoi gian!\" -ForegroundColor Green } else { Write-Host \"[!] Can quyen Admin hoac service da chay\" -ForegroundColor Red }; Write-Host \"\"; Write-Host \"Thoi gian sau khi sync:\"; Get-Date -Format \"yyyy-MM-dd HH:mm:ss\"; Write-Host \"\"; Write-Host \"Status:\"; w32tm /query /status | Select-String -Pattern \"Source|Last Successful Sync\"; pause' -Verb RunAs"

echo.
echo ========================================
echo   Sau Khi Sync
echo ========================================
echo.
echo 1. Restart backend:
echo    RESTART_BACKEND_NAT.bat
echo.
echo 2. Test dat lenh lai
echo.
pause

