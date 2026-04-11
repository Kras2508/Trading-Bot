# Lịch Sử Vị Thế (Position History)

## Giải Thích

**"Lịch sử vị thế"** trong Binance app chính là các **position đã đóng** (closed positions).

Trong hệ thống của bạn, các lệnh có **`status = "closed"`** chính là **"Lịch sử vị thế"**.

---

## So Sánh

| Binance App | Hệ Thống Của Bạn |
|-------------|------------------|
| **"Lịch sử vị thế"** | **Orders với `status = "closed"`** |
| PnL đóng (USDT) | `order.pnl` |
| ROI (%) | `order.pnl_percent` |
| Giá vào lệnh | `order.filled_price` |
| Giá đóng cửa trung bình | `order.closed_at` (từ close order) |
| Đã mở | `order.created_at` |
| Đã đóng | `order.closed_at` |

---

## Cách Xem Lịch Sử Vị Thế

### 1. Qua Frontend (Orders Page)

1. Mở trang **Orders**
2. Filter theo **Status = "Đã đóng"** (closed)
3. Xem các lệnh đã đóng với PnL, ROI, giá vào/ra

### 2. Qua API

#### Lấy Tất Cả Lệnh Đã Đóng

```bash
GET /api/orders/completed
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
[
  {
    "id": 123,
    "symbol": "ADAUSDT",
    "side": "buy",
    "status": "closed",           // ✅ Đã đóng
    "filled_price": 0.3861,        // Giá vào lệnh
    "pnl": 0.30,                  // PnL đóng (USDT)
    "pnl_percent": 15.80,         // ROI (%)
    "filled_amount": 50,           // Khối lượng đóng
    "created_at": "2025-12-02T10:27:32Z",  // Đã mở
    "closed_at": "2025-12-02T11:03:35Z"    // Đã đóng
  }
]
```

#### Lọc Theo Symbol

```bash
GET /api/orders/completed?symbol=ADAUSDT
```

#### Lọc Theo Bot Config

```bash
GET /api/orders/completed?bot_config_id=1
```

---

## Lưu Ý

### ✅ Đã Có Trong DB

- Tất cả lệnh đã đóng qua API `/close-order` đều có trong DB
- PnL được lấy từ sàn và lưu vào DB
- Có thể xem lại bất cứ lúc nào

### ⚠️ Chưa Có Trong DB

- Lệnh đóng **thủ công trên Binance app** sẽ **không có** trong DB
- Để có đầy đủ lịch sử, cần đóng lệnh qua API `/close-order`

---

## Tóm Tắt

✅ **"Lịch sử vị thế" = Orders với `status = "closed"`**  
✅ **Xem qua Frontend**: Filter status = "Đã đóng"  
✅ **Xem qua API**: `/api/orders/completed`  
✅ **Có đầy đủ thông tin**: PnL, ROI, giá vào/ra, timestamps  

