# Hướng Dẫn Sync Thời Gian - Fix Binance Timestamp Error

## 🔴 Lỗi

```
Failed to place order: binance {"code":-1021,"msg":"Timestamp for this request was 1000ms ahead of the server's time."}
```

## 🔍 Nguyên Nhân

Thời gian máy tính không đồng bộ với thời gian server của Binance (chênh lệch > 1000ms).

Binance yêu cầu timestamp chính xác để bảo mật API requests.

---

## ✅ Giải Pháp

### Cách 1: Dùng Script Tự Động

**Chạy script:**
```bash
SYNC_THOI_GIAN.bat
```

Script sẽ:
1. Kiểm tra Windows Time service
2. Start service nếu chưa chạy
3. Sync thời gian với NTP server

**Lưu ý**: Cần quyền Administrator

### Cách 2: Thủ Công (PowerShell Admin)

**Bước 1: Start Windows Time Service**
```powershell
net start w32time
```

**Bước 2: Sync Thời Gian**
```powershell
w32tm /resync
```

**Bước 3: Kiểm Tra Status**
```powershell
w32tm /query /status
```

### Cách 3: Cấu Hình NTP Server Cụ Thể

**PowerShell (Admin):**
```powershell
# Cấu hình NTP server
w32tm /config /manualpeerlist:"time.windows.com,time.nist.gov" /syncfromflags:manual /reliable:YES /update

# Restart service
net stop w32time
net start w32time

# Sync lại
w32tm /resync
```

---

## 🔍 Kiểm Tra Thời Gian

**Chạy script:**
```bash
KIEM_TRA_THOI_GIAN.bat
```

**Hoặc thủ công:**
```powershell
# Thời gian máy tính
Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Thời gian từ NTP
(Invoke-WebRequest -Uri "http://worldtimeapi.org/api/timezone/Asia/Ho_Chi_Minh" -UseBasicParsing).Content | ConvertFrom-Json | Select-Object -ExpandProperty datetime
```

---

## 🔧 Fix Hoàn Chỉnh

**Chạy script tự động:**
```bash
FIX_TIMESTAMP_BINANCE.bat
```

Script sẽ:
1. Sync thời gian
2. Kiểm tra lại
3. Hướng dẫn restart backend

---

## 📋 Checklist

- [ ] Windows Time service đang chạy
- [ ] Đã sync thời gian với NTP server
- [ ] Thời gian máy tính chính xác (chênh lệch < 1 giây)
- [ ] Đã restart backend sau khi sync
- [ ] Test đặt lệnh lại

---

## 🆘 Troubleshooting

### Windows Time Service Không Chạy

**Lỗi**: `The service cannot be started`

**Giải pháp**:
1. Mở **Services** (services.msc)
2. Tìm **Windows Time**
3. Right-click → **Properties**
4. Set **Startup type** = **Automatic**
5. Click **Start**

### Vẫn Bị Lỗi Sau Khi Sync

1. **Kiểm tra timezone**:
   ```powershell
   Get-TimeZone
   ```
   Đảm bảo timezone đúng (ví dụ: `(UTC+07:00) Bangkok, Hanoi, Jakarta`)

2. **Sync lại với server khác**:
   ```powershell
   w32tm /config /manualpeerlist:"pool.ntp.org" /syncfromflags:manual /reliable:YES /update
   net stop w32time
   net start w32time
   w32tm /resync
   ```

3. **Kiểm tra BIOS/UEFI time**:
   - Restart máy
   - Vào BIOS/UEFI
   - Kiểm tra thời gian trong BIOS
   - Sync nếu cần

### Lỗi "The computer did not resync because no time data was available"

**Giải pháp**:
```powershell
# Reset Windows Time service
net stop w32time
w32tm /unregister
w32tm /register
net start w32time
w32tm /config /manualpeerlist:"time.windows.com,time.nist.gov" /syncfromflags:manual /reliable:YES /update
w32tm /resync
```

---

## 💡 Lưu Ý

1. **Tự động sync**: Windows tự động sync mỗi 7 ngày, nhưng có thể cấu hình để sync thường xuyên hơn

2. **Cấu hình auto-sync thường xuyên**:
   ```powershell
   # Sync mỗi 1 giờ
   w32tm /config /update /manualpeerlist:"time.windows.com" /syncfromflags:manual /reliable:YES
   ```

3. **Kiểm tra định kỳ**:
   - Chạy `KIEM_TRA_THOI_GIAN.bat` định kỳ
   - Hoặc cấu hình Windows Task Scheduler để tự động sync

---

## ✅ Sau Khi Fix

1. **Restart backend**:
   ```bash
   RESTART_BACKEND_NAT.bat
   ```

2. **Test đặt lệnh lại**

3. **Nếu vẫn lỗi**: Kiểm tra lại thời gian và sync lại

---

## 🔗 Tham Khảo

- **Binance API Error Codes**: https://binance-docs.github.io/apidocs/spot/en/#error-codes
- **Windows Time Service**: https://docs.microsoft.com/en-us/windows-server/networking/windows-time-service/windows-time-service

