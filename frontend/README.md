# Trading Bot Frontend (React)

Giao diện quản lý Trading Bot được xây dựng bằng React.

## Cài đặt

```bash
cd frontend
npm install
```

## Chạy Development Server

```bash
npm run dev
```

Frontend sẽ chạy tại: http://localhost:3000

## Build Production

```bash
npm run build
```

## Tính năng

- ✅ Đăng nhập/Đăng ký
- ✅ Dashboard với thống kê
- ✅ Quản lý Bot Configurations (CRUD)
- ✅ Xem lịch sử Orders
- ✅ Monitoring bot status
- ✅ Pause/Resume bots

## Cấu trúc

```
frontend/
├── src/
│   ├── components/     # Components tái sử dụng
│   ├── pages/          # Các trang chính
│   ├── context/        # React Context (Auth)
│   ├── App.jsx         # Main App component
│   └── main.jsx        # Entry point
├── package.json
└── vite.config.js      # Vite configuration
```

## API Backend

Frontend kết nối với backend tại: http://127.0.0.1:8000

Proxy được cấu hình trong `vite.config.js` để tự động forward `/api/*` requests đến backend.

