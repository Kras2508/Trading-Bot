# Hướng Dẫn Expose Qua NAT - Tóm Tắt

## Các Bước

### 1. Lấy IP

**Local IP** (IP nội bộ):
```cmd
ipconfig
```
Tìm IPv4 Address → Ví dụ: `192.168.1.100`

**Public IP** (IP công khai):
```cmd
curl ifconfig.me
```
Hoặc: https://whatismyipaddress.com/

### 2. Cấu Hình Router

1. Đăng nhập router: `192.168.1.1` (hoặc IP router của bạn)
2. Vào **Port Forwarding** / **Virtual Server**
3. Thêm rule:
   - External Port: `3000`
   - Internal Port: `3000`
   - Internal IP: `192.168.1.100` (IP máy bạn)
   - Protocol: `TCP`
4. Save

### 3. Mở Firewall

Chạy:
```bash
MO_PORT_FIREWALL.bat
```

Hoặc PowerShell (Admin):
```powershell
New-NetFirewallRule -DisplayName "Trading Bot Frontend" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
```

### 4. Kiểm Tra

Chạy:
```bash
KIEM_TRA_NAT.bat
```

### 5. Truy Cập

**URL công khai**: `http://YOUR_PUBLIC_IP:3000`

---

## Lưu Ý

- ✅ Đảm bảo frontend đang chạy tại `localhost:3000`
- ✅ Đảm bảo router đã cấu hình port forwarding
- ✅ Đảm bảo firewall đã mở port 3000
- ⚠️ IP công khai có thể thay đổi (Dynamic IP)
- 🔒 Nên dùng HTTPS và authentication

---

## So Sánh với Ngrok

| Tính năng | NAT | Ngrok |
|-----------|-----|-------|
| Miễn phí | ✅ | ✅ (có giới hạn) |
| URL tĩnh | ✅ (với static IP/DDNS) | ❌ (free plan) |
| Warning page | ✅ Không có | ❌ Có (free plan) |
| Độ khó | ⚠️ Phức tạp | ✅ Đơn giản |
| Cần router access | ✅ Có | ❌ Không |

