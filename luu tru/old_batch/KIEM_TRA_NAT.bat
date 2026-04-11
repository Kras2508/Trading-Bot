@echo off
echo ========================================
echo   Kiem Tra NAT Configuration
echo ========================================
echo.

echo [1/4] Local IP (IP noi bo):
ipconfig | findstr /i "IPv4"

echo.
echo [2/4] Public IP (IP cong khai):
powershell -Command "try { $ip = (Invoke-WebRequest -Uri 'https://ifconfig.me' -UseBasicParsing).Content; Write-Host $ip -ForegroundColor Green } catch { Write-Host 'Khong the lay Public IP' -ForegroundColor Red }"

echo.
echo [3/4] Frontend Status (Port 3000):
netstat -ano | findstr :3000 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo    [OK] Frontend dang chay tai port 3000
    netstat -ano | findstr :3000
) else (
    echo    [X] Frontend KHONG chay!
    echo    Chay: RESTART_FRONTEND_FORCE.bat
)

echo.
echo [4/4] Firewall Rule:
netsh advfirewall firewall show rule name="Trading Bot Frontend" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo    [OK] Firewall rule da duoc tao
    netsh advfirewall firewall show rule name="Trading Bot Frontend"
) else (
    echo    [X] Firewall rule CHUA duoc tao
    echo    Chay: MO_PORT_FIREWALL.bat
)

echo.
echo ========================================
echo   Huong Dan
echo ========================================
echo.
echo 1. Cap nhat Port Forwarding tren router:
echo    - External Port: 3000
echo    - Internal Port: 3000
echo    - Internal IP: [Local IP o tren]
echo.
echo 2. URL cong khai se la:
echo    http://[Public IP o tren]:3000
echo.
pause

