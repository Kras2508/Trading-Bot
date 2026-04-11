# Cách Đặt Lệnh với curl (Đơn giản)

## Bước 1: Lấy Token

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login?username=testuser&password=testpass123"
```

**Copy `access_token`** từ response.

## Bước 2: Đặt lệnh (Thay YOUR_TOKEN)

```bash
curl -X POST "http://127.0.0.1:8000/api/trading/place-order" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "bot_config_id": 1,
    "side": "buy",
    "order_type": "market"
  }'
```

## Ví dụ đầy đủ (1 dòng):

```bash
TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/api/auth/login?username=testuser&password=testpass123" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4) && curl -X POST "http://127.0.0.1:8000/api/trading/place-order" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"bot_config_id":1,"side":"buy","order_type":"market"}'
```

## Lưu ý:

1. **Thay `YOUR_TOKEN`** bằng token thật từ bước 1
2. **Kiểm tra `bot_config_id`** có đúng không (hiện tại là 1)
3. ⚠️ **Đây là lệnh THẬT** trên Binance

## Các tham số:

- `bot_config_id`: 1 (ID của config đã có API key)
- `side`: "buy" hoặc "sell"
- `order_type`: "market" (mặc định) hoặc "limit"
- `amount`: Tùy chọn (nếu không có, dùng amount từ config)
- `price`: Chỉ cần khi `order_type="limit"`

