# Hướng Dẫn Expose Frontend Ra Internet với Ngrok

## Tổng Quan

Chỉ expose **Frontend** ra internet qua Ngrok. **Backend** chạy local và frontend sẽ tự động proxy đến backend.

## Kiến Trúc

```
Internet → Ngrok → Frontend (Port 3000) → Backend (Port 8000 - Local)
```

- **Frontend**: Expose qua Ngrok, có thể truy cập từ internet
- **Backend**: Chạy local (127.0.0.1:8000), không expose ra ngoài
- **Proxy**: Frontend tự động proxy API requests đến backend local

---

## Bước 1: Cài Đặt Ngrok

### Windows

1. Download: https://ngrok.com/download
2. Giải nén `ngrok.exe` vào thư mục project
3. Hoặc thêm vào PATH

### Xác Thực

1. Đăng ký: https://dashboard.ngrok.com/signup
2. Lấy Authtoken: https://dashboard.ngrok.com/get-started/your-authtoken
3. Chạy:
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

---

## Bước 2: Chạy Backend (Local)

Backend phải chạy trước để frontend có thể proxy đến:

```bash
python run.py
```

Backend sẽ chạy tại: `http://127.0.0.1:8000`

**Kiểm tra:**
```bash
curl http://127.0.0.1:8000/health
```

---

## Bước 3: Chạy Frontend + Ngrok

### Cách 1: Dùng Script Tự Động (Khuyến Nghị)

Chạy file:
```bash
CHAY_FRONTEND_NGROK.bat
```

Script sẽ:
1. ✅ Kiểm tra backend đang chạy (nếu chưa thì tự động start)
2. ✅ Chạy frontend
3. ✅ Chạy ngrok để expose frontend

### Cách 2: Chạy Thủ Công

#### 3.1. Chạy Frontend

Mở terminal 1:
```bash
cd frontend
npm run dev
```

Frontend chạy tại: `http://localhost:3000`

#### 3.2. Chạy Ngrok

Mở terminal 2:
```bash
ngrok http 3000
```

**Output:**
```
Forwarding   https://abc123.ngrok-free.app -> http://localhost:3000
```

---

## Bước 4: Truy Cập

### URL Công Khai

Sau khi chạy ngrok, bạn sẽ có URL công khai:
- **HTTPS**: `https://abc123.ngrok-free.app`
- **HTTP**: `http://abc123.ngrok-free.app`

### Truy Cập Từ Bất Kỳ Đâu

1. Mở browser
2. Truy cập: `https://abc123.ngrok-free.app`
3. Đăng nhập và sử dụng như bình thường

### Kiểm Tra

```bash
curl https://abc123.ngrok-free.app
```

---

## Cấu Hình Frontend

