# Hướng Dẫn Pine Script Đặt Lệnh Qua API

## Trả Lời Ngắn Gọn

**CÓ**, Pine Script có thể đẩy dữ liệu qua API đặt lệnh! Có **2 cách**:

1. ✅ **API Endpoint mới** (`/api/trading/place-order-pine`) - **KHUYẾN NGHỊ**
   - Không cần JWT token
   - Hỗ trợ đầy đủ tính năng (amount, price, order_type)
   
2. ✅ **Webhook Endpoint** (`/api/webhook/tradingview`)
   - Không cần JWT token
   - Chỉ hỗ trợ market order, dùng amount từ config

## Chi Tiết

### 1. API Nào Pine Script Có Thể Gọi?

#### ✅ **CÁCH 1 - KHUYẾN NGHỊ**: API Endpoint Cho Pine Script
- **URL**: `POST /api/trading/place-order-pine`
- **Yêu cầu**: Không cần JWT token
- **Bảo mật**: IP whitelist (nếu bật)
- **Tính năng**: ✅ Đầy đủ (amount, price, order_type, symbol)

#### ✅ **CÁCH 2**: Webhook Endpoint
- **URL**: `POST /api/webhook/tradingview`
- **Yêu cầu**: Không cần JWT token
- **Bảo mật**: IP whitelist (nếu bật)
- **Tính năng**: ⚠️ Hạn chế (chỉ market order, dùng amount từ config)

---

## Cách 1: Sử Dụng API Endpoint Cho Pine Script (KHUYẾN NGHỊ)

### Bước 1: Cấu Hình IP Whitelist (Nếu Cần)

Nếu bạn đã bật IP whitelist, cần thêm IP của TradingView vào danh sách:

**File `.env`:**
```env
ENABLE_IP_WHITELIST=true
ALLOWED_IPS=52.89.214.238,52.36.61.30,34.212.75.30,54.218.53.128,52.32.178.7,35.162.51.207,35.160.1.145,34.220.50.114,18.236.148.232,52.24.126.177,35.155.77.1,52.10.83.167,34.211.224.9,52.88.56.195,35.86.171.241,52.88.47.69,34.214.2.85,52.12.45.97
```

**Hoặc tắt IP whitelist:**
```env
ENABLE_IP_WHITELIST=false
```

### Bước 2: Tạo Bot Config Trong Database

Bạn cần có một bot config đã được tạo với:
- `is_active = true`
- Có API key/secret từ Binance
- Có `symbol` và `amount` được cấu hình (nếu không truyền trong request)

### Bước 3: Cấu Hình Alert Trong TradingView

**Ví dụ Pine Script:**
```pinescript
//@version=5
indicator("Trading Bot Signal", overlay=true)

// Điều kiện mua
buy_signal = ta.crossover(ta.sma(close, 20), ta.sma(close, 50))

// Điều kiện bán
sell_signal = ta.crossunder(ta.sma(close, 20), ta.sma(close, 50))

// Vẽ tín hiệu
plotshape(buy_signal, style=shape.triangleup, location=location.belowbar, color=color.green, size=size.small)
plotshape(sell_signal, style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small)

// Alert conditions
alertcondition(buy_signal, title="Buy Signal", message="Buy")
alertcondition(sell_signal, title="Sell Signal", message="Sell")
```

### Bước 4: Cấu Hình Webhook URL Trong TradingView Alert

Khi tạo alert trong TradingView:

1. **Chọn điều kiện**: Buy Signal hoặc Sell Signal
2. **Webhook URL**: 
   ```
   http://YOUR_SERVER_IP:8000/api/trading/place-order-pine
   ```
   Hoặc nếu dùng ngrok:
   ```
   https://YOUR_NGROK_URL.ngrok.io/api/trading/place-order-pine
   ```

3. **Message (JSON format)**:
   ```json
   {
     "bot_config_id": 1,
     "side": "buy",
     "amount": 100.0,
     "symbol": "BTCUSDT",
     "order_type": "market"
   }
   ```

### Format Request Body

