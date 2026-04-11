# Hướng dẫn Đặt Lệnh Trực Tiếp Lên Binance

## API Đặt Lệnh Trực Tiếp

### Endpoint: `POST /api/trading/place-order`

API này cho phép đặt lệnh trực tiếp lên Binance mà **không cần qua webhook TradingView**.

## Yêu cầu

1. **Phải đăng nhập** và có JWT token
2. **Bot config phải có API key/secret** từ Binance
3. **Bot config phải active** (`is_active: true`)
4. **Bot không được pause**

## Cách sử dụng

### 1. Đăng nhập để lấy token

```bash
POST /api/auth/login
{
  "username": "your-username",
  "password": "your-password"
}
```

### 2. Đặt lệnh trực tiếp

```bash
POST /api/trading/place-order
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "bot_config_id": 1,
  "side": "buy",
  "amount": 100.0,
  "order_type": "market"
}
```

### 3. Các tham số

- `bot_config_id` (bắt buộc): ID của bot config
- `side` (bắt buộc): "buy" hoặc "sell"
- `amount` (tùy chọn): Số tiền đặt lệnh. Nếu không có, dùng amount từ config
- `price` (tùy chọn): Giá cho limit order (bắt buộc nếu `order_type="limit"`)
- `order_type` (tùy chọn): "market" (mặc định) hoặc "limit"

### 4. Ví dụ đầy đủ

#### Market Order (Mua ngay):
```json
{
  "bot_config_id": 1,
  "side": "buy",
  "order_type": "market"
}
```

#### Limit Order (Mua với giá chỉ định):
```json
{
  "bot_config_id": 1,
  "side": "buy",
  "order_type": "limit",
  "price": 50000.0,
  "amount": 100.0
}
```

#### Sell Order:
```json
{
  "bot_config_id": 1,
  "side": "sell",
  "order_type": "market",
  "amount": 50.0
}
```

## Response

### Thành công:
```json
{
  "status": "success",
  "order_id": 1,
  "exchange_order_id": "12345678",
  "symbol": "BTC/USDT",
  "side": "buy",
  "order_type": "market",
  "amount": 100.0,
  "price": 50000.0,
  "filled_price": 50000.0,
  "stop_loss": 49000.0,
  "take_profit": 52500.0,
  "order_status": "filled"
}
```

### Lỗi:
```json
{
  "detail": "Bot config 1 not found or inactive"
}
```

## Các API khác

### 1. Kiểm tra trạng thái lệnh

```bash
GET /api/trading/check-order/{order_id}
Authorization: Bearer YOUR_TOKEN
```

Kiểm tra trạng thái lệnh trên Binance và cập nhật trong database.

### 2. Đóng lệnh (Close Position)

```bash
POST /api/trading/close-order/{order_id}
Authorization: Bearer YOUR_TOKEN
```

Đóng lệnh đang mở (sell nếu đã buy, buy nếu đã sell).

## So sánh với Webhook

| Tính năng | Webhook | Direct API |
|-----------|---------|------------|
| Cần TradingView | ✅ Có | ❌ Không |
| Đặt lệnh thủ công | ❌ Không | ✅ Có |
| Tự động từ alert | ✅ Có | ❌ Không |
| Cần JWT token | ❌ Không | ✅ Có |
| Kiểm soát tốt hơn | ❌ | ✅ |

## Ví dụ sử dụng với curl

```bash
# 1. Đăng nhập
TOKEN=$(curl -X POST "http://127.0.0.1:8000/api/auth/login?username=admin&password=pass" | jq -r '.access_token')

# 2. Đặt lệnh mua
curl -X POST "http://127.0.0.1:8000/api/trading/place-order" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_config_id": 1,
    "side": "buy",
    "order_type": "market"
  }'

# 3. Kiểm tra lệnh
curl -X GET "http://127.0.0.1:8000/api/trading/check-order/1" \
  -H "Authorization: Bearer $TOKEN"
```

## Ví dụ sử dụng với Python

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

# 1. Đăng nhập
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    params={"username": "admin", "password": "pass"}
)
token = response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# 2. Đặt lệnh
response = requests.post(
    f"{BASE_URL}/api/trading/place-order",
    headers=headers,
    json={
        "bot_config_id": 1,
        "side": "buy",
        "order_type": "market"
    }
)

print(response.json())
```

## Lưu ý

1. ⚠️ **Đây là lệnh THẬT** trên Binance, sẽ mất tiền nếu lệnh được fill
2. ✅ **Test với số tiền nhỏ** trước
3. ✅ **Kiểm tra bot config** có API key/secret đúng không
4. ✅ **Kiểm tra balance** trên Binance trước khi đặt lệnh
5. ✅ **Sử dụng Binance Testnet** để test an toàn

## Test với Swagger UI

1. Mở: http://127.0.0.1:8000/docs
2. Click "Authorize" → nhập `Bearer YOUR_TOKEN`
3. Tìm endpoint `POST /api/trading/place-order`
4. Click "Try it out"
5. Điền thông tin và Execute

