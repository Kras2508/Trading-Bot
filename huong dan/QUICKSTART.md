# Hướng dẫn Nhanh - Quick Start

## Bước 1: Cài đặt Dependencies

```bash
# Tạo virtual environment (khuyến nghị)
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Cài đặt packages
pip install -r requirements.txt
```

## Bước 2: Cấu hình Environment

Tạo file `.env` từ template:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Chỉnh sửa file `.env` với các thông tin cơ bản:

```env
# Bắt buộc: Tạo secret key ngẫu nhiên
SECRET_KEY=your-random-secret-key-min-32-chars
ENCRYPTION_KEY=your-random-32-byte-key

# Database (SQLite mặc định - không cần cấu hình)
DATABASE_URL=sqlite:///./trading_bot.db

# Telegram (tùy chọn - có thể bỏ qua nếu chưa có)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
ENABLE_TELEGRAM=False
```

## Bước 3: Chạy Server

```bash
python run.py
```

Server sẽ chạy tại: `http://localhost:8000`

## Bước 4: Truy cập API Documentation

Mở trình duyệt và truy cập:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Bước 5: Tạo User đầu tiên

### Cách 1: Dùng Swagger UI
1. Mở http://localhost:8000/docs
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

### Cách 2: Dùng curl
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "your-secure-password",
    "is_admin": true
  }'
```

## Bước 6: Đăng nhập để lấy Token

### Cách 1: Dùng Swagger UI
1. Tìm endpoint `POST /api/auth/login`
2. Click "Try it out"
3. Điền:
   - `username`: admin
   - `password`: your-secure-password
4. Click "Execute"
5. Copy `access_token` từ response

### Cách 2: Dùng curl
```bash
curl -X POST "http://localhost:8000/api/auth/login?username=admin&password=your-secure-password"
```

Response sẽ có dạng:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Bước 7: Tạo Bot Config đầu tiên

### Cách 1: Dùng Swagger UI
1. Click nút "Authorize" ở đầu trang
2. Nhập: `Bearer YOUR_ACCESS_TOKEN`
3. Tìm endpoint `POST /api/config/`
4. Click "Try it out"
5. Điền thông tin config (ví dụ):

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

### Cách 2: Dùng curl
```bash
curl -X POST "http://localhost:8000/api/config/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "BTC Spot Bot",
    "symbol": "BTC/USDT",
    "exchange": "binance",
    "amount": 100.0,
    "stop_loss_percent": 2.0,
    "take_profit_percent": 5.0,
    "trading_mode": "spot"
  }'
```

## Bước 8: Test Webhook (TradingView)

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

### Cách 2: Dùng curl
```bash
curl -X POST "http://localhost:8000/api/webhook/tradingview" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC/USDT",
    "action": "buy",
    "config": "BTC Spot Bot"
  }'
```

## Bước 9: Xem Lịch sử Lệnh

```bash
curl -X GET "http://localhost:8000/api/orders/history" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Bước 10: Xem Trạng thái Bot

```bash
curl -X GET "http://localhost:8000/api/monitoring/status/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Cấu hình TradingView Alert

1. Tạo alert trong TradingView
2. Webhook URL: `http://your-server:8000/api/webhook/tradingview`
3. Alert Message (JSON):
```json
{
  "symbol": "BTC/USDT",
  "action": "buy",
  "config": "BTC Spot Bot"
}
```

## Troubleshooting

### Lỗi: Module not found
```bash
pip install -r requirements.txt
```

### Lỗi: Database connection
- Kiểm tra `DATABASE_URL` trong `.env`
- Đảm bảo thư mục có quyền ghi (cho SQLite)

### Lỗi: Authentication failed
- Kiểm tra token có đúng không
- Token có thể đã hết hạn (mặc định 24h), đăng nhập lại

### Lỗi: Webhook không hoạt động
- Kiểm tra bot config có tồn tại không
- Kiểm tra bot có bị pause không
- Xem logs trong `logs/app.log`

## Next Steps

1. Đọc `README.md` để hiểu đầy đủ các tính năng
2. Đọc `DEPLOYMENT.md` để triển khai production
3. Xem `examples/api_usage.py` để học cách sử dụng API
4. Xem `PROJECT_SUMMARY.md` để tổng quan dự án

## Cần hỗ trợ?

- Xem API docs tại `/docs`
- Kiểm tra logs tại `logs/app.log`
- Đọc documentation files trong project

