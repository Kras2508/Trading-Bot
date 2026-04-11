# Kiểm Tra Port 8000

## Vấn Đề

Port 8000 đang listen trên `127.0.0.1:8000` thay vì `0.0.0.0:8000`

**Kết quả kiểm tra:**
```
TCP    127.0.0.1:8000         0.0.0.0:0              LISTENING
```

❌ **Sai**: Chỉ có thể truy cập từ localhost
✅ **Đúng**: Phải là `TCP    0.0.0.0:8000`

---

## Giải Pháp

### 1. Đảm Bảo Backend Listen trên 0.0.0.0

Backend đã được cấu hình đúng trong `run.py`:
```python
uvicorn.run(
    "app.main:app",
    host="0.0.0.0",  # ✅ Đúng
    port=8000,
    ...
)
```

**Nhưng backend có thể đang chạy bằng cách khác!**

### 2. Restart Backend

**Cách 1: Dùng run.py**
```bash
python run.py
```

**Cách 2: Dùng uvicorn trực tiếp**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Mở Port 8000 trong Firewall

**PowerShell (Admin):**
```powershell
New-NetFirewallRule -DisplayName "Trading Bot Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

**Hoặc CMD (Admin):**
```cmd
netsh advfirewall firewall add rule name="Trading Bot Backend" dir=in action=allow protocol=TCP localport=8000
```

### 4. Kiểm Tra Sau Khi Restart

```cmd
netstat -ano | findstr :8000
```

**Phải thấy:**
```
TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING
```

---

## Test Từ Internet

Sau khi cấu hình xong:

1. **Từ máy khác (hoặc điện thoại 4G)**:
   ```
   http://113.22.30.49:8000
   ```

2. **Test API**:
   ```
   http://113.22.30.49:8000/health
   ```

3. **Test từ localhost** (phải hoạt động):
   ```
   http://localhost:8000/health
   ```

---

## Checklist

- [ ] Backend đang chạy với `host="0.0.0.0"`
- [ ] `netstat` hiển thị `0.0.0.0:8000` (không phải `127.0.0.1:8000`)
- [ ] Firewall đã mở port 8000
- [ ] Router đã cấu hình port forwarding cho port 8000
- [ ] Test từ localhost: `http://localhost:8000/health` ✅
- [ ] Test từ internet: `http://113.22.30.49:8000/health` ✅

---

## Lưu Ý

Nếu vẫn không được:

1. **Kiểm tra router port forwarding**:
   - Đảm bảo đã cấu hình cho port 8000
   - Đảm bảo Internal IP đúng: `192.168.1.3`

2. **Kiểm tra ISP**:
   - Một số ISP block port 8000
   - Thử port khác: 8080, 9000

3. **Kiểm tra router firewall**:
   - Tắt tạm thời để test

