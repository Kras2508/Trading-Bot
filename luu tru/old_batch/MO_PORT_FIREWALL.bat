@echo off
echo ========================================
echo   Mo Port 3000 trong Firewall
echo ========================================
echo.

echo Dang tao firewall rule cho port 3000...

powershell -Command "Start-Process powershell -ArgumentList '-Command', 'New-NetFirewallRule -DisplayName \"Trading Bot Frontend\" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow; Write-Host \"Firewall rule da duoc tao!\" -ForegroundColor Green; pause' -Verb RunAs"

echo.
echo Neu khong chay duoc, chay PowerShell as Administrator va chay:
echo New-NetFirewallRule -DisplayName "Trading Bot Frontend" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
echo.
pause

