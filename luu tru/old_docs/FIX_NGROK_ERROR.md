# Khắc Phục Lỗi Ngrok ERR_NGROK_3200

## Nguyên Nhân

Lỗi `ERR_NGROK_3200 - The endpoint is offline` xảy ra khi:
1. ❌ Frontend không còn chạy tại `localhost:3000`
2. ❌ Ngrok tunnel bị ngắt kết nối
3. ❌ Ngrok process bị tắt
4. ❌ Port 3000 bị block hoặc đang được sử dụng bởi process khác

---

## Cách Khắc Phục

### Bước 1: Kiểm Tra Frontend Đang Chạy

Mở terminal và kiểm tra:

```bash
# Windows
netstat -an | findstr 3000

# Hoặc kiểm tra trong browser
# Mở: http://localhost:3000
```

**Nếu frontend không chạy:**

```bash
cd frontend
npm run dev
```

Đảm bảo frontend chạy thành công và hiển thị:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: http://0.0.0.0:3000/
```

### Bước 2: Kiểm Tra Ngrok Đang Chạy

Mở terminal khác và kiểm tra:

```bash
# Windows
tasklist | findstr ngrok

# Hoặc mở ngrok dashboard
# http://127.0.0.1:4040
```

**Nếu ngrok không chạy:**

1. Đóng tất cả ngrok processes cũ:
   ```bash
   taskkill /F /IM ngrok.exe
   ```

2. Chạy lại ngrok:
   ```bash
   ngrok http 3000
   ```

### Bước 3: Kiểm Tra Port 3000

```bash
# Windows - Kiểm tra port đang được sử dụng
netstat -ano | findstr :3000
```

Nếu port bị chiếm bởi process khác:
```bash
# Tìm PID
netstat -ano | findstr :3000

# Kill process (thay PID bằng số thực tế)
taskkill /F /PID <PID>
```

### Bước 4: Chạy Lại Tất Cả

#### Cách 1: Chạy Thủ Công

**Terminal 1 - Backend:**
```bash
python run.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Ngrok:**
```bash
ngrok http 3000
```

#### Cách 2: Dùng Script

Chạy file:
```bash
CHAY_FRONTEND_NGROK.bat
```

Script sẽ tự động:
1. ✅ Kiểm tra và chạy backend
2. ✅ Chạy frontend
3. ✅ Chạy ngrok

---

## Kiểm Tra Kết Nối

### 1. Kiểm Tra Frontend Local

Mở browser: `http://localhost:3000`

Nếu không mở được → Frontend chưa chạy

### 2. Kiểm Tra Ngrok Dashboard

Mở browser: `http://127.0.0.1:4040`

- Nếu không mở được → Ngrok chưa chạy
- Nếu mở được nhưng không có tunnel → Ngrok chưa kết nối

### 3. Kiểm Tra Ngrok URL

Từ ngrok dashboard hoặc terminal, lấy URL mới:
```
Forwarding   https://xyz789.ngrok-free.app -> http://localhost:3000
```

**Lưu ý:** URL có thể thay đổi mỗi lần restart ngrok!

---

## Troubleshooting Chi Tiết

### Lỗi: "ngrok: command not found"

**Giải pháp:**
```bash
# Kiểm tra ngrok đã cài chưa
where ngrok

# Nếu chưa có, download từ:
# https://ngrok.com/download

# Hoặc dùng đường dẫn đầy đủ
.\ngrok.exe http 3000
```

### Lỗi: "authtoken required"

**Giải pháp:**
```bash
# Lấy token từ: https://dashboard.ngrok.com/get-started/your-authtoken
ngrok config add-authtoken YOUR_TOKEN
```

### Frontend chạy nhưng ngrok không kết nối

**Kiểm tra:**
1. Frontend có chạy trên port 3000 không?
   ```bash
   curl http://localhost:3000
   ```

2. Firewall có block không?
   - Tạm thời tắt Windows Firewall để test

3. Có process khác đang dùng port 3000 không?
   ```bash
   netstat -ano | findstr :3000
   ```

### Ngrok kết nối nhưng URL không hoạt động

**Kiểm tra:**
1. Frontend có đang chạy không?
2. URL có đúng không? (copy lại từ terminal)
3. Có dùng HTTPS không? (ngrok free plan yêu cầu HTTPS)

---

## Quy Trình Đúng

### 1. Start Backend
```bash
python run.py
```
✅ Đợi đến khi thấy: `Uvicorn running on http://0.0.0.0:8000`

### 2. Start Frontend
```bash
cd frontend
npm run dev
```
✅ Đợi đến khi thấy: `Local: http://localhost:3000/`

### 3. Start Ngrok
```bash
ngrok http 3000
```
✅ Đợi đến khi thấy: `Forwarding https://xxx.ngrok-free.app -> http://localhost:3000`

### 4. Test
- Mở browser: `http://localhost:3000` → Phải hoạt động
- Mở browser: `https://xxx.ngrok-free.app` → Phải hoạt động

---

## Script Tự Động

Sử dụng script `CHAY_FRONTEND_NGROK.bat` để tự động chạy tất cả:

```bash
CHAY_FRONTEND_NGROK.bat
```

Script sẽ:
1. ✅ Kiểm tra backend
2. ✅ Tự động start backend nếu chưa chạy
3. ✅ Start frontend
4. ✅ Start ngrok
5. ✅ Hiển thị URL

---

## Lưu Ý Quan Trọng

1. **Thứ tự chạy**: Backend → Frontend → Ngrok
2. **URL thay đổi**: Mỗi lần restart ngrok, URL sẽ thay đổi (free plan)
3. **Giữ terminal mở**: Không đóng terminal chạy ngrok
4. **Kiểm tra thường xuyên**: Đảm bảo cả 3 services đang chạy

---

## Quick Fix

Nếu gặp lỗi, chạy lệnh này để reset tất cả:

```bash
# 1. Kill tất cả processes
taskkill /F /IM ngrok.exe
taskkill /F /IM node.exe
taskkill /F /IM python.exe

# 2. Chạy lại từ đầu
python run.py
# (Terminal mới)
cd frontend && npm run dev
# (Terminal mới)
ngrok http 3000
```

Hoặc đơn giản hơn, dùng script:
```bash
CHAY_FRONTEND_NGROK.bat
```