```json
{
  "bot_config_id": 1,        // Bắt buộc: ID của bot config
  "side": "buy",             // Bắt buộc: "buy" hoặc "sell"
  "amount": 100.0,           // Tùy chọn: Số tiền (nếu không có, dùng từ config)
  "symbol": "BTCUSDT",       // Tùy chọn: Symbol (nếu không có, dùng từ config)
  "price": 50000.0,          // Tùy chọn: Giá (chỉ cần cho limit order)
  "order_type": "market"     // Tùy chọn: "market" (mặc định) hoặc "limit"
}
```

### Ví Dụ Request

**Market Order:**
```json
{
  "bot_config_id": 1,
  "side": "buy",
  "amount": 100.0,
  "order_type": "market"
}
```

**Limit Order:**
```json
{
  "bot_config_id": 1,
  "side": "buy",
  "amount": 100.0,
  "price": 50000.0,
  "order_type": "limit"
}
```

### Response (Thành Công)

```json
{
  "status": "success",
  "order_id": 123,
  "exchange_order_id": "abc123",
  "symbol": "BTCUSDT",
  "side": "buy",
  "order_type": "market",
  "amount": 100.0,
  "price": 50000.0,
  "filled_price": 50001.5,
  "stop_loss": 48000.0,
  "take_profit": 52000.0,
  "order_status": "filled"
}
```

---

## Cách 2: Sử Dụng Webhook Từ Pine Script

### Bước 1: Cấu Hình IP Whitelist (Nếu Cần)

Nếu bạn đã bật IP whitelist, cần thêm IP của TradingView vào danh sách:

**File `.env`:**
```env
ENABLE_IP_WHITELIST=true
ALLOWED_IPS=52.89.214.238,52.36.61.30,34.212.75.30,54.218.53.128,52.32.178.7,35.162.51.207,35.160.1.145,34.220.50.114,18.236.148.232,52.24.126.177,35.155.77.1,52.10.83.167,34.211.224.9,52.88.56.195,35.86.171.241,52.88.47.69,34.214.2.85,52.12.45.97,35.155.77.1,52.10.83.167,34.211.224.9,52.88.56.195,35.86.171.241,52.88.47.69,34.214.2.85,52.12.45.97
```

**Hoặc tắt IP whitelist:**
```env
ENABLE_IP_WHITELIST=false
```

### Bước 2: Tạo Bot Config Trong Database

Bạn cần có một bot config đã được tạo với:
- `is_active = true`
- Có API key/secret từ Binance
- Có `symbol` và `amount` được cấu hình

### Bước 3: Cấu Hình Alert Trong TradingView

Trong Pine Script, bạn cần tạo alert và cấu hình webhook URL:

**Ví dụ Pine Script:**
```pinescript
//@version=5
indicator("Trading Bot Signal", overlay=true)

// Điều kiện mua
buy_signal = ta.crossover(ta.sma(close, 20), ta.sma(close, 50))

// Điều kiện bán
sell_signal = ta.crossunder(ta.sma(close, 20), ta.sma(close, 50))

// Vẽ tín hiệu
plotshape(buy_signal, style=shape.triangleup, location=location.belowbar, color=color.green, size=size.small)
plotshape(sell_signal, style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small)

// Alert conditions
alertcondition(buy_signal, title="Buy Signal", message="Buy")
alertcondition(sell_signal, title="Sell Signal", message="Sell")
```

### Bước 4: Cấu Hình Webhook URL Trong TradingView Alert

Khi tạo alert trong TradingView, bạn cần:

1. **Chọn điều kiện**: Buy Signal hoặc Sell Signal
2. **Webhook URL**: 
   ```
   http://YOUR_SERVER_IP:8000/api/webhook/tradingview
   ```
   Hoặc nếu dùng ngrok:
   ```
   https://YOUR_NGROK_URL.ngrok.io/api/webhook/tradingview
   ```

3. **Message (JSON format)**:
   ```json
   {
     "symbol": "{{ticker}}",
     "action": "{{strategy.order.action}}",
     "config": "BotConfigName"
   }
   ```

   **Hoặc đơn giản hơn:**
   ```json
   {
     "symbol": "BTCUSDT",
     "action": "buy"
   }
   ```

---

## Format Dữ Liệu Webhook

### Request Body (JSON)

```json
{
  "symbol": "BTCUSDT",        // Bắt buộc: Symbol cần trade
  "action": "buy",             // Bắt buộc: "buy" hoặc "sell"
  "config": "MyBotConfig"      // Tùy chọn: Tên bot config (nếu không có, tìm theo symbol)
}
```

