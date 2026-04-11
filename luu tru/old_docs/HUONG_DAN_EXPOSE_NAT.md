# Hướng Dẫn Expose Ra Internet Qua NAT (Port Forwarding)

## Tổng Quan

Expose frontend ra internet bằng cách cấu hình Port Forwarding trên router, không cần ngrok.

## Kiến Trúc

```
Internet → Router (Port Forwarding) → Your PC (Port 3000) → Frontend
```

---

## Bước 1: Lấy IP Công Khai (Public IP)

### Cách 1: Dùng Website

Truy cập: https://whatismyipaddress.com/

Hoặc:
```bash
curl ifconfig.me
```

**Ví dụ**: `123.45.67.89`

### Cách 2: Dùng PowerShell

```powershell
(Invoke-WebRequest -Uri "https://ifconfig.me" -UseBasicParsing).Content
```

---

## Bước 2: Lấy IP Nội Bộ (Local IP)

### Windows

```cmd
ipconfig
```

Tìm **IPv4 Address** trong phần **Ethernet adapter** hoặc **Wireless LAN adapter**:

**Ví dụ**: `192.168.1.100`

---

## Bước 3: Cấu Hình Port Forwarding trên Router

### 3.1. Đăng Nhập Router

1. Mở browser
2. Truy cập IP router (thường là):
   - `192.168.1.1`
   - `192.168.0.1`
   - `10.0.0.1`
3. Đăng nhập (xem thông tin ở mặt sau router)

### 3.2. Tìm Port Forwarding

Tên có thể là:
- **Port Forwarding**
- **Virtual Server**
- **NAT Forwarding**
- **Port Mapping**
- **Applications & Gaming**

Thường ở phần **Advanced** hoặc **Network**

### 3.3. Thêm Port Forwarding Rule

**Thông tin cần điền:**

- **Service Name**: `Trading Bot Frontend` (tên tùy ý)
- **External Port**: `3000` (hoặc port khác như 8080, 9000)
- **Internal Port**: `3000`
- **Protocol**: `TCP` (hoặc `Both`)
- **Internal IP**: IP máy tính của bạn (ví dụ: `192.168.1.100`)
- **Status**: `Enabled`

**Ví dụ:**
```
Service Name: Trading Bot Frontend
External Port: 3000
Internal Port: 3000
Protocol: TCP
Internal IP: 192.168.1.100
Status: Enabled
```

### 3.4. Lưu và Áp Dụng

Click **Save** hoặc **Apply**

---

## Bước 4: Mở Port trong Windows Firewall

### Cách 1: PowerShell (Admin)

```powershell
New-NetFirewallRule -DisplayName "Trading Bot Frontend" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
```

### Cách 2: GUI

1. Mở **Windows Defender Firewall**
2. Click **Advanced settings**
3. Click **Inbound Rules** → **New Rule**
4. Chọn **Port** → **TCP** → **Specific local ports**: `3000`
5. Chọn **Allow the connection**
6. Áp dụng cho tất cả profiles
7. Đặt tên: "Trading Bot Frontend"

---

## Bước 5: Kiểm Tra

### Kiểm Tra Port Forwarding

1. **Từ máy khác trong mạng nội bộ**:
   ```bash
   curl http://192.168.1.100:3000
   ```

2. **Từ internet** (dùng điện thoại 4G hoặc máy khác):
   ```bash
   curl http://123.45.67.89:3000
   ```

### Kiểm Tra Port Đang Listen

```cmd
netstat -an | findstr :3000
```

Phải thấy: `0.0.0.0:3000` (LISTENING)

---

## Bước 6: Truy Cập Từ Internet

Sau khi cấu hình xong:

**URL công khai**: `http://YOUR_PUBLIC_IP:3000`

**Ví dụ**: `http://123.45.67.89:3000`

---

## Lưu Ý Quan Trọng

### ⚠️ Bảo Mật

