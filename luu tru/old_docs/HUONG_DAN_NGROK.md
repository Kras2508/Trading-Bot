# Hướng Dẫn Sử Dụng Ngrok để Expose Host Ra Internet

## Mục Lục
1. [Cài Đặt Ngrok](#1-cài-đặt-ngrok)
2. [Expose Backend API](#2-expose-backend-api)
3. [Expose Frontend](#3-expose-frontend)
4. [Sử Dụng Ngrok Domain Tĩnh](#4-sử-dụng-ngrok-domain-tĩnh)
5. [Cấu Hình CORS](#5-cấu-hình-cors)
6. [Tự Động Hóa với Script](#6-tự-động-hóa-với-script)

---

## 1. Cài Đặt Ngrok

### Windows

#### Cách 1: Download Trực Tiếp
1. Truy cập: https://ngrok.com/download
2. Download file `ngrok.exe`
3. Đặt vào thư mục dự án hoặc thêm vào PATH

#### Cách 2: Dùng Chocolatey
```powershell
choco install ngrok
```

#### Cách 3: Dùng Scoop
```powershell
scoop install ngrok
```

### Linux/Mac
```bash
# Download và cài đặt
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
```

### Xác Thực (Cần Thiết)

1. Đăng ký tài khoản tại: https://dashboard.ngrok.com/signup
2. Lấy Authtoken từ: https://dashboard.ngrok.com/get-started/your-authtoken
3. Chạy lệnh:
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

---

## 2. Expose Backend API

### Chạy Backend

Đảm bảo backend đang chạy:
```bash
python run.py
```

Backend sẽ chạy tại: `http://127.0.0.1:8000`

### Chạy Ngrok cho Backend

Mở terminal mới và chạy:
```bash
ngrok http 8000
```

**Output:**
```
Forwarding   https://abc123.ngrok-free.app -> http://localhost:8000
```

**URL công khai:**
- **HTTPS**: `https://abc123.ngrok-free.app`
- **HTTP**: `http://abc123.ngrok-free.app`

### Kiểm Tra

```bash
curl https://abc123.ngrok-free.app/health
```

Hoặc mở browser: `https://abc123.ngrok-free.app/docs`

---

## 3. Expose Frontend

### Chạy Frontend

```bash
cd frontend
npm run dev
```

Frontend sẽ chạy tại: `http://localhost:3000`

### Chạy Ngrok cho Frontend

Mở terminal mới và chạy:
```bash
ngrok http 3000
```

**Output:**
```
Forwarding   https://xyz789.ngrok-free.app -> http://localhost:3000
```

**URL công khai:**
- **HTTPS**: `https://xyz789.ngrok-free.app`

### Cập Nhật Frontend Config

Cập nhật `frontend/vite.config.js` để proxy đến ngrok URL:

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': {
        target: 'https://abc123.ngrok-free.app', // Ngrok backend URL
        changeOrigin: true,
        secure: true
      }
    }
  }
})
```

Hoặc cập nhật trực tiếp trong code để dùng ngrok URL.

---

## 4. Sử Dụng Ngrok Domain Tĩnh (Paid Plan)

### Lợi Ích

- URL cố định, không thay đổi mỗi lần restart
- Dễ nhớ và chia sẻ
- Phù hợp cho production

### Cấu Hình

1. Đăng ký Ngrok Paid Plan
2. Tạo static domain từ dashboard
3. Chạy với domain tĩnh:

```bash
ngrok http 8000 --domain=your-domain.ngrok.app
```

### Ví Dụ

```bash
# Backend
ngrok http 8000 --domain=trading-api.ngrok.app

# Frontend
ngrok http 3000 --domain=trading-bot.ngrok.app
```

---

## 5. Cấu Hình CORS

### Cập Nhật .env

Thêm ngrok URL vào CORS_ORIGINS:

```env
CORS_ORIGINS=["https://xyz789.ngrok-free.app", "http://localhost:3000"]
```

Hoặc cho phép tất cả:
```env
CORS_ORIGINS=["*"]
```

### Restart Backend

Sau khi cập nhật `.env`, restart backend để áp dụng thay đổi.

---

## 6. Tự Động Hóa với Script

### Script Chạy Backend + Ngrok (Windows)

Tạo file `CHAY_BACKEND_NGROK.bat`:

```batch
@echo off
echo ========================================
echo   Trading Bot - Backend + Ngrok
echo ========================================

REM Chạy backend trong background
start "Backend Server" cmd /k "python run.py"

REM Đợi backend khởi động
timeout /t 3 /nobreak >nul

REM Chạy ngrok
echo.
echo Starting Ngrok...
echo Backend will be available at ngrok URL
echo.
ngrok http 8000

pause
```

### Script Chạy Frontend + Ngrok (Windows)

Tạo file `CHAY_FRONTEND_NGROK.bat`:

```batch
@echo off
echo ========================================
echo   Trading Bot - Frontend + Ngrok
echo ========================================

cd frontend

REM Chạy frontend trong background
start "Frontend Server" cmd /k "npm run dev"

REM Đợi frontend khởi động
timeout /t 5 /nobreak >nul

REM Chạy ngrok
echo.
echo Starting Ngrok...
echo Frontend will be available at ngrok URL
echo.
ngrok http 3000

pause
```

### Script PowerShell (Tự Động Lấy URL)

Tạo file `CHAY_NGROK_AUTO.ps1`:

```powershell
# Chạy Backend
Write-Host "Starting Backend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python run.py" -WindowStyle Minimized

Start-Sleep -Seconds 3

# Chạy Ngrok cho Backend
Write-Host "Starting Ngrok for Backend (Port 8000)..." -ForegroundColor Green
$backendNgrok = Start-Process ngrok -ArgumentList "http", "8000" -PassThru -WindowStyle Minimized

Write-Host "Backend Ngrok started. Check ngrok dashboard for URL." -ForegroundColor Yellow
Write-Host "Dashboard: http://127.0.0.1:4040" -ForegroundColor Cyan

# Chạy Frontend
Write-Host "`nStarting Frontend..." -ForegroundColor Green
Set-Location frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev" -WindowStyle Minimized

Start-Sleep -Seconds 5

# Chạy Ngrok cho Frontend
Write-Host "Starting Ngrok for Frontend (Port 3000)..." -ForegroundColor Green
$frontendNgrok = Start-Process ngrok -ArgumentList "http", "3000" -PassThru -WindowStyle Minimized

Write-Host "Frontend Ngrok started. Check ngrok dashboard for URL." -ForegroundColor Yellow
Write-Host "Dashboard: http://127.0.0.1:4040" -ForegroundColor Cyan

Write-Host "`nPress Ctrl+C to stop all services..." -ForegroundColor Red
Write-Host "Or close this window to stop." -ForegroundColor Red

# Giữ script chạy
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host "`nStopping services..." -ForegroundColor Yellow
    Stop-Process -Id $backendNgrok.Id -ErrorAction SilentlyContinue
    Stop-Process -Id $frontendNgrok.Id -ErrorAction SilentlyContinue
}
```

---

## 7. Lấy Ngrok URL Tự Động

### Sử Dụng Ngrok API

Ngrok cung cấp local API tại `http://127.0.0.1:4040/api/tunnels`