### Các Trường Hỗ Trợ

| Trường | Bắt buộc | Mô tả | Ví dụ |
|--------|----------|-------|-------|
| `symbol` hoặc `ticker` | ✅ | Symbol cần trade | `"BTCUSDT"` |
| `action` hoặc `side` | ✅ | Hướng lệnh | `"buy"`, `"sell"`, `"long"`, `"short"` |
| `config` hoặc `bot_name` | ❌ | Tên bot config | `"MyBotConfig"` |

### Response (Thành Công)

```json
{
  "status": "success",
  "order_id": 123,
  "symbol": "BTCUSDT",
  "side": "buy",
  "amount": 100.0,
  "price": 50000.0,
  "stop_loss": 48000.0,
  "take_profit": 52000.0
}
```

---

## Hạn Chế Của Webhook

So với API `/api/trading/place-order`, webhook có các hạn chế:

| Tính năng | API `/place-order` | Webhook `/tradingview` |
|-----------|-------------------|----------------------|
| JWT Token | ✅ Cần | ❌ Không cần |
| Custom Amount | ✅ Có | ❌ Dùng amount từ config |
| Custom Price | ✅ Có (limit order) | ❌ Không hỗ trợ |
| Order Type | ✅ Market/Limit | ❌ Chỉ Market |
| Custom Symbol | ✅ Có | ✅ Có |

---

## Ví Dụ Hoàn Chỉnh

### 1. Pine Script Code

```pinescript
//@version=5
strategy("Trading Bot Strategy", overlay=true, initial_capital=10000)

// Strategy logic
fast_ma = ta.sma(close, 10)
slow_ma = ta.sma(close, 30)

long_condition = ta.crossover(fast_ma, slow_ma)
short_condition = ta.crossunder(fast_ma, slow_ma)

if (long_condition)
    strategy.entry("Long", strategy.long)
    
if (short_condition)
    strategy.entry("Short", strategy.short)

// Alert messages
alert_message_long = '{"symbol": "' + syminfo.ticker + '", "action": "buy"}'
alert_message_short = '{"symbol": "' + syminfo.ticker + '", "action": "sell"}'

// Create alerts
if (long_condition)
    alert(alert_message_long, alert.freq_once_per_bar)
    
if (short_condition)
    alert(alert_message_short, alert.freq_once_per_bar)
```

### 2. TradingView Alert Configuration

**Webhook URL:**
```
http://192.168.1.100:8000/api/webhook/tradingview
```

**Alert Message:**
```
{"symbol": "{{ticker}}", "action": "{{strategy.order.action}}"}
```

**Hoặc sử dụng biến TradingView:**
```
{"symbol": "{{ticker}}", "action": "buy"}
```

---

## Kiểm Tra Kết Nối

### Test Webhook Bằng cURL

```bash
curl -X POST http://YOUR_SERVER:8000/api/webhook/tradingview \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "action": "buy",
    "config": "MyBotConfig"
  }'
```

### Test Từ Pine Script

Sau khi cấu hình alert, bạn có thể test bằng cách:
1. Tạo alert với điều kiện test
2. Trigger alert thủ công
3. Kiểm tra logs của backend để xem request có đến không

---

## Troubleshooting

### Lỗi 403 Forbidden
- **Nguyên nhân**: IP không trong whitelist
- **Giải pháp**: Tắt IP whitelist hoặc thêm IP vào danh sách

### Lỗi 404 Not Found
- **Nguyên nhân**: Không tìm thấy bot config
- **Giải pháp**: Kiểm tra `symbol` hoặc `config` name có đúng không

### Lỗi 400 Bad Request
- **Nguyên nhân**: Bot đang pause hoặc thiếu API credentials
- **Giải pháp**: Kiểm tra bot config có `is_active=true` và có API key/secret

---

## Tóm Tắt

✅ **Pine Script CÓ THỂ** đặt lệnh qua webhook endpoint  
✅ **Không cần** JWT token  
✅ **Đơn giản** hơn API trực tiếp  
⚠️ **Hạn chế**: Chỉ hỗ trợ market order, dùng amount từ config  
⚠️ **Cần**: Cấu hình IP whitelist (hoặc tắt) và bot config sẵn có

