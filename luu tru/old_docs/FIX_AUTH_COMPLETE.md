# Đã Sửa Hoàn Toàn Lỗi 403 Forbidden

## Vấn đề

Frontend báo lỗi **403 Forbidden** vì:
1. Token không được gửi trong headers của axios requests
2. Một số components không sử dụng token từ `useAuth()`

## Đã sửa

✅ **Trading.jsx**: 
   - Thêm `useAuth()` để lấy token
   - Gửi token trong headers của mọi axios calls
   - Cải thiện error handling

✅ **BotConfigs.jsx**: 
   - Thêm `useAuth()` và gửi token trong headers

✅ **Orders.jsx**: 
   - Thêm `useAuth()` và gửi token trong headers

✅ **Dashboard.jsx**: 
   - Thêm `useAuth()` và gửi token trong headers

✅ **Monitoring.jsx**: 
   - Thêm `useAuth()` và gửi token trong headers

✅ **AuthContext.jsx**: 
   - Cải thiện error handling
   - Đảm bảo token được set/remove đúng cách

## Cách test

1. **Refresh frontend** (F5)
2. **Đăng xuất và đăng nhập lại**:
   - Click "Đăng xuất"
   - Đăng nhập lại với:
     - Username: `admin`
     - Password: `admin123`
3. Vào trang **"Đặt Lệnh"**
4. Dropdown config sẽ load được

## Nếu vẫn lỗi

### Clear localStorage:
1. Mở Developer Tools (F12)
2. Application tab > Local Storage > http://localhost:3000
3. Xóa tất cả keys
4. Refresh và đăng nhập lại

### Hoặc dùng Console:
```javascript
localStorage.clear()
location.reload()
```

## Lưu ý

- Token có thời hạn **24 giờ**
- Nếu token hết hạn, frontend sẽ tự động logout
- Đảm bảo backend đang chạy

