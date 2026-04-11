# Hướng dẫn Đăng nhập Frontend

## Thông tin đăng nhập

### User mặc định (đã có trong database):

**Username:** `testuser`  
**Password:** `testpass123`

Hoặc:

**Username:** `admin` (nếu đã tạo)  
**Password:** (tùy theo khi tạo)

## Cách đăng nhập

1. Mở trình duyệt và truy cập: **http://localhost:3000**
2. Bạn sẽ được chuyển đến trang Login
3. Nhập:
   - **Username:** `testuser`
   - **Password:** `testpass123`
4. Click nút **"Login"**

## Tạo user mới

Nếu muốn tạo user mới, trên trang Login có nút **"Register"** hoặc **"Create Account"**:

1. Click **"Register"**
2. Điền thông tin:
   - Username
   - Email
   - Password
   - Confirm Password
3. Click **"Register"**

## API đăng nhập

Nếu muốn test qua API:

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login?username=testuser&password=testpass123"
```

Response sẽ có `access_token` để dùng cho các API calls khác.

## Lưu ý

- Backend phải đang chạy (http://127.0.0.1:8000)
- Frontend phải đang chạy (http://localhost:3000)
- Token sẽ được lưu trong localStorage của browser
- Token có thời hạn 24 giờ (theo cấu hình)

## Troubleshooting

### Lỗi: "Invalid credentials"
- Kiểm tra username/password đúng chưa
- Kiểm tra user có `is_active = True` không

### Lỗi: "Network error"
- Kiểm tra backend đã chạy chưa
- Kiểm tra CORS settings

### Lỗi: "Cannot connect to API"
- Kiểm tra backend URL trong frontend code
- Kiểm tra proxy settings trong `vite.config.js`

