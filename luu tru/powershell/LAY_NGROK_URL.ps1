# Script để lấy Ngrok URLs tự động

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Trading Bot - Ngrok URLs" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Lấy Backend URL (port 4040)
Write-Host "Backend Ngrok URLs:" -ForegroundColor Green
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -ErrorAction Stop
    $backendTunnel = $response.tunnels | Where-Object { 
        $_.config.addr -eq "http://localhost:8000" -or $_.config.addr -eq "http://127.0.0.1:8000"
    }
    if ($backendTunnel) {
        $httpUrl = $backendTunnel.public_url
        $httpsUrl = $httpUrl -replace 'http://', 'https://'
        Write-Host "  HTTP:  $httpUrl" -ForegroundColor Yellow
        Write-Host "  HTTPS: $httpsUrl" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  API Docs: $httpsUrl/docs" -ForegroundColor Cyan
        Write-Host "  Health:   $httpsUrl/health" -ForegroundColor Cyan
    } else {
        Write-Host "  Backend ngrok not running or port 8000 not exposed" -ForegroundColor Red
    }
} catch {
    Write-Host "  Backend ngrok not running (port 4040)" -ForegroundColor Red
    Write-Host "  Start with: ngrok http 8000" -ForegroundColor Gray
}

Write-Host ""

# Lấy Frontend URL (port 4041 - nếu chạy 2 ngrok instances)
Write-Host "Frontend Ngrok URLs:" -ForegroundColor Green
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:4041/api/tunnels" -ErrorAction Stop
    $frontendTunnel = $response.tunnels | Where-Object { 
        $_.config.addr -eq "http://localhost:3000" -or $_.config.addr -eq "http://127.0.0.1:3000"
    }
    if ($frontendTunnel) {
        $httpUrl = $frontendTunnel.public_url
        $httpsUrl = $httpUrl -replace 'http://', 'https://'
        Write-Host "  HTTP:  $httpUrl" -ForegroundColor Yellow
        Write-Host "  HTTPS: $httpsUrl" -ForegroundColor Yellow
    } else {
        Write-Host "  Frontend ngrok not running or port 3000 not exposed" -ForegroundColor Red
    }
} catch {
    # Thử port 4040 (nếu chỉ chạy 1 ngrok instance)
    try {
        $response = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -ErrorAction Stop
        $frontendTunnel = $response.tunnels | Where-Object { 
            $_.config.addr -eq "http://localhost:3000" -or $_.config.addr -eq "http://127.0.0.1:3000"
        }
        if ($frontendTunnel) {
            $httpUrl = $frontendTunnel.public_url
            $httpsUrl = $httpUrl -replace 'http://', 'https://'
            Write-Host "  HTTP:  $httpUrl" -ForegroundColor Yellow
            Write-Host "  HTTPS: $httpsUrl" -ForegroundColor Yellow
        } else {
            Write-Host "  Frontend ngrok not running (port 3000)" -ForegroundColor Red
            Write-Host "  Start with: ngrok http 3000" -ForegroundColor Gray
        }
    } catch {
        Write-Host "  Frontend ngrok not running" -ForegroundColor Red
        Write-Host "  Start with: ngrok http 3000" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Ngrok Dashboard: http://127.0.0.1:4040" -ForegroundColor Cyan
Write-Host ""