Frontend đã được cấu hình sẵn trong `frontend/vite.config.js`:

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',  // Cho phép truy cập từ bên ngoài
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',  // Backend local
        changeOrigin: true
      }
    }
  }
})
```

**Giải thích:**
- Frontend proxy tất cả requests `/api/*` đến backend local
- Backend không cần expose ra ngoài
- Chỉ cần expose frontend qua ngrok

---

## Lấy Ngrok URL

### Cách 1: Xem Trong Terminal

Khi chạy `ngrok http 3000`, URL sẽ hiển thị ngay:
```
Forwarding   https://abc123.ngrok-free.app -> http://localhost:3000
```

### Cách 2: Ngrok Dashboard

Mở browser: `http://127.0.0.1:4040`

Dashboard hiển thị:
- URL công khai
- Tất cả requests
- Có thể replay requests

### Cách 3: Dùng Script

Chạy:
```powershell
.\LAY_NGROK_URL.ps1
```

Script sẽ tự động lấy URL từ ngrok API.

---

## Ví Dụ Sử Dụng

### Scenario 1: Chia Sẻ với Người Khác

1. **Chạy backend**:
   ```bash
   python run.py
   ```

2. **Chạy frontend + ngrok**:
   ```bash
   CHAY_FRONTEND_NGROK.bat
   ```

3. **Lấy URL**: `https://abc123.ngrok-free.app`

4. **Chia sẻ URL** cho người khác

5. **Người khác truy cập**: Mở browser và vào URL

### Scenario 2: Test Từ Điện Thoại

1. Chạy `CHAY_FRONTEND_NGROK.bat`
2. Lấy ngrok URL
3. Mở browser trên điện thoại
4. Truy cập ngrok URL
5. Test đặt lệnh từ điện thoại

### Scenario 3: Demo Cho Khách Hàng

1. Chạy backend + frontend + ngrok
2. Chia sẻ ngrok URL
3. Khách hàng truy cập và test
4. Tắt ngrok khi xong

---

## Lưu Ý Quan Trọng

### ⚠️ Bảo Mật

1. **Ngrok Free Plan**:
   - URL thay đổi mỗi lần restart
   - Có warning page
   - Giới hạn requests

2. **Ngrok Paid Plan**:
   - URL tĩnh (không đổi)
   - Không có warning page
   - Không giới hạn

3. **Authentication**:
   - Luôn yêu cầu đăng nhập
   - Không chia sẻ URL công khai nếu không cần

### ✅ Ưu Điểm

- **Đơn giản**: Chỉ cần expose frontend
- **Bảo mật**: Backend không expose ra ngoài
- **Dễ dàng**: Một lệnh là xong
- **Nhanh**: Không cần cấu hình router

### 🔒 Best Practices

1. **Chỉ expose khi cần**: Tắt ngrok khi không dùng
2. **Monitor requests**: Kiểm tra dashboard thường xuyên
3. **Strong passwords**: Đảm bảo user có password mạnh
4. **HTTPS**: Luôn dùng HTTPS (ngrok tự động)

---

## Troubleshooting

### Lỗi: "ngrok: command not found"

**Giải pháp**: 
- Thêm ngrok vào PATH
- Hoặc dùng đường dẫn đầy đủ: `.\ngrok.exe http 3000`

### Lỗi: "authtoken required"

**Giải pháp**: 
```bash
ngrok config add-authtoken YOUR_TOKEN
```

### Frontend không kết nối được backend

**Kiểm tra**:
1. Backend đang chạy: `curl http://127.0.0.1:8000/health`
2. Frontend proxy config đúng trong `vite.config.js`
3. Không có firewall block

### URL không hoạt động

**Kiểm tra**:
1. Ngrok đang chạy: Mở `http://127.0.0.1:4040`
2. Frontend đang chạy: `curl http://localhost:3000`
3. Internet connection

---

## Scripts Có Sẵn

### `CHAY_FRONTEND_NGROK.bat`
- Tự động kiểm tra và chạy backend
- Chạy frontend
- Chạy ngrok
- Tất cả trong một lệnh

### `LAY_NGROK_URL.ps1`
- Lấy ngrok URL tự động
- Hiển thị HTTP và HTTPS URLs
- Link đến API docs

---

## So Sánh

### Expose Cả Backend + Frontend

❌ **Nhược điểm**:
- Phải chạy 2 ngrok instances
- Phải cấu hình CORS phức tạp
- Backend expose ra ngoài (không an toàn)
- Phức tạp hơn

### Chỉ Expose Frontend (Khuyến Nghị)

✅ **Ưu điểm**:
- Chỉ cần 1 ngrok instance
- Backend an toàn (chạy local)
- Đơn giản, dễ quản lý
- Frontend tự động proxy đến backend

---

## Kết Luận

Với cách này, bạn chỉ cần:
1. Chạy backend local
2. Chạy `CHAY_FRONTEND_NGROK.bat`
3. Lấy ngrok URL
4. Chia sẻ và sử dụng!

**Đơn giản, nhanh chóng, an toàn!** 🚀

