# API Đặt Lệnh Trên Binance

## Cách hệ thống đặt lệnh trên Binance

Hệ thống sử dụng thư viện **CCXT** để kết nối và đặt lệnh trực tiếp trên Binance.

### Luồng hoạt động:

1. **Nhận alert từ TradingView** → Webhook endpoint
2. **Đọc config từ database** → Lấy API key/secret (đã mã hóa)
3. **Giải mã credentials** → Dùng để kết nối Binance
4. **Kết nối Binance qua CCXT** → `ccxt.binance()`
5. **Đặt lệnh** → `exchange.create_market_order()` hoặc `create_limit_order()`
6. **Lưu vào database** → Lưu thông tin lệnh
7. **Gửi thông báo** → Telegram (nếu bật)

## API Đặt Lệnh

### 1. Webhook TradingView (Tự động)

**Endpoint:** `POST /api/webhook/tradingview`

Đây là cách chính để đặt lệnh. TradingView gửi alert → hệ thống tự động đặt lệnh.

**Ví dụ:**
```bash
POST http://127.0.0.1:8000/api/webhook/tradingview
Content-Type: application/json

{
  "symbol": "BTC/USDT",
  "action": "buy",
  "config": "BTC Spot Bot"
}
```

**Hệ thống sẽ:**
- Tìm bot config "BTC Spot Bot" trong database
- Lấy API key/secret đã lưu (đã mã hóa)
- Giải mã và kết nối Binance
- Đặt lệnh market buy BTC/USDT với amount từ config
- Tính SL/TP tự động
- Lưu vào database

### 2. Cấu hình Bot trước khi đặt lệnh

**Bắt buộc phải có:**
- API Key từ Binance
- API Secret từ Binance
- Symbol (VD: "BTC/USDT")
- Amount (số tiền đặt lệnh)
- SL/TP percentages

**Tạo config:**
```bash
POST /api/config/
Authorization: Bearer YOUR_TOKEN

{
  "name": "BTC Spot Bot",
  "symbol": "BTC/USDT",
  "exchange": "binance",
  "amount": 100.0,
  "stop_loss_percent": 2.0,
  "take_profit_percent": 5.0,
  "trading_mode": "spot",
  "api_key": "your-binance-api-key",
  "api_secret": "your-binance-api-secret"
}
```

## Cách lấy API Key từ Binance

1. Đăng nhập Binance
2. Vào **API Management**
3. Tạo API Key mới
4. **QUAN TRỌNG:** Chỉ bật quyền:
   - ✅ Enable Reading
   - ✅ Enable Spot & Margin Trading
   - ❌ KHÔNG bật Withdrawals (bảo mật)
5. Copy API Key và Secret Key
6. Nhập vào bot config (sẽ được mã hóa tự động)

## Hỗ trợ các loại lệnh

### Market Order (Mặc định)
- Đặt lệnh ngay với giá thị trường
- Không cần chỉ định price
- Được fill ngay lập tức

### Limit Order
- Đặt lệnh với giá chỉ định
- Cần thêm parameter `price`
- Chờ giá đạt mức chỉ định mới fill

## Hỗ trợ Spot và Futures

### Spot Trading
```json
{
  "trading_mode": "spot",
  "leverage": 1
}
```

### Futures Trading
```json
{
  "trading_mode": "futures",
  "leverage": 10
}
```

Hệ thống tự động set leverage cho futures.

## Xem lệnh đã đặt

### Tất cả lệnh:
```bash
GET /api/orders/history
Authorization: Bearer YOUR_TOKEN
```

### Chi tiết một lệnh:
```bash
GET /api/orders/{order_id}
Authorization: Bearer YOUR_TOKEN
```

Response sẽ có:
- `exchange_order_id`: ID lệnh trên Binance
- `filled_price`: Giá đã fill
- `status`: pending, filled, cancelled, error
- `stop_loss_price`: Giá stop loss
- `take_profit_price`: Giá take profit

## Test đặt lệnh

### 1. Test với API key thật (Cẩn thận!)

**Lưu ý:** Sẽ đặt lệnh thật trên Binance!

```bash
# Tạo config với API key thật
POST /api/config/
{
  "name": "Test Bot",
  "symbol": "BTC/USDT",
  "exchange": "binance",
  "amount": 10.0,  # Chỉ test với số tiền nhỏ!
  "stop_loss_percent": 2.0,
  "take_profit_percent": 5.0,
  "trading_mode": "spot",
  "api_key": "your-real-api-key",
  "api_secret": "your-real-api-secret"
}

# Đặt lệnh qua webhook
POST /api/webhook/tradingview
{
  "symbol": "BTC/USDT",
  "action": "buy",
  "config": "Test Bot"
}
```

### 2. Test với Testnet (An toàn hơn)

Binance có Testnet để test không mất tiền thật:
- Testnet URL: https://testnet.binance.vision/
- Tạo API key trên testnet
- Dùng API key testnet để test

## Lưu ý bảo mật

1. ✅ API key/secret được **mã hóa** trong database
2. ✅ Chỉ bật quyền cần thiết trên Binance
3. ✅ KHÔNG bật quyền Withdrawals
4. ✅ Sử dụng IP whitelist trên Binance (nếu có thể)
5. ✅ Kiểm tra logs thường xuyên

## Troubleshooting

### Lỗi: "binance requires 'apiKey' credential"
- Bot config chưa có API key/secret
- Hoặc API key/secret không đúng

### Lỗi: "Insufficient balance"
- Không đủ số dư trên Binance
- Kiểm tra balance trước khi đặt lệnh

### Lỗi: "Invalid symbol"
- Symbol không đúng format
- Phải là "BTC/USDT" hoặc "BTCUSDT"

### Lệnh không được fill
- Market order: Kiểm tra liquidity
- Limit order: Giá chưa đạt mức chỉ định

