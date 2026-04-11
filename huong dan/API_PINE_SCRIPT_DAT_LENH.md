# API Đặt Lệnh Cho Pine Script

## Endpoint Mới: `/api/trading/place-order-pine`

✅ **Không cần JWT token** - Pine Script có thể gọi trực tiếp!

## URL

```
POST /api/trading/place-order-pine
```

## Request Body (JSON)

```json
{
  "bot_config_id": 1,        // ⚠️ BẮT BUỘC - ID của bot config
  "side": "buy",             // ⚠️ BẮT BUỘC - "buy" hoặc "sell"
  "amount": 100.0,           // ✅ TÙY CHỌN - Số tiền (nếu không có, dùng từ config)
  "symbol": "BTCUSDT",       // ✅ TÙY CHỌN - Symbol (nếu không có, dùng từ config)
  "price": 50000.0,          // ✅ TÙY CHỌN - Giá (chỉ cần cho limit order)
  "order_type": "market"     // ✅ TÙY CHỌN - "market" (mặc định) hoặc "limit"
}
```

## Ví Dụ

### 1. Market Order (Mua ngay)

```json
{
  "bot_config_id": 1,
  "side": "buy",
  "amount": 100.0,
  "order_type": "market"
}
```

### 2. Limit Order (Mua với giá chỉ định)

```json
{
  "bot_config_id": 1,
  "side": "buy",
  "amount": 100.0,
  "price": 50000.0,
  "order_type": "limit"
}
```

### 3. Bán (Sell)

```json
{
  "bot_config_id": 1,
  "side": "sell",
  "amount": 50.0,
  "order_type": "market"
}
```

## Response (Thành Công)

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

## Cấu Hình TradingView Alert

### Webhook URL:
```
http://YOUR_SERVER:8000/api/trading/place-order-pine
```

### Alert Message (JSON):
```json
{
  "bot_config_id": 1,
  "side": "buy",
  "amount": 100.0,
  "symbol": "{{ticker}}",
  "order_type": "market"
}
```

## So Sánh Với Các Endpoint Khác

| Tính năng | `/place-order` | `/place-order-pine` | `/webhook/tradingview` |
|-----------|---------------|---------------------|----------------------|
| JWT Token | ✅ Cần | ❌ Không cần | ❌ Không cần |
| Custom Amount | ✅ Có | ✅ Có | ❌ Dùng từ config |
| Custom Price | ✅ Có | ✅ Có | ❌ Không hỗ trợ |
| Order Type | ✅ Market/Limit | ✅ Market/Limit | ❌ Chỉ Market |
| Custom Symbol | ✅ Có | ✅ Có | ✅ Có |
| IP Whitelist | ❌ Không | ✅ Có | ✅ Có |

## Bảo Mật

- ✅ **IP Whitelist**: Kiểm tra IP nếu `ENABLE_IP_WHITELIST=true`
- ✅ **Bot Config Validation**: Kiểm tra bot config active và có API credentials
- ✅ **Bot Status Check**: Kiểm tra bot không bị pause

## Lưu Ý

1. **Bot Config ID**: Phải có bot config đã tạo với `is_active=true`
2. **API Credentials**: Bot config phải có API key/secret từ Binance
3. **IP Whitelist**: Nếu bật, cần thêm IP TradingView vào whitelist
4. **Limit Order**: Phải có `price` nếu `order_type="limit"`

## Test Bằng cURL

```bash
curl -X POST http://localhost:8000/api/trading/place-order-pine \
  -H "Content-Type: application/json" \
  -d '{
    "bot_config_id": 1,
    "side": "buy",
    "amount": 100.0,
    "order_type": "market"
  }'
```

## Lỗi Thường Gặp

### 403 Forbidden
- **Nguyên nhân**: IP không trong whitelist
- **Giải pháp**: Tắt IP whitelist hoặc thêm IP vào danh sách

### 404 Not Found
- **Nguyên nhân**: Bot config không tồn tại hoặc không active
- **Giải pháp**: Kiểm tra `bot_config_id` và đảm bảo config `is_active=true`

### 400 Bad Request
- **Nguyên nhân**: Bot bị pause hoặc thiếu API credentials
- **Giải pháp**: Kiểm tra bot status và API key/secret