### Script Lấy URL (PowerShell)

Tạo file `LAY_NGROK_URL.ps1`:

```powershell
# Lấy Backend URL
Write-Host "Backend Ngrok URLs:" -ForegroundColor Green
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -ErrorAction Stop
    $backendTunnel = $response.tunnels | Where-Object { $_.config.addr -eq "http://localhost:8000" }
    if ($backendTunnel) {
        Write-Host "  HTTP:  $($backendTunnel.public_url)" -ForegroundColor Cyan
        Write-Host "  HTTPS: $($backendTunnel.public_url -replace 'http://', 'https://')" -ForegroundColor Cyan
    }
} catch {
    Write-Host "  Backend ngrok not running or port 8000 not exposed" -ForegroundColor Red
}

# Lấy Frontend URL
Write-Host "`nFrontend Ngrok URLs:" -ForegroundColor Green
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:4041/api/tunnels" -ErrorAction Stop
    $frontendTunnel = $response.tunnels | Where-Object { $_.config.addr -eq "http://localhost:3000" }
    if ($frontendTunnel) {
        Write-Host "  HTTP:  $($frontendTunnel.public_url)" -ForegroundColor Cyan
        Write-Host "  HTTPS: $($frontendTunnel.public_url -replace 'http://', 'https://')" -ForegroundColor Cyan
    }
} catch {
    Write-Host "  Frontend ngrok not running or port 3000 not exposed" -ForegroundColor Red
}
```

### Script Python

Tạo file `lay_ngrok_url.py`:

```python
import requests
import json

