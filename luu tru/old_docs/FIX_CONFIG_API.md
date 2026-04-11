# Hướng dẫn Sửa Lỗi "Không thể tải danh sách configs"

## Nguyên nhân

Lỗi 500 Internal Server Error khi gọi API `/api/config/` có thể do:
1. Database connection issue với SQL Server
2. Schema serialization issue
3. Missing field trong response

## Đã sửa

1. ✅ Thêm error handling trong `app/routers/config.py`
2. ✅ Cải thiện error message trong frontend

## Cách kiểm tra

### 1. Kiểm tra Backend đang chạy
```bash
curl http://127.0.0.1:8000/health
```

### 2. Test API Config
```bash
python test_api_config.py
```

### 3. Kiểm tra Logs
Xem file `logs/app.log` để xem lỗi chi tiết

## Giải pháp

### Nếu vẫn lỗi:

1. **Restart Backend Server**
   ```bash
   python run.py
   ```

2. **Kiểm tra Database Connection**
   ```bash
   python kiem_tra_database.py
   ```

3. **Kiểm tra SQL Server đang chạy**
   - Mở SQL Server Management Studio
   - Kiểm tra database `BackendAPI_Trading` có accessible không

4. **Clear Browser Cache**
   - Xóa localStorage trong browser
   - Đăng nhập lại

5. **Kiểm tra CORS**
   - Đảm bảo CORS_ORIGINS trong `.env` có `["*"]` hoặc `["http://localhost:3000"]`

## Test lại

Sau khi sửa, test lại:
1. Mở frontend: http://localhost:3000
2. Đăng nhập
3. Vào trang "Đặt Lệnh"
4. Kiểm tra dropdown config có load được không

