# Hướng dẫn Thêm API Key vào Bot Config

## API Key bạn đã cung cấp:

- **API Key:** `Nk2SufxLinCEYVC98ghNd9sRr3NpdkcgbZgWU1MXn7setQboIlSdDv2gbHmgEWiq`
- **API Secret:** `aXUTSRziPY0vZT9q4z6VCddhtxMHDYwDT0Q8pOyJa3igza5bK6HvxjpS4ar4yYD6`

## Cách 1: Qua Swagger UI (Dễ nhất)

### Bước 1: Đăng nhập
1. Mở: http://127.0.0.1:8000/docs
2. Tìm `POST /api/auth/login`
3. Đăng nhập và copy `access_token`

### Bước 2: Authorize
1. Click nút **"Authorize"** ở đầu trang
2. Nhập: `Bearer YOUR_ACCESS_TOKEN`
3. Click "Authorize"

### Bước 3: Lấy config ID
1. Tìm `GET /api/config/`
2. Execute → xem danh sách → copy `id` (VD: `1`)

### Bước 4: Cập nhật config
1. Tìm `PUT /api/config/{config_id}`
2. Điền `config_id`: `1` (hoặc ID bạn vừa copy)
3. Request body:
```json
{
  "api_key": "Nk2SufxLinCEYVC98ghNd9sRr3NpdkcgbZgWU1MXn7setQboIlSdDv2gbHmgEWiq",
  "api_secret": "aXUTSRziPY0vZT9q4z6VCddhtxMHDYwDT0Q8pOyJa3igza5bK6HvxjpS4ar4yYD6"
}
```
4. Click "Execute"

✅ **Xong!** API key đã được mã hóa và lưu vào database.

## Cách 2: Dùng Script

### Script tự động:
```bash
python THEM_API_KEY_AUTO.py
```

**Lưu ý:** Script sẽ tự động thêm vào config đầu tiên. Nếu cần chọn config khác, sửa script hoặc dùng Swagger UI.

### Script tương tác:
```bash
python THEM_API_KEY_VAO_CONFIG.py
```

Script sẽ hỏi bạn chọn config và nhập API key.

## Sau khi thêm API key:

Bạn có thể đặt lệnh:

### 1. Đặt lệnh trực tiếp:
```bash
POST /api/trading/place-order
{
  "bot_config_id": 1,
  "side": "buy"
}
```

### 2. Hoặc qua webhook:
```bash
POST /api/webhook/tradingview
{
  "symbol": "BTC/USDT",
  "action": "buy",
  "config": "Bot Name"
}
```

## Kiểm tra API key đã được thêm:

1. Tìm `GET /api/config/{config_id}`
2. Execute
3. Response sẽ có `api_key_encrypted` và `api_secret_encrypted` (đã mã hóa)

## Lưu ý bảo mật:

⚠️ **QUAN TRỌNG:**
1. ✅ API key/secret đã được **mã hóa** trong database
2. ✅ Chỉ bật quyền **Spot Trading** trên Binance
3. ❌ **KHÔNG** bật quyền **Withdrawals**
4. ❌ Không chia sẻ API key/secret với ai
5. ✅ Kiểm tra logs thường xuyên

## Test đặt lệnh:

Sau khi thêm API key, test với số tiền nhỏ:

```bash
POST /api/trading/place-order
{
  "bot_config_id": 1,
  "side": "buy",
  "amount": 10.0  # Test với số tiền nhỏ!
}
```

⚠️ **Cảnh báo:** Đây là lệnh THẬT trên Binance, sẽ mất tiền nếu lệnh được fill!

