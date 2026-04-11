# Hướng dẫn Sửa Lỗi Đăng Nhập

## Vấn đề

1. **"Cannot destructure property 'token' of 'useAuth(...)' as it is undefined"**
   - `useAuth()` hook trả về undefined

2. **"GET /api/auth/me 401 (Unauthorized)"**
   - Token không hợp lệ hoặc đã hết hạn

## Đã sửa

✅ **AuthContext.jsx**:
   - Thêm error handling cho `useAuth()` hook
   - Sửa `fetchUser` để nhận token làm parameter
   - Cải thiện error handling khi token invalid

✅ **App.jsx**:
   - Sửa `ProtectedRoute` để handle undefined token

## Cách khắc phục

### Bước 1: Clear localStorage
1. Mở Developer Tools (F12)
2. Application tab > Local Storage > http://localhost:3000
3. Click chuột phải > Clear
4. Hoặc xóa từng key một

### Bước 2: Refresh Frontend
- Nhấn **F5** hoặc **Ctrl+R**

### Bước 3: Đăng nhập lại
- Username: `admin`
- Password: `admin123`

## Hoặc dùng Console

Mở Console (F12) và chạy:
```javascript
localStorage.clear()
location.reload()
```

Sau đó đăng nhập lại.

## Kiểm tra

1. Console không còn lỗi
2. Đăng nhập thành công
3. Chuyển đến Dashboard
4. Có thể vào trang "Đặt Lệnh"

## Lưu ý

- Backend API login hoạt động tốt (đã test)
- Vấn đề là ở frontend React context
- Đảm bảo backend đang chạy

