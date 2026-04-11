# Hướng dẫn Sửa Lỗi 403 Forbidden

## Vấn đề

Frontend báo lỗi **403 Forbidden** khi gọi API vì token không được gửi trong headers.

## Đã sửa

✅ Tất cả các pages đã được cập nhật để:
- Sử dụng `useAuth()` để lấy token
- Gửi token trong headers của mọi axios requests

## Cách khắc phục

### Bước 1: Refresh Frontend
- Nhấn **F5** hoặc **Ctrl+R** để refresh trang

### Bước 2: Đăng nhập lại (nếu cần)
- Nếu vẫn lỗi, **đăng xuất** và **đăng nhập lại**:
  - Username: `admin`
  - Password: `admin123`

### Bước 3: Kiểm tra
- Vào trang **"Đặt Lệnh"**
- Dropdown config sẽ load được danh sách

## Lưu ý

- Token có thời hạn **24 giờ**
- Nếu token hết hạn, frontend sẽ tự động logout
- Đảm bảo backend đang chạy (http://127.0.0.1:8000)

## Nếu vẫn lỗi

1. **Clear browser cache và localStorage**
   - Mở Developer Tools (F12)
   - Application tab > Local Storage
   - Xóa tất cả
   - Refresh và đăng nhập lại

2. **Kiểm tra backend**
   ```bash
   curl http://127.0.0.1:8000/health
   ```

3. **Kiểm tra CORS settings**
   - File `.env` có `CORS_ORIGINS=["*"]` hoặc `["http://localhost:3000"]`

