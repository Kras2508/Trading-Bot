# Hướng dẫn Thêm API Key qua Swagger UI

## Bước 1: Đăng nhập

1. Mở Swagger UI: http://127.0.0.1:8000/docs
2. Tìm endpoint `POST /api/auth/login`
3. Click "Try it out"
4. Điền:
   - `username`: your-username
   - `password`: your-password
5. Click "Execute"
6. Copy `access_token` từ response

## Bước 2: Authorize

1. Click nút **"Authorize"** ở đầu trang Swagger
2. Nhập: `Bearer YOUR_ACCESS_TOKEN`
3. Click "Authorize" → "Close"

## Bước 3: Lấy danh sách configs

1. Tìm endpoint `GET /api/config/`
2. Click "Try it out" → "Execute"
3. Xem danh sách configs
4. Copy `id` của config bạn muốn thêm API key

## Bước 4: Cập nhật config với API key

1. Tìm endpoint `PUT /api/config/{config_id}`
2. Click "Try it out"
3. Điền `config_id`: ID vừa copy (VD: `1`)
4. Trong Request body, điền:

```json
{
  "api_key": "Nk2SufxLinCEYVC98ghNd9sRr3NpdkcgbZgWU1MXn7setQboIlSdDv2gbHmgEWiq",
  "api_secret": "aXUTSRziPY0vZT9q4z6VCddhtxMHDYwDT0Q8pOyJa3igza5bK6HvxjpS4ar4yYD6"
}
```

5. Click "Execute"

## Bước 5: Xác nhận

Nếu thành công (Status 200), API key/secret đã được:
- ✅ Mã hóa
- ✅ Lưu vào database
- ✅ Sẵn sàng để đặt lệnh

## Sau khi thêm API key:

Bạn có thể:
1. Đặt lệnh trực tiếp: `POST /api/trading/place-order`
2. Hoặc dùng webhook: `POST /api/webhook/tradingview`

## Lưu ý bảo mật:

⚠️ **QUAN TRỌNG:**
- API key/secret đã được mã hóa trong database
- Không chia sẻ API key/secret với ai
- Chỉ bật quyền **Spot Trading** trên Binance
- ❌ **KHÔNG** bật quyền **Withdrawals** (bảo mật)

