# Hướng dẫn Sử dụng Trading Bot Backend

## Bước 1: Tạo User Admin đầu tiên

### Cách 1: Dùng script
```bash
python TAO_USER_ADMIN.py
```

### Cách 2: Dùng Swagger UI
1. Mở trình duyệt: http://127.0.0.1:8000/docs
2. Tìm endpoint `POST /api/auth/register`
3. Click "Try it out"
4. Điền thông tin:
```json
{
  "username": "admin",
  "email": "admin@example.com",
  "password": "your-secure-password",
  "is_admin": true
}
```
5. Click "Execute"

### Cách 3: Dùng curl
```bash
curl -X POST "http://127.0.0.1:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "your-password",
    "is_admin": true
  }'
```

## Bước 2: Đăng nhập để lấy Token

### Cách 1: Dùng Swagger UI
1. Tìm endpoint `POST /api/auth/login`
2. Click "Try it out"
3. Điền:
   - `username`: admin
   - `password`: your-password
4. Click "Execute"
5. Copy `access_token` từ response

### Cách 2: Dùng curl
```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login?username=admin&password=your-password"
```

Response sẽ có dạng:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Bước 3: Tạo Bot Config đầu tiên

### Dùng Swagger UI:
1. Click nút "Authorize" ở đầu trang
2. Nhập: `Bearer YOUR_ACCESS_TOKEN`
3. Tìm endpoint `POST /api/config/`
4. Click "Try it out"
5. Điền thông tin config:

```json
{
  "name": "BTC Spot Bot",
  "symbol": "BTC/USDT",
  "exchange": "binance",
  "amount": 100.0,
  "leverage": 1,
  "stop_loss_percent": 2.0,
  "take_profit_percent": 5.0,
  "trading_mode": "spot",
  "enable_notifications": false
}
```

6. Click "Execute"

## Bước 4: Test Webhook (TradingView)

### Cách 1: Dùng Swagger UI
1. Tìm endpoint `POST /api/webhook/tradingview`
2. Click "Try it out"
3. Điền payload:
```json
{
  "symbol": "BTC/USDT",
  "action": "buy",
  "config": "BTC Spot Bot"
}
```
4. Click "Execute"

**Lưu ý:** Webhook sẽ fail nếu không có API key/secret trong config. Đây là bình thường.

## Bước 5: Xem Dashboard và Monitoring

### Swagger UI:
- API Documentation: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Các endpoint quan trọng:
- `GET /api/config/` - Danh sách bot configs
- `GET /api/orders/history` - Lịch sử lệnh
- `GET /api/monitoring/status` - Trạng thái bots
- `POST /api/monitoring/status/{id}/pause` - Tạm dừng bot
- `POST /api/monitoring/status/{id}/resume` - Tiếp tục bot

## Bước 6: Chạy Frontend React (Tùy chọn)

```bash
cd frontend
npm install
npm run dev
```

Frontend sẽ chạy tại: http://localhost:3000

## Checklist

- [ ] Tạo user admin đầu tiên
- [ ] Đăng nhập và lấy token
- [ ] Tạo bot config đầu tiên
- [ ] Test các endpoint khác
- [ ] (Tùy chọn) Chạy frontend React

## Troubleshooting

### Lỗi 401 Unauthorized
- Kiểm tra token có đúng không
- Token có thể đã hết hạn (mặc định 24h), đăng nhập lại

### Lỗi 404 Not Found
- Kiểm tra endpoint URL có đúng không
- Kiểm tra server có đang chạy không

### Lỗi 500 Internal Server Error
- Xem logs trong console của server
- Kiểm tra database có được tạo đúng không

## Next Steps

1. Cấu hình API key/secret cho exchange (nếu muốn test thật)
2. Tích hợp với TradingView alerts
3. Cấu hình Telegram notifications
4. Deploy lên production server