1. **HTTPS**: Cài SSL certificate (Let's Encrypt) nếu có thể
2. **Authentication**: Luôn yêu cầu đăng nhập
3. **Firewall**: Chỉ mở port cần thiết
4. **IP Whitelist**: Giới hạn IP được phép (nếu router hỗ trợ)

### 🔒 Best Practices

1. **Không expose trực tiếp** nếu không cần thiết
2. **Sử dụng VPN** thay vì expose trực tiếp
3. **Reverse Proxy**: Dùng Nginx/Caddy với SSL
4. **Rate Limiting**: Giới hạn số requests

### 📝 Dynamic IP

Nếu IP công khai thay đổi (Dynamic IP):

1. **Dynamic DNS (DDNS)**:
   - Đăng ký: No-IP, DuckDNS, Dynu
   - Cấu hình trên router
   - Dùng domain thay vì IP

2. **Ví dụ với DuckDNS**:
   - Đăng ký: https://www.duckdns.org
   - Lấy domain: `yourname.duckdns.org`
   - Cấu hình trên router
   - Truy cập: `http://yourname.duckdns.org:3000`

---

## So Sánh: NAT vs Ngrok

### NAT (Port Forwarding)

✅ **Ưu điểm**:
- Miễn phí
- Không giới hạn
- URL tĩnh (nếu có static IP hoặc DDNS)
- Không có warning page

❌ **Nhược điểm**:
- Cần quyền truy cập router
- Phức tạp hơn
- Cần cấu hình firewall
- IP có thể thay đổi (Dynamic IP)

### Ngrok

✅ **Ưu điểm**:
- Đơn giản, dễ dùng
- Không cần cấu hình router
- Tự động HTTPS
- Hoạt động ngay

❌ **Nhược điểm**:
- Free plan có warning page
- URL thay đổi mỗi lần restart
- Giới hạn 1 session (free plan)

---

## Troubleshooting

### Không Truy Cập Được Từ Internet

1. **Kiểm tra Port Forwarding**:
   - Đảm bảo rule đã được lưu
   - Kiểm tra Internal IP đúng chưa
   - Kiểm tra port đúng chưa

2. **Kiểm tra Firewall**:
   ```cmd
   netsh advfirewall firewall show rule name="Trading Bot Frontend"
   ```

3. **Kiểm tra Frontend**:
   ```cmd
   curl http://localhost:3000
   ```

4. **Kiểm tra Router**:
   - Restart router
   - Kiểm tra firmware mới nhất

### Port Bị Block

1. **ISP có thể block port**:
   - Thử port khác (8080, 9000, 8443)
   - Liên hệ ISP để mở port

2. **Router có thể block**:
   - Kiểm tra firewall trên router
   - Tắt tạm thời để test

---

## Ví Dụ Cấu Hình Router

### TP-Link

1. **Advanced** → **NAT Forwarding** → **Virtual Servers**
2. Click **Add**
3. Điền thông tin:
   - Service Port: `3000`
   - Internal Port: `3000`
   - IP Address: `192.168.1.100`
   - Protocol: `TCP`
   - Status: `Enabled`

### ASUS

1. **Advanced Settings** → **WAN** → **Virtual Server / Port Forwarding**
2. Click **Add**
3. Điền thông tin tương tự

### Linksys

1. **Connectivity** → **Administration** → **Port Range Forwarding**
2. Click **Add**
3. Điền thông tin tương tự

---

## Script Tự Động Kiểm Tra

Tạo file `KIEM_TRA_NAT.bat`:

```batch
@echo off
echo ========================================
echo   Kiem Tra NAT Configuration
echo ========================================
echo.

echo 1. Local IP:
ipconfig | findstr /i "IPv4"

echo.
echo 2. Public IP:
powershell -Command "(Invoke-WebRequest -Uri 'https://ifconfig.me' -UseBasicParsing).Content"

echo.
echo 3. Frontend Status:
netstat -ano | findstr :3000

echo.
echo 4. Firewall Rule:
netsh advfirewall firewall show rule name="Trading Bot Frontend"

echo.
pause
```

---

## Kết Luận

Sau khi cấu hình Port Forwarding:

**URL công khai**: `http://YOUR_PUBLIC_IP:3000`

**Lưu ý**: 
- Đảm bảo frontend đang chạy tại `localhost:3000`
- Đảm bảo firewall đã mở port 3000
- Đảm bảo router đã cấu hình port forwarding

