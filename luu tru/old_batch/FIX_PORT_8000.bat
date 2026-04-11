@echo off
echo ========================================
echo   Fix Port 8000 - Backend Access
echo ========================================
echo.

echo [1/3] Dang kill cac process backend cu...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *run.py*" >nul 2>&1
taskkill /F /IM python.exe /FI "COMMANDLINE eq *uvicorn*" >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/3] Dang mo port 8000 trong firewall...
netsh advfirewall firewall add rule name="Trading Bot Backend" dir=in action=allow protocol=TCP localport=8000 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo    [OK] Firewall rule da duoc tao
) else (
    echo    [!] Firewall rule da ton tai hoac can quyen Admin
    echo    Neu can, chay PowerShell as Admin:
    echo    New-NetFirewallRule -DisplayName "Trading Bot Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
)

echo.
echo [3/3] Kiem tra port 8000...
netstat -ano | findstr :8000
echo.

echo ========================================
echo   Huong Dan
echo ========================================
echo.
echo 1. Restart backend de listen tren 0.0.0.0:8000
echo    Chay: python run.py
echo.
echo 2. Kiem tra:
echo    netstat -ano ^| findstr :8000
echo    Phai thay: TCP    0.0.0.0:8000
echo.
echo 3. Test tu internet:
echo    http://113.22.30.49:8000
echo.
pause

