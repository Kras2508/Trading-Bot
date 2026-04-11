# Hướng Dẫn PnL Lấy Từ Sàn (Cách 2)

## ✅ Đã Triển Khai

Hệ thống đã được cập nhật để **lấy PnL từ sàn khi đóng lệnh** và **lưu vào database**.

## Cách Hoạt Động

### 1. Khi Đóng Lệnh

Khi gọi API `POST /api/trading/close-order/{order_id}`:

1. **Đóng lệnh trên sàn** (Binance)
2. **Lấy PnL từ sàn**:
   - **Futures**: Lấy `realizedPnl` từ position (nếu có)
   - **Spot**: Tính từ entry price và exit price
3. **Lưu vào database**:
   - `order.pnl` = PnL (số tiền)
   - `order.pnl_percent` = PnL phần trăm
4. **Cập nhật bot status**: Tổng PnL của bot

### 2. Khi Xem Orders

Trang Orders chỉ **đọc từ database** (rất nhanh, < 100ms), không cần gọi API sàn.

## API Endpoint

### Đóng Lệnh và Lấy PnL

```
POST /api/trading/close-order/{order_id}
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "status": "success",
  "message": "Order 123 closed successfully",
  "order_id": 123,
  "close_order": {...},
  "pnl": 150.50,           // ✅ PnL từ sàn
  "pnl_percent": 3.01,     // ✅ PnL phần trăm
  "close_price": 50150.0   // Giá đóng lệnh
}
```

## Chi Tiết Tính PnL

### Spot Trading

PnL được tính từ:
- **Entry price**: `order.filled_price` (giá khi mua)
- **Exit price**: `close_price` (giá khi bán)
- **Amount**: `order.filled_amount`

**Công thức:**
- **Long (Buy)**: `PnL = (exit_price - entry_price) × amount`
- **Short (Sell)**: `PnL = (entry_price - exit_price) × amount`

**Ví dụ:**
- Mua BTC ở 50000 USDT, bán ở 50150 USDT, số lượng 1 BTC
- PnL = (50150 - 50000) × 1 = **150 USDT**
- PnL% = (150 / 50000) × 100 = **0.3%**

### Futures Trading

1. **Ưu tiên**: Lấy `realizedPnl` từ position API (nếu có)
2. **Fallback**: Tính từ entry/exit price với leverage

**Công thức (nếu không có realizedPnl):**
- **Long**: `PnL = (exit_price - entry_price) × amount × leverage`
- **Short**: `PnL = (entry_price - exit_price) × amount × leverage`

**Ví dụ:**
- Mua BTC futures ở 50000 USDT, bán ở 50150 USDT
- Số lượng: 1 BTC, Leverage: 10x
- PnL = (50150 - 50000) × 1 × 10 = **1500 USDT**
- PnL% = (1500 / 50000) × 100 = **3%**

## Lưu Ý

### ✅ Ưu Điểm

1. **Nhanh**: Khi xem Orders, chỉ đọc từ DB (< 100ms)
2. **Chính xác**: PnL lấy từ sàn khi đóng lệnh
3. **Lịch sử**: Lưu PnL vĩnh viễn, xem lại bất cứ lúc nào
4. **Tiết kiệm**: Không tốn API rate limit khi xem Orders

### ⚠️ Lưu Ý

1. **Chỉ có PnL khi đóng lệnh**: Lệnh đang mở sẽ có `pnl = 0`
2. **Spot trading**: PnL được tính từ giá vào/ra (không có realizedPnl từ sàn)
3. **Futures trading**: Ưu tiên lấy từ position API, nếu không có thì tính thủ công

## Kiểm Tra PnL

### Xem PnL Trong Orders Page

1. Mở trang **Orders**
2. Tìm cột **PnL**
3. PnL sẽ hiển thị:
   - **Màu xanh**: Lãi (PnL > 0)
   - **Màu đỏ**: Lỗ (PnL < 0)
   - **-**: Chưa có PnL (lệnh chưa đóng)

### Xem PnL Qua API

```bash
GET /api/orders/history
Authorization: Bearer YOUR_TOKEN
```

Response sẽ có:
```json
[
  {
    "id": 123,
    "symbol": "BTCUSDT",
    "side": "buy",
    "status": "closed",
    "pnl": 150.50,        // ✅ PnL từ sàn
    "pnl_percent": 3.01,  // ✅ PnL phần trăm
    ...
  }
]
```

## Tóm Tắt

✅ **PnL được lấy từ sàn** khi đóng lệnh  
✅ **Lưu vào database** để xem nhanh  
✅ **Hỗ trợ cả Spot và Futures**  
✅ **Tự động cập nhật** bot status với tổng PnL  

