@echo off
echo ========================================
echo   Mo Port 8000 trong Firewall
echo ========================================
echo.

echo Dang tao firewall rule cho port 8000...
echo CAN QUYEN ADMINISTRATOR!
echo.

powershell -Command "Start-Process powershell -ArgumentList '-Command', 'New-NetFirewallRule -DisplayName \"Trading Bot Backend\" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow; Write-Host \"Firewall rule da duoc tao!\" -ForegroundColor Green; pause' -Verb RunAs"

echo.
echo Neu khong chay duoc, chay PowerShell as Administrator va chay:
echo New-NetFirewallRule -DisplayName "Trading Bot Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
echo.
pause

