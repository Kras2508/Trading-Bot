# Hướng Dẫn Truy Cập Từ Bên Ngoài

## Mục Lục
1. [Lấy IP Address](#1-lấy-ip-address)
2. [Cấu Hình Backend](#2-cấu-hình-backend)
3. [Cấu Hình Frontend](#3-cấu-hình-frontend)
4. [Truy Cập Từ Thiết Bị Khác](#4-truy-cập-từ-thiết-bị-khác)
5. [Truy Cập Từ Internet](#5-truy-cập-từ-internet)

---

## 1. Lấy IP Address

### Windows

#### Cách 1: Dùng Command Prompt
```cmd
ipconfig
```

Tìm dòng **IPv4 Address** trong phần **Ethernet adapter** hoặc **Wireless LAN adapter**:
```
IPv4 Address. . . . . . . . . . . : 192.168.1.100
```

#### Cách 2: Dùng PowerShell
```powershell
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"} | Select-Object IPAddress
```

### Linux/Mac
```bash
ifconfig
# hoặc
ip addr show
```

---

## 2. Cấu Hình Backend

### Đã Cấu Hình Sẵn

Backend đã được cấu hình để chạy trên `0.0.0.0` (tất cả interfaces), cho phép truy cập từ bên ngoài.

### Chạy Backend

```bash
python run.py
```

Hoặc:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Kiểm Tra

Backend sẽ chạy và có thể truy cập từ:
- **Local**: `http://127.0.0.1:8000` hoặc `http://localhost:8000`
- **Mạng nội bộ**: `http://YOUR_IP:8000` (ví dụ: `http://192.168.1.100:8000`)

### CORS Configuration

Đảm bảo file `.env` có:
```env
CORS_ORIGINS=["*"]
```

Hoặc chỉ định IP cụ thể:
```env
CORS_ORIGINS=["http://192.168.1.100:3000", "http://localhost:3000"]
```

---

## 3. Cấu Hình Frontend

### Cập Nhật Vite Config

File `frontend/vite.config.js` đã được cấu hình để:
- Chạy trên `0.0.0.0` (tất cả interfaces)
- Proxy API requests đến backend

### Chạy Frontend

```bash
cd frontend
npm run dev
```

Frontend sẽ chạy và có thể truy cập từ:
- **Local**: `http://localhost:3000`
- **Mạng nội bộ**: `http://YOUR_IP:3000` (ví dụ: `http://192.168.1.100:3000`)

### Cập Nhật API URL (Nếu Cần)

Nếu frontend và backend chạy trên các máy khác nhau, cập nhật `frontend/vite.config.js`:

```javascript
server: {
  host: '0.0.0.0',
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://YOUR_BACKEND_IP:8000',  // Thay YOUR_BACKEND_IP
      changeOrigin: true,
    }
  }
}
```

---

## 4. Truy Cập Từ Thiết Bị Khác

### Trong Cùng Mạng WiFi/LAN

1. **Lấy IP của máy chạy server**:
   ```cmd
   ipconfig
   ```
   Ví dụ: `192.168.1.100`

2. **Truy cập từ thiết bị khác**:
   - **Backend API**: `http://192.168.1.100:8000`
   - **Frontend**: `http://192.168.1.100:3000`
   - **API Docs**: `http://192.168.1.100:8000/docs`

3. **Kiểm tra Firewall**:
   - Windows Firewall có thể chặn kết nối
   - Cho phép port 8000 và 3000 trong Windows Firewall

### Mở Port Trong Windows Firewall

#### Cách 1: Dùng PowerShell (Admin)
```powershell
New-NetFirewallRule -DisplayName "Backend API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Frontend" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
```

#### Cách 2: Dùng GUI
1. Mở **Windows Defender Firewall**
2. Click **Advanced settings**
3. Click **Inbound Rules** > **New Rule**
4. Chọn **Port** > **TCP** > **Specific local ports**: `8000, 3000`
5. Chọn **Allow the connection**
6. Áp dụng cho tất cả profiles
7. Đặt tên: "Trading Bot API"

---

## 5. Truy Cập Từ Internet

### Yêu Cầu

- Router có chức năng Port Forwarding
- IP tĩnh hoặc Dynamic DNS (DDNS)
- Đảm bảo bảo mật (HTTPS, Authentication)

### Cấu Hình Port Forwarding

1. **Đăng nhập Router**:
   - Thường là: `192.168.1.1` hoặc `192.168.0.1`
   - Xem thông tin đăng nhập ở mặt sau router

2. **Tìm Port Forwarding**:
   - Tên có thể là: "Port Forwarding", "Virtual Server", "NAT"
   - Thường ở phần **Advanced** hoặc **Network**

3. **Thêm Rules**:
   - **Backend (Port 8000)**:
     - External Port: `8000`
     - Internal Port: `8000`
     - Protocol: `TCP`
     - Internal IP: IP của máy chạy server (ví dụ: `192.168.1.100`)
   
   - **Frontend (Port 3000)**:
     - External Port: `3000`
     - Internal Port: `3000`
     - Protocol: `TCP`
     - Internal IP: IP của máy chạy server

4. **Lưu và Áp dụng**

### Lấy Public IP

```bash
curl ifconfig.me
# hoặc
curl ipinfo.io/ip
```

### Truy Cập

Sau khi cấu hình port forwarding:
- **Backend**: `http://YOUR_PUBLIC_IP:8000`
- **Frontend**: `http://YOUR_PUBLIC_IP:3000`

### ⚠️ Cảnh Báo Bảo Mật

1. **Sử dụng HTTPS**: Cài đặt SSL certificate (Let's Encrypt)
2. **Authentication**: Luôn yêu cầu đăng nhập
3. **Firewall**: Chỉ mở port cần thiết
4. **VPN**: Sử dụng VPN thay vì expose trực tiếp
5. **Rate Limiting**: Giới hạn số request

---

## Ví Dụ Thực Tế

### Scenario 1: Truy Cập Từ Điện Thoại (Cùng WiFi)

1. **Máy tính chạy server**: IP = `192.168.1.100`
2. **Điện thoại**: Kết nối cùng WiFi
3. **Truy cập**: `http://192.168.1.100:3000`

### Scenario 2: Truy Cập Từ Máy Tính Khác (Cùng LAN)

1. **Server**: `192.168.1.100`
2. **Client**: `192.168.1.101`
3. **Truy cập**: `http://192.168.1.100:3000`

### Scenario 3: Truy Cập Từ Internet

1. **Public IP**: `123.45.67.89`
2. **Port Forwarding**: Đã cấu hình
3. **Truy cập**: `http://123.45.67.89:3000`

---

## Kiểm Tra Kết Nối

### Test Backend

```bash
# Từ máy khác
curl http://YOUR_IP:8000/health
```

### Test Frontend

Mở browser và truy cập: `http://YOUR_IP:3000`

### Test API

```bash
curl http://YOUR_IP:8000/api/auth/login?username=admin&password=admin123
```

---

## Troubleshooting

### Không Truy Cập Được

1. **Kiểm tra Firewall**:
   ```cmd
   netsh advfirewall firewall show rule name=all | findstr 8000
   ```

2. **Kiểm tra Port Đang Listen**:
   ```cmd
   netstat -an | findstr 8000
   ```

3. **Kiểm tra IP**:
   ```cmd
   ipconfig
   ```

4. **Ping Test**:
   ```cmd
   ping YOUR_IP
   ```

### Lỗi CORS

Cập nhật `.env`:
```env
CORS_ORIGINS=["*"]
```

Hoặc chỉ định IP cụ thể:
```env
CORS_ORIGINS=["http://192.168.1.100:3000", "http://localhost:3000"]
```

---

## Lưu Ý

- ⚠️ **Bảo mật**: Không expose trực tiếp ra internet nếu không cần thiết
- ✅ **Nên dùng**: VPN hoặc reverse proxy (Nginx, Caddy)
- 🔒 **HTTPS**: Luôn sử dụng HTTPS cho production
- 🛡️ **Firewall**: Chỉ mở port cần thiết

