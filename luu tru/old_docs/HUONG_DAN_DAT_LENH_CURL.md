# Hướng dẫn Đặt Lệnh bằng curl

## Bước 1: Đăng nhập để lấy Token

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login?username=testuser&password=testpass123"
```

Response sẽ có dạng:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Copy `access_token`** để dùng ở bước sau.

## Bước 2: Đặt lệnh với Token

### Ví dụ đầy đủ:

```bash
curl -X POST "http://127.0.0.1:8000/api/trading/place-order" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -d '{
    "bot_config_id": 1,
    "side": "buy",
    "order_type": "market"
  }'
```

### Thay thế:
- `YOUR_ACCESS_TOKEN_HERE` → Token bạn vừa copy ở bước 1

## Các ví dụ khác:

### 1. Market Order - Mua (Đơn giản nhất)
```bash
curl -X POST "http://127.0.0.1:8000/api/trading/place-order" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_config_id": 1,
    "side": "buy"
  }'
```

### 2. Market Order - Bán với số tiền
```bash
curl -X POST "http://127.0.0.1:8000/api/trading/place-order" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_config_id": 1,
    "side": "sell",
    "amount": 50.0
  }'
```

### 3. Limit Order - Mua với giá
```bash
curl -X POST "http://127.0.0.1:8000/api/trading/place-order" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_config_id": 1,
    "side": "buy",
    "order_type": "limit",
    "price": 50000.0,
    "amount": 100.0
  }'
```

## Script tự động (Windows PowerShell):

```powershell
# 1. Login và lấy token
$loginResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/login?username=testuser&password=testpass123" -Method Post
$token = $loginResponse.access_token

# 2. Đặt lệnh
$body = @{
    bot_config_id = 1
    side = "buy"
    order_type = "market"
} | ConvertTo-Json

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/trading/place-order" -Method Post -Headers $headers -Body $body
```

## Script tự động (Bash/Linux):

```bash
#!/bin/bash

# 1. Login
TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/api/auth/login?username=testuser&password=testpass123" | jq -r '.access_token')

# 2. Đặt lệnh
curl -X POST "http://127.0.0.1:8000/api/trading/place-order" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_config_id": 1,
    "side": "buy",
    "order_type": "market"
  }'
```

## Lưu ý:

1. ⚠️ **Đây là lệnh THẬT** trên Binance
2. ✅ **Test với số tiền nhỏ** trước
3. ✅ **Kiểm tra bot_config_id** có đúng không
4. ✅ **Đảm bảo có đủ số dư** trên Binance

## Troubleshooting:

### Lỗi 401 Unauthorized
- Token đã hết hạn hoặc sai
- Đăng nhập lại để lấy token mới

### Lỗi 404 Bot config not found
- Kiểm tra `bot_config_id` có đúng không
- Xem danh sách configs: `GET /api/config/`

### Lỗi 400 Bot is paused
- Bot đang bị pause
- Resume bot: `POST /api/monitoring/status/{id}/resume`

