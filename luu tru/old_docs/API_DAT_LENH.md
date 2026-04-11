# API Đặt Lệnh Trading

## API Chính: Webhook TradingView

### Endpoint: `POST /api/webhook/tradingview`

Đây là API chính để đặt lệnh. Hệ thống sẽ:
1. Nhận alert từ TradingView
2. Đọc cấu hình bot từ database
3. Tự động đặt lệnh trên exchange
4. Lưu vào database
5. Gửi thông báo Telegram (nếu bật)

### Cách sử dụng:

#### 1. Từ TradingView Alert:

**Webhook URL:**
```
http://your-server:8000/api/webhook/tradingview
```

**Alert Message (JSON):**
```json
{
  "symbol": "BTC/USDT",
  "action": "buy",
  "config": "BTC Spot Bot"
}
```

Hoặc đơn giản hơn:
```json
{
  "ticker": "BTCUSDT",
  "side": "buy",
  "bot_name": "BTC Spot Bot"
}
```

#### 2. Test thủ công bằng curl:

```bash
curl -X POST "http://127.0.0.1:8000/api/webhook/tradingview" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC/USDT",
    "action": "buy",
    "config": "BTC Spot Bot"
  }'
```

#### 3. Test bằng Swagger UI:

1. Mở: http://127.0.0.1:8000/docs
2. Tìm endpoint `POST /api/webhook/tradingview`
3. Click "Try it out"
4. Điền payload JSON
5. Click "Execute"

### Các trường hỗ trợ:

- `symbol` hoặc `ticker`: Symbol cần trade (VD: "BTC/USDT", "BTCUSDT")
- `action` hoặc `side`: "buy" hoặc "sell"
- `config` hoặc `bot_name`: Tên bot config (tùy chọn, sẽ tìm theo symbol nếu không có)

### Response:

**Thành công:**
```json
{
  "status": "success",
  "order_id": 1,
  "symbol": "BTC/USDT",
  "side": "buy",
  "amount": 100.0,
  "price": 50000.0,
  "stop_loss": 49000.0,
  "take_profit": 52500.0
}
```

**Lỗi:**
```json
{
  "detail": "No active bot config found for symbol: BTC/USDT"
}
```

## Lưu ý quan trọng:

1. **Bot config phải có API key/secret** để đặt lệnh thật
2. **Bot config phải active** (`is_active: true`)
3. **Bot không được pause** (`is_paused: false`)
4. **Tránh trùng lệnh**: Hệ thống tự động kiểm tra và tránh đặt lệnh trùng

## Xem lệnh đã đặt:

### Endpoint: `GET /api/orders/history`

Xem tất cả lệnh đã đặt:
```bash
curl -X GET "http://127.0.0.1:8000/api/orders/history" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Endpoint: `GET /api/orders/{order_id}`

Xem chi tiết một lệnh:
```bash
curl -X GET "http://127.0.0.1:8000/api/orders/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Cấu hình Bot trước khi đặt lệnh:

1. Tạo bot config với API key/secret (sẽ được mã hóa)
2. Đảm bảo config có:
   - Symbol đúng
   - Amount hợp lệ
   - SL/TP được cấu hình
   - Trading mode (spot/futures)

## Ví dụ đầy đủ:

### Bước 1: Tạo bot config
```bash
POST /api/config/
{
  "name": "BTC Spot Bot",
  "symbol": "BTC/USDT",
  "exchange": "binance",
  "amount": 100.0,
  "stop_loss_percent": 2.0,
  "take_profit_percent": 5.0,
  "trading_mode": "spot",
  "api_key": "your-api-key",
  "api_secret": "your-api-secret"
}
```

### Bước 2: Đặt lệnh qua webhook
```bash
POST /api/webhook/tradingview
{
  "symbol": "BTC/USDT",
  "action": "buy",
  "config": "BTC Spot Bot"
}
```

### Bước 3: Xem kết quả
```bash
GET /api/orders/history
```

