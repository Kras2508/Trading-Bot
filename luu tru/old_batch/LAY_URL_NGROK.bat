@echo off
echo ========================================
echo   Lay Ngrok URL
echo ========================================
echo.

powershell -Command "$response = Invoke-RestMethod -Uri 'http://127.0.0.1:4040/api/tunnels' -ErrorAction SilentlyContinue; if ($response) { $tunnel = $response.tunnels | Where-Object { $_.config.addr -match ':3000' }; if ($tunnel) { Write-Host 'URL CONG KHAI:' -ForegroundColor Green; Write-Host $tunnel.public_url -ForegroundColor Yellow; Write-Host ''; Write-Host 'Dashboard: http://127.0.0.1:4040' -ForegroundColor Cyan } else { Write-Host 'Chua co tunnel cho port 3000' -ForegroundColor Red } } else { Write-Host 'Ngrok chua chay!' -ForegroundColor Red; Write-Host 'Chay: CHAY_NGROK_NHANH.bat' -ForegroundColor Yellow }"

echo.
pause

