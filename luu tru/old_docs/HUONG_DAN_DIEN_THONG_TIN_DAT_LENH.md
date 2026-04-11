# Hướng dẫn Điền Thông Tin Đặt Lệnh

## API: POST /api/trading/place-order

### Các trường cần điền:

```json
{
  "bot_config_id": 0,      // ⚠️ BẮT BUỘC - ID của bot config
  "side": "sell",           // ⚠️ BẮT BUỘC - "buy" hoặc "sell"
  "amount": 1,              // ✅ TÙY CHỌN - Số tiền (nếu không có, dùng amount từ config)
  "price": 1,               // ✅ TÙY CHỌN - Giá (chỉ cần nếu order_type="limit")
  "order_type": "market"    // ✅ TÙY CHỌN - "market" (mặc định) hoặc "limit"
}
```

## Chi tiết từng trường:

### 1. `bot_config_id` (BẮT BUỘC)
- **Là gì:** ID của bot config bạn đã tạo
- **Lấy ở đâu:** 
  - Xem danh sách configs: `GET /api/config/`
  - Hoặc sau khi tạo config, lấy `id` từ response
- **Ví dụ:** `1`, `2`, `3`...

**Cách lấy:**
1. Mở Swagger UI: http://127.0.0.1:8000/docs
2. Tìm `GET /api/config/`
3. Click "Try it out" → "Execute"
4. Xem danh sách configs, copy `id` của config bạn muốn dùng

### 2. `side` (BẮT BUỘC)
- **Là gì:** Hướng lệnh - mua hay bán
- **Giá trị:** 
  - `"buy"` - Mua (long)
  - `"sell"` - Bán (short)
- **Ví dụ:** `"buy"` hoặc `"sell"`

### 3. `amount` (TÙY CHỌN)
- **Là gì:** Số tiền đặt lệnh
- **Đơn vị:** USDT (hoặc base currency của symbol)
- **Nếu không điền:** Sẽ dùng `amount` từ bot config
- **Ví dụ:** `100.0`, `50.5`, `200`

**Lưu ý:** 
- Phải lớn hơn 0
- Phải đủ số dư trên Binance

### 4. `price` (TÙY CHỌN - Chỉ cần cho limit order)
- **Là gì:** Giá đặt lệnh (cho limit order)
- **Khi nào cần:** Chỉ khi `order_type="limit"`
- **Khi nào không cần:** Khi `order_type="market"` (có thể bỏ trống)
- **Ví dụ:** `50000.0`, `3000.5`

**Lưu ý:**
- Phải lớn hơn 0
- Phải hợp lý với giá thị trường

### 5. `order_type` (TÙY CHỌN)
- **Là gì:** Loại lệnh
- **Giá trị:**
  - `"market"` - Lệnh thị trường (mặc định) - Mua/bán ngay với giá hiện tại
  - `"limit"` - Lệnh giới hạn - Chờ giá đạt mức chỉ định
- **Mặc định:** `"market"` (nếu không điền)

## Ví dụ cụ thể:

### Ví dụ 1: Market Order - Mua ngay (Đơn giản nhất)
```json
{
  "bot_config_id": 1,
  "side": "buy"
}
```
- Không cần `amount` → dùng amount từ config
- Không cần `price` → market order
- Không cần `order_type` → mặc định "market"

### Ví dụ 2: Market Order - Bán với số tiền chỉ định
```json
{
  "bot_config_id": 1,
  "side": "sell",
  "amount": 50.0
}
```

### Ví dụ 3: Limit Order - Mua với giá chỉ định
```json
{
  "bot_config_id": 1,
  "side": "buy",
  "order_type": "limit",
  "price": 50000.0,
  "amount": 100.0
}
```
- **Bắt buộc có `price`** vì là limit order

### Ví dụ 4: Limit Order - Bán với giá chỉ định
```json
{
  "bot_config_id": 1,
  "side": "sell",
  "order_type": "limit",
  "price": 52000.0
}
```
- Không có `amount` → dùng amount từ config

## Checklist trước khi đặt lệnh:

- [ ] Đã đăng nhập và có JWT token
- [ ] Đã tạo bot config với API key/secret từ Binance
- [ ] Bot config đang active (`is_active: true`)
- [ ] Bot không bị pause
- [ ] Đã biết `bot_config_id` cần dùng
- [ ] Đã kiểm tra số dư trên Binance
- [ ] Đã xác nhận đây là lệnh THẬT (sẽ mất tiền nếu fill)

## Các bước thực hiện:

### Bước 1: Lấy bot_config_id
1. Mở Swagger UI: http://127.0.0.1:8000/docs
2. Click "Authorize" → nhập `Bearer YOUR_TOKEN`
3. Tìm `GET /api/config/`
4. Click "Try it out" → "Execute"
5. Xem danh sách, copy `id` của config bạn muốn

### Bước 2: Điền thông tin
```json
{
  "bot_config_id": 1,        // ← ID vừa copy
  "side": "buy",              // ← "buy" hoặc "sell"
  "order_type": "market"      // ← "market" hoặc "limit"
}
```

### Bước 3: Execute
- Click "Execute"
- Xem kết quả

## Lưu ý quan trọng:

1. ⚠️ **Đây là lệnh THẬT** - Sẽ đặt lệnh thật trên Binance
2. ⚠️ **Sẽ mất tiền** nếu lệnh được fill
3. ✅ **Test với số tiền nhỏ** trước
4. ✅ **Kiểm tra bot config** có API key/secret đúng không
5. ✅ **Sử dụng Binance Testnet** để test an toàn

## Troubleshooting:

### Lỗi: "Bot config X not found or inactive"
- Kiểm tra `bot_config_id` có đúng không
- Kiểm tra config có `is_active: true` không

### Lỗi: "Bot X is paused"
- Bot đang bị pause
- Cần resume bot trước: `POST /api/monitoring/status/{id}/resume`

### Lỗi: "Bot config missing API credentials"
- Config chưa có API key/secret
- Cần cập nhật config với API key/secret từ Binance

### Lỗi: "binance requires 'apiKey' credential"
- API key/secret không đúng hoặc không có
- Kiểm tra lại API key/secret trong config

