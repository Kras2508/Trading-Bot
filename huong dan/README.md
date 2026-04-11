# Trading Bot Backend API

Backend API quản lý và điều khiển hệ thống trading bot với đầy đủ tính năng CRUD, webhook TradingView, SL/TP/Trailing nâng cao, và tích hợp Telegram.

## Tính năng chính

1. **Backend quản lý cấu hình (FastAPI)**
   - CRUD API cho cấu hình bot (symbol, amount, SL, TP, trailing, leverage...)
   - Hỗ trợ nhiều bot config
   - Mã hóa API key/secret trong database

2. **Auth & Bảo mật**
   - Xác thực JWT
   - Mã hóa API key/secret trong DB
   - IP whitelist cho webhook

3. **Database (SQLite/PostgreSQL)**
   - Lưu cấu hình bot
   - Lịch sử lệnh
   - Nhật ký hoạt động
   - Trạng thái bot

4. **Webhook TradingView (DB-driven)**
   - Endpoint `/api/webhook/tradingview` đọc cấu hình trực tiếp từ DB
   - Tránh trùng lệnh
   - Hỗ trợ cả Spot và Futures

5. **SL / TP / Trailing nâng cao**
   - Hỗ trợ nhiều TP (TP1/TP2...)
   - Trailing theo ATR hoặc %
   - Trailing linh hoạt

6. **Logging & Order History API**
   - API `/api/orders/history` với lọc theo thời gian
   - Lọc theo symbol, status, side, bot config

7. **Telegram Notify & Monitoring**
   - Gửi trạng thái bot
   - Cảnh báo lỗi
   - Tự động báo khi bot tạm dừng

## Cài đặt

### Yêu cầu
- Python 3.8+
- PostgreSQL (tùy chọn) hoặc SQLite (mặc định)

### Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Cấu hình môi trường

Tạo file `.env`:

```env
# App
DEBUG=False

# Database
DATABASE_URL=sqlite:///./trading_bot.db
# Hoặc PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/dbname

# Security
SECRET_KEY=your-secret-key-change-in-production
ENCRYPTION_KEY=your-32-byte-encryption-key-change-this

# CORS
CORS_ORIGINS=["*"]

# IP Whitelist
ENABLE_IP_WHITELIST=False
ALLOWED_IPS=127.0.0.1,192.168.1.1

# Telegram
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id
ENABLE_TELEGRAM=True

# Exchange
DEFAULT_EXCHANGE=binance
```

### Chạy ứng dụng

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Sau khi chạy server, truy cập:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Đăng ký user mới
- `POST /api/auth/login` - Đăng nhập, nhận JWT token
- `GET /api/auth/me` - Lấy thông tin user hiện tại

### Configuration
- `POST /api/config/` - Tạo bot config mới
- `GET /api/config/` - Danh sách tất cả configs
- `GET /api/config/{config_id}` - Lấy config theo ID
- `PUT /api/config/{config_id}` - Cập nhật config
- `DELETE /api/config/{config_id}` - Xóa config

### Webhook
- `POST /api/webhook/tradingview` - Webhook nhận alert từ TradingView

### Orders
- `GET /api/orders/history` - Lịch sử lệnh với filtering
- `GET /api/orders/{order_id}` - Chi tiết một lệnh
- `GET /api/orders/` - Danh sách tất cả lệnh

### Monitoring
- `GET /api/monitoring/status` - Trạng thái tất cả bots
- `GET /api/monitoring/status/{bot_config_id}` - Trạng thái một bot
- `POST /api/monitoring/status/{bot_config_id}/pause` - Tạm dừng bot
- `POST /api/monitoring/status/{bot_config_id}/resume` - Tiếp tục bot
- `GET /api/monitoring/logs` - Nhật ký hoạt động
- `GET /api/monitoring/health` - Health check hệ thống

## Sử dụng Webhook TradingView

### Cấu hình TradingView Alert

1. Tạo alert trong TradingView
2. Webhook URL: `http://your-server:8000/api/webhook/tradingview`
3. Alert Message (JSON):
```json
{
  "symbol": "BTC/USDT",
  "action": "buy",
  "config": "my_bot_config_name"
}
```

Hoặc đơn giản hơn:
```json
{
  "ticker": "BTCUSDT",
  "side": "buy",
  "bot_name": "my_bot_config_name"
}
```

### Các trường hỗ trợ:
- `symbol` hoặc `ticker`: Symbol cần trade
- `action` hoặc `side`: "buy" hoặc "sell"
- `config` hoặc `bot_name`: Tên bot config (tùy chọn, sẽ tìm theo symbol nếu không có)

## Cấu hình Bot

### Ví dụ tạo bot config:

```json
{
  "name": "BTC Spot Bot",
  "symbol": "BTC/USDT",
  "exchange": "binance",
  "amount": 100.0,
  "leverage": 1,
  "stop_loss_percent": 2.0,
  "take_profit_percent": 5.0,
  "tp_levels": [
    {"percent": 3.0, "close_percent": 50},
    {"percent": 5.0, "close_percent": 50}
  ],
  "enable_trailing": true,
  "trailing_type": "percent",
  "trailing_percent": 1.5,
  "trading_mode": "spot",
  "api_key": "your-api-key",
  "api_secret": "your-api-secret",
  "enable_notifications": true
}
```

### Trailing Stop

**Trailing theo %:**
```json
{
  "enable_trailing": true,
  "trailing_type": "percent",
  "trailing_percent": 1.5
}
```

**Trailing theo ATR:**
```json
{
  "enable_trailing": true,
  "trailing_type": "atr",
  "trailing_atr_multiplier": 2.0,
  "trailing_atr_period": 14
}
```

## Bảo mật

1. **JWT Authentication**: Tất cả endpoints (trừ webhook) yêu cầu JWT token
2. **Encryption**: API keys và secrets được mã hóa trong database
3. **IP Whitelist**: Có thể bật IP whitelist cho webhook
4. **HTTPS**: Nên sử dụng HTTPS trong production

## Logging

Logs được lưu trong thư mục `logs/app.log` và cũng hiển thị trên console.

## Telegram Notifications

Cấu hình Telegram trong `.env`:
- `TELEGRAM_BOT_TOKEN`: Token từ BotFather
- `TELEGRAM_CHAT_ID`: Chat ID nhận thông báo
- `ENABLE_TELEGRAM`: Bật/tắt thông báo

## Database Schema

### BotConfig
- Cấu hình bot (symbol, amount, SL, TP, trailing...)

### Order
- Lịch sử lệnh với đầy đủ thông tin

### ActivityLog
- Nhật ký hoạt động hệ thống

### BotStatus
- Trạng thái và thống kê bot

### User
- Quản lý users và authentication

## Development

### Cấu trúc thư mục

```
app/
├── core/           # Core config, security, logging
├── models/         # Database models
├── schemas/        # Pydantic schemas
├── routers/        # API routes
├── services/       # Business logic
├── utils/          # Utilities
└── main.py         # FastAPI app
```

## License

Proprietary - All rights reserved

