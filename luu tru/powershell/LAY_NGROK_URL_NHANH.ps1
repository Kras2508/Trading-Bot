# Script lấy Ngrok URL nhanh
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Lay Ngrok URL" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Start-Sleep -Seconds 2

try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -ErrorAction Stop
    $tunnel = $response.tunnels | Where-Object { 
        $_.config.addr -like "*:3000" -or $_.config.addr -eq "http://localhost:3000"
    } | Select-Object -First 1
    
    if ($tunnel) {
        Write-Host "Ngrok URL Cong Khai:" -ForegroundColor Green
        Write-Host ""
        Write-Host "  HTTPS: " -NoNewline -ForegroundColor Yellow
        Write-Host $tunnel.public_url -ForegroundColor White
        Write-Host ""
        Write-Host "Dashboard: http://127.0.0.1:4040" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Truy cap: " -NoNewline -ForegroundColor Green
        Write-Host $tunnel.public_url -ForegroundColor White
    } else {
        Write-Host "Khong tim thay tunnel cho port 3000" -ForegroundColor Red
        Write-Host "Kiem tra: http://127.0.0.1:4040" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Ngrok chua chay hoac chua san sang" -ForegroundColor Red
    Write-Host ""
    Write-Host "Chay ngrok bang lenh:" -ForegroundColor Yellow
    Write-Host "  C:\ngrok\ngrok.exe http 3000" -ForegroundColor White
    Write-Host ""
    Write-Host "Hoac chay: CHAY_NGROK.bat" -ForegroundColor Yellow
}