def get_ngrok_url(port=4040):
    """Lấy ngrok URL từ local API"""
    try:
        response = requests.get(f"http://127.0.0.1:{port}/api/tunnels")
        data = response.json()
        
        for tunnel in data.get('tunnels', []):
            addr = tunnel.get('config', {}).get('addr', '')
            if f':{port-4040+8000}' in addr or f':{port-4040+3000}' in addr:
                return tunnel.get('public_url')
        return None
    except:
        return None

# Backend
backend_url = get_ngrok_url(4040)
if backend_url:
    print(f"Backend URL: {backend_url}")
else:
    print("Backend ngrok not running")

# Frontend
frontend_url = get_ngrok_url(4041)
if frontend_url:
    print(f"Frontend URL: {frontend_url}")
else:
    print("Frontend ngrok not running")
```

---

## 8. Ngrok Dashboard

### Truy Cập

Khi chạy ngrok, dashboard tự động mở tại:
- **URL**: http://127.0.0.1:4040
- **Features**:
  - Xem tất cả requests
  - Replay requests
  - Inspect headers và body
  - Export requests

### Sử Dụng

1. Mở browser: `http://127.0.0.1:4040`
2. Xem tab **Requests** để xem tất cả API calls
3. Click vào request để xem chi tiết
4. Có thể replay request

---

## 9. Ví Dụ Sử Dụng

### Scenario 1: Test API Từ Điện Thoại

1. **Chạy backend + ngrok**:
   ```bash
   python run.py
   ngrok http 8000
   ```

2. **Lấy ngrok URL**: `https://abc123.ngrok-free.app`

3. **Test từ điện thoại**:
   ```bash
   curl https://abc123.ngrok-free.app/health
   ```

### Scenario 2: Chia Sẻ Frontend

1. **Chạy frontend + ngrok**:
   ```bash
   cd frontend
   npm run dev
   ngrok http 3000
   ```

2. **Chia sẻ URL**: `https://xyz789.ngrok-free.app`

3. **Người khác truy cập**: Mở browser và vào URL

### Scenario 3: Webhook từ TradingView

1. **Chạy backend + ngrok**:
   ```bash
   ngrok http 8000
   ```

2. **Lấy ngrok URL**: `https://abc123.ngrok-free.app`

3. **Cấu hình TradingView Webhook**:
   ```
   URL: https://abc123.ngrok-free.app/api/webhook/tradingview
   ```

---

## 10. Lưu Ý Quan Trọng

### ⚠️ Bảo Mật

1. **Ngrok Free Plan**:
   - URL thay đổi mỗi lần restart
   - Có giới hạn requests
   - Có warning page

2. **Ngrok Paid Plan**:
   - URL tĩnh
   - Không giới hạn
   - Không có warning page

3. **Authentication**:
   - Luôn sử dụng authentication
   - Không expose API không cần thiết
   - Sử dụng HTTPS

### ✅ Best Practices

1. **Chỉ expose khi cần**: Tắt ngrok khi không dùng
2. **Monitor requests**: Kiểm tra dashboard thường xuyên
3. **Rate limiting**: Cấu hình rate limiting cho API
4. **Logging**: Log tất cả requests

### 🔒 Security Tips

1. **IP Whitelist**: Sử dụng IP whitelist nếu có thể
2. **API Keys**: Không expose API keys trong code
3. **HTTPS Only**: Luôn dùng HTTPS
4. **Token Expiry**: Set token expiry ngắn

---

## 11. Troubleshooting

### Lỗi: "ngrok: command not found"

**Giải pháp**: Thêm ngrok vào PATH hoặc dùng đường dẫn đầy đủ

### Lỗi: "authtoken required"

**Giải pháp**: Chạy `ngrok config add-authtoken YOUR_TOKEN`

### Lỗi: "tunnel session failed"

**Giải pháp**: 
- Kiểm tra internet connection
- Kiểm tra backend đang chạy
- Thử restart ngrok

### URL Không Hoạt Động

**Kiểm tra**:
1. Backend đang chạy: `curl http://127.0.0.1:8000/health`
2. Ngrok đang chạy: Kiểm tra dashboard
3. Firewall: Cho phép ngrok

---

## 12. Scripts Tự Động

Tôi đã tạo các script tự động trong project:
- `CHAY_BACKEND_NGROK.bat`: Chạy backend + ngrok
- `CHAY_FRONTEND_NGROK.bat`: Chạy frontend + ngrok
- `CHAY_NGROK_AUTO.ps1`: Chạy tất cả tự động
- `LAY_NGROK_URL.ps1`: Lấy ngrok URLs

Sử dụng các script này để tiết kiệm thời gian!

