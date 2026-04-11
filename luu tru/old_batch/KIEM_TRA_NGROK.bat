@echo off
echo ========================================
echo   Kiem Tra Ngrok Status
echo ========================================
echo.

echo 1. Kiem tra Frontend (port 3000)...
netstat -ano | findstr :3000 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo    [OK] Frontend dang chay tai port 3000
) else (
    echo    [X] Frontend KHONG chay!
    echo    Chay: cd frontend ^&^& npm run dev
)

echo.
echo 2. Kiem tra Ngrok...
tasklist | findstr ngrok.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo    [OK] Ngrok dang chay
) else (
    echo    [X] Ngrok KHONG chay!
    echo    Chay: CHAY_NGROK_NHANH.bat
)

echo.
echo 3. Lay Ngrok URL...
echo.
powershell -Command "try { $response = Invoke-RestMethod -Uri 'http://127.0.0.1:4040/api/tunnels' -ErrorAction Stop; $tunnel = $response.tunnels | Where-Object { $_.config.addr -match ':3000' }; if ($tunnel) { Write-Host 'URL CONG KHAI:' -ForegroundColor Green; Write-Host $tunnel.public_url -ForegroundColor Yellow; Write-Host ''; Write-Host 'Mo browser va truy cap URL tren!' -ForegroundColor Cyan } else { Write-Host 'Chua co tunnel cho port 3000' -ForegroundColor Red; Write-Host 'Chay: RESTART_NGROK.bat' -ForegroundColor Yellow } } catch { Write-Host 'Ngrok chua san sang hoac chua chay' -ForegroundColor Red; Write-Host 'Chay: RESTART_NGROK.bat' -ForegroundColor Yellow }"

echo.
echo 4. Ngrok Dashboard: http://127.0.0.1:4040
echo.
pause

