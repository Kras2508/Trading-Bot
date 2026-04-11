# Cấu Hình NAT - Thông Tin Của Bạn

## 📋 Thông Tin IP

- **Local IP (Nội bộ)**: `192.168.1.3`
- **Public IP (Công khai)**: `113.22.30.49`

---

## 🔧 Cấu Hình Port Forwarding trên Router

### Bước 1: Đăng Nhập Router

1. Mở browser
2. Truy cập: `192.168.1.1` (hoặc IP router của bạn)
3. Đăng nhập (xem thông tin ở mặt sau router)

### Bước 2: Tìm Port Forwarding

Tìm trong menu:
- **Port Forwarding**
- **Virtual Server**
- **NAT Forwarding**
- **Port Mapping**

### Bước 3: Thêm Rule

**Thông tin cần điền:**

```
Service Name: Trading Bot Frontend
External Port: 3000
Internal Port: 3000
Internal IP: 192.168.1.3
Protocol: TCP
Status: Enabled
```

### Bước 4: Save và Apply

Click **Save** hoặc **Apply**

---

## 🔥 Mở Port trong Firewall

Chạy PowerShell **as Administrator**:

```powershell
New-NetFirewallRule -DisplayName "Trading Bot Frontend" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
```

Hoặc chạy script:
```bash
MO_PORT_FIREWALL.bat
```
*(Cần chạy as Administrator)*

---

## ✅ Kiểm Tra

### 1. Kiểm Tra Frontend

```bash
curl http://localhost:3000
```

### 2. Kiểm Tra từ Mạng Nội Bộ

```bash
curl http://192.168.1.3:3000
```

### 3. Kiểm Tra từ Internet

Sau khi cấu hình port forwarding, từ máy khác (hoặc điện thoại 4G):

```bash
curl http://113.22.30.49:3000
```

---

## 🌐 URL Công Khai

Sau khi cấu hình xong:

**HTTP**: `http://113.22.30.49:3000`

**Lưu ý**: 
- IP này có thể thay đổi nếu là Dynamic IP
- Để giữ IP cố định, cần Static IP hoặc Dynamic DNS (DDNS)

---

## 📝 Checklist

- [ ] Frontend đang chạy tại `localhost:3000`
- [ ] Backend đang chạy tại `127.0.0.1:8000`
- [ ] Firewall đã mở port 3000
- [ ] Router đã cấu hình port forwarding
- [ ] Test từ mạng nội bộ: `http://192.168.1.3:3000`
- [ ] Test từ internet: `http://113.22.30.49:3000`

---

## 🔒 Bảo Mật

1. **HTTPS**: Cài SSL certificate nếu có thể
2. **Authentication**: Luôn yêu cầu đăng nhập
3. **IP Whitelist**: Giới hạn IP được phép (nếu router hỗ trợ)
4. **Firewall**: Chỉ mở port cần thiết

---

## 💡 Dynamic DNS (Nếu IP Thay Đổi)

Nếu IP công khai thay đổi, dùng Dynamic DNS:

1. **Đăng ký DDNS**: 
   - No-IP: https://www.noip.com
   - DuckDNS: https://www.duckdns.org
   - Dynu: https://www.dynu.com

2. **Cấu hình trên router**:
   - Nhập thông tin DDNS
   - Router tự động cập nhật IP

3. **Truy cập bằng domain**:
   - `http://yourname.duckdns.org:3000`

---

## 🆘 Troubleshooting

### Không truy cập được từ internet

1. **Kiểm tra port forwarding**: Đảm bảo đã save và apply
2. **Kiểm tra firewall**: Đảm bảo port 3000 đã mở
3. **Kiểm tra frontend**: Đảm bảo đang chạy
4. **Kiểm tra router firewall**: Tắt tạm thời để test
5. **Kiểm tra ISP**: Một số ISP block port, thử port khác (8080, 9000)

### Port bị block

- Thử port khác: 8080, 9000, 8443
- Liên hệ ISP để mở port
- Dùng port 80/443 nếu có thể (cần quyền admin)

---

## ✅ Sau Khi Hoàn Thành

**URL công khai**: `http://113.22.30.49:3000`

Bạn có thể truy cập từ bất kỳ đâu trên internet!

