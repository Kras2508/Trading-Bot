# Hướng dẫn Chạy Frontend

## Frontend Location

Frontend nằm trong thư mục: `frontend/`

## Cách Chạy Frontend

### Bước 1: Cài đặt Dependencies (Lần đầu)

```bash
cd frontend
npm install
```

### Bước 2: Chạy Frontend

```bash
npm run dev
```

Hoặc sử dụng script có sẵn:
```bash
CHAY_FRONTEND.bat
```

## Frontend URL

Sau khi chạy, frontend sẽ có tại:

**http://localhost:3000**

## Cấu hình

- **Port**: 3000 (theo `vite.config.js`)
- **Backend API**: http://127.0.0.1:8000
- **Proxy**: Frontend tự động proxy `/api` requests đến backend

## Các Trang

1. **Login**: http://localhost:3000/login
2. **Dashboard**: http://localhost:3000/dashboard
3. **Bot Configs**: http://localhost:3000/configs
4. **Orders**: http://localhost:3000/orders
5. **Monitoring**: http://localhost:3000/monitoring

## Lưu ý

- Backend phải chạy trước (port 8000)
- Frontend sẽ tự động kết nối với backend qua proxy
- Nếu backend không chạy, frontend sẽ báo lỗi khi gọi API

## Troubleshooting

### Lỗi: "Cannot find module"
- Chạy `npm install` trong thư mục `frontend/`

### Lỗi: "Port 3000 already in use"
- Đổi port trong `vite.config.js` hoặc tắt ứng dụng đang dùng port 3000

### Frontend không kết nối được backend
- Kiểm tra backend đã chạy chưa: http://127.0.0.1:8000/health
- Kiểm tra CORS settings trong backend

