# Đã Sửa Lỗi 403 Forbidden

## Vấn đề

Frontend báo lỗi **403 Forbidden** khi gọi API `/api/config/` vì:
- Token không được gửi trong headers của axios requests
- Một số components không sử dụng `useAuth()` để lấy token

## Đã sửa

✅ **Trading.jsx**: Thêm `useAuth()` và gửi token trong headers
✅ **BotConfigs.jsx**: Thêm `useAuth()` và gửi token trong headers  
✅ **Orders.jsx**: Thêm `useAuth()` và gửi token trong headers
✅ **Dashboard.jsx**: Thêm `useAuth()` và gửi token trong headers
✅ **Monitoring.jsx**: Thêm `useAuth()` và gửi token trong headers
✅ **AuthContext.jsx**: Cải thiện error handling

## Cách test

1. **Refresh frontend** (F5 hoặc Ctrl+R)
2. **Đăng nhập lại** nếu cần:
   - Username: `admin`
   - Password: `admin123`
3. Vào trang **"Đặt Lệnh"**
4. Dropdown config sẽ load được

## Lưu ý

- Nếu vẫn lỗi, **đăng xuất và đăng nhập lại** để lấy token mới
- Token có thời hạn 24 giờ
- Nếu token hết hạn, frontend sẽ tự động logout

