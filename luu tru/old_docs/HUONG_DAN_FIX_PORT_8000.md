# Hướng Dẫn Fix Port 8000

## 🔴 Vấn Đề

Port 8000 đang listen trên `127.0.0.1:8000` thay vì `0.0.0.0:8000`

**Kết quả kiểm tra:**
```
TCP    127.0.0.1:8000         0.0.0.0:0              LISTENING
```

❌ **Sai**: Chỉ có thể truy cập từ localhost  
✅ **Đúng**: Phải là `TCP    0.0.0.0:8000`

---

## ✅ Giải Pháp

### Bước 1: Mở Port 8000 trong Firewall

**Chạy script (cần quyền Admin):**
```bash
MO_PORT_8000_FIREWALL.bat
```

**Hoặc PowerShell (Admin):**
```powershell
New-NetFirewallRule -DisplayName "Trading Bot Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### Bước 2: Restart Backend

**Chạy script:**
```bash
RESTART_BACKEND_NAT.bat
```

**Hoặc thủ công:**
1. Kill backend cũ (Ctrl+C trong cửa sổ backend)
2. Chạy lại:
   ```bash
   python run.py
   ```

### Bước 3: Kiểm Tra

```cmd
netstat -ano | findstr :8000
```

**Phải thấy:**
```
TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING
```

**Không được thấy:**
```
TCP    127.0.0.1:8000         0.0.0.0:0              LISTENING
```

---

## 🌐 Test Từ Internet

Sau khi fix xong:

1. **Test từ localhost** (phải hoạt động):
   ```
   http://localhost:8000/health
   ```

2. **Test từ internet** (từ máy khác hoặc điện thoại 4G):
   ```
   http://113.22.30.49:8000/health
   ```

3. **Test API**:
   ```
   http://113.22.30.49:8000/api/auth/me
   ```

---

## 📋 Checklist

- [ ] Firewall đã mở port 8000
- [ ] Backend đã restart
- [ ] `netstat` hiển thị `0.0.0.0:8000`
- [ ] Router đã cấu hình port forwarding cho port 8000
- [ ] Test từ localhost: ✅
- [ ] Test từ internet: ✅

---

## 🔍 Troubleshooting

### Vẫn thấy `127.0.0.1:8000`

1. **Kiểm tra backend đang chạy như thế nào**:
   - Đảm bảo chạy bằng `python run.py`
   - Hoặc `uvicorn app.main:app --host 0.0.0.0 --port 8000`

2. **Kiểm tra file `run.py`**:
   - Phải có `host="0.0.0.0"`

3. **Kill tất cả process Python và restart**:
   ```cmd
   taskkill /F /IM python.exe
   python run.py
   ```

### Không truy cập được từ internet

1. **Kiểm tra router port forwarding**:
   - Đảm bảo đã cấu hình cho port 8000
   - Internal IP: `192.168.1.3`

2. **Kiểm tra firewall**:
   ```cmd
   netsh advfirewall firewall show rule name="Trading Bot Backend"
   ```

3. **Kiểm tra ISP**:
   - Một số ISP block port 8000
   - Thử port khác: 8080, 9000

---

## 📝 Lưu Ý

- **Frontend (port 3000)**: Đã OK, đang listen trên `0.0.0.0:3000`
- **Backend (port 8000)**: Cần fix để listen trên `0.0.0.0:8000`

Sau khi fix, cả 2 port sẽ có thể truy cập từ internet qua NAT!

