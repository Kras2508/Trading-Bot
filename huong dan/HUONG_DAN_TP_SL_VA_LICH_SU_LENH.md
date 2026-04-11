# Hướng Dẫn TP/SL và Lịch Sử Lệnh

## 1. TP/SL (Take Profit / Stop Loss)

### ✅ Lệnh Có Tự Động Đặt TP/SL

**CÓ**, khi đặt lệnh thành công, hệ thống sẽ **tự động tính toán và lưu TP/SL** dựa trên cấu hình bot config.

### Cách Hoạt Động

1. **Khi đặt lệnh thành công**, hệ thống sẽ:
   - Tính toán `stop_loss_price` dựa trên `config.stop_loss_percent`
   - Tính toán `take_profit_price` dựa trên `config.take_profit_percent`
   - Lưu vào database trong bảng `orders`
   - Trả về trong response của API

### Ví Dụ Response Khi Đặt Lệnh Thành Công

```json
{
  "status": "success",
  "order_id": 123,
  "symbol": "BTCUSDT",
  "side": "buy",
  "order_type": "market",
  "amount": 100.0,
  "price": 50000.0,
  "filled_price": 50001.5,
  "stop_loss": 48000.0,      // ✅ Tự động tính từ config
  "take_profit": 52000.0,    // ✅ Tự động tính từ config
  "order_status": "filled"
}
```

### Cấu Hình TP/SL Trong Bot Config

TP/SL được cấu hình trong **Bot Config**:
- `stop_loss_percent`: Phần trăm stop loss (VD: 4.0 = 4%)
- `take_profit_percent`: Phần trăm take profit (VD: 4.0 = 4%)

**Ví dụ:**
- Entry price: 50000 USDT
- Stop loss: 4% → 48000 USDT
- Take profit: 4% → 52000 USDT

---

## 2. Lấy Lịch Sử Lệnh Đã Hoàn Thành

### API Endpoint

#### Cách 1: Lấy Tất Cả Lệnh Đã Hoàn Thành (KHUYẾN NGHỊ)

```
GET /api/orders/completed
```

**Query Parameters:**
- `bot_config_id` (tùy chọn): Lọc theo bot config ID
- `symbol` (tùy chọn): Lọc theo symbol
- `side` (tùy chọn): Lọc theo side (buy/sell)
- `start_date` (tùy chọn): Ngày bắt đầu (ISO format)
- `end_date` (tùy chọn): Ngày kết thúc (ISO format)
- `limit` (mặc định: 100): Số lượng lệnh trả về (1-1000)
- `offset` (mặc định: 0): Số lượng bỏ qua (pagination)

**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Ví Dụ Request:**
```bash
GET /api/orders/completed?limit=50&bot_config_id=1
```

**Response:**
```json
[
  {
    "id": 123,
    "bot_config_id": 1,
    "symbol": "BTCUSDT",
    "side": "buy",
    "order_type": "market",
    "amount": 100.0,
    "price": 50000.0,
    "filled_price": 50001.5,
    "status": "filled",
    "stop_loss_price": 48000.0,      // ✅ TP/SL
    "take_profit_price": 52000.0,     // ✅ TP/SL
    "pnl": 150.0,
    "pnl_percent": 0.3,
    "created_at": "2024-01-15T10:30:00Z",
    "closed_at": null
  },
  {
    "id": 122,
    "bot_config_id": 1,
    "symbol": "ETHUSDT",
    "side": "sell",
    "order_type": "market",
    "amount": 50.0,
    "price": 3000.0,
    "filled_price": 2998.5,
    "status": "closed",
    "stop_loss_price": 3120.0,
    "take_profit_price": 2880.0,
    "pnl": -75.0,
    "pnl_percent": -0.5,
    "created_at": "2024-01-15T09:15:00Z",
    "closed_at": "2024-01-15T10:00:00Z"
  }
]
```

#### Cách 2: Lấy Lịch Sử Với Filter Status

```
GET /api/orders/history?status=filled
```

Hoặc lấy cả filled và closed:
```
GET /api/orders/history?status=filled,closed
```

**Lưu ý:** Endpoint `/history` hỗ trợ filter `status`, nhưng chỉ nhận 1 giá trị. Để lấy cả filled và closed, dùng endpoint `/completed`.

---

## 3. Các Trường Thông Tin Trong Response

### Thông Tin Cơ Bản
- `id`: ID lệnh
- `bot_config_id`: ID bot config
- `symbol`: Symbol giao dịch
- `side`: "buy" hoặc "sell"
- `order_type`: "market" hoặc "limit"
- `amount`: Số lượng
- `price`: Giá đặt lệnh
- `filled_price`: Giá đã khớp
- `status`: Trạng thái (filled, closed, pending, cancelled)

### Thông Tin TP/SL
- `stop_loss_price`: Giá stop loss
- `take_profit_price`: Giá take profit
- `tp_levels`: Danh sách các mức TP (nếu có nhiều TP)

### Thông Tin PnL
- `pnl`: Lợi nhuận/lỗ (số tiền)
- `pnl_percent`: Lợi nhuận/lỗ (phần trăm)

### Thông Tin Thời Gian
- `created_at`: Thời gian tạo lệnh
- `updated_at`: Thời gian cập nhật
- `closed_at`: Thời gian đóng lệnh (nếu đã đóng)

---

## 4. Ví Dụ Sử Dụng

### Lấy Tất Cả Lệnh Đã Hoàn Thành

```bash
curl -X GET "http://localhost:8000/api/orders/completed" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Lấy Lệnh Đã Hoàn Thành Của Một Bot Config

```bash
curl -X GET "http://localhost:8000/api/orders/completed?bot_config_id=1&limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Lấy Lệnh Đã Hoàn Thành Của Một Symbol

```bash
curl -X GET "http://localhost:8000/api/orders/completed?symbol=BTCUSDT" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Lấy Lệnh Đã Hoàn Thành Trong Khoảng Thời Gian

```bash
curl -X GET "http://localhost:8000/api/orders/completed?start_date=2024-01-01T00:00:00Z&end_date=2024-01-31T23:59:59Z" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Lấy Lệnh Đã Hoàn Thành Với Pagination

```bash
# Trang 1 (lệnh 1-50)
curl -X GET "http://localhost:8000/api/orders/completed?limit=50&offset=0" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Trang 2 (lệnh 51-100)
curl -X GET "http://localhost:8000/api/orders/completed?limit=50&offset=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 5. Sử Dụng Trong Frontend

### JavaScript/React

```javascript
// Lấy lệnh đã hoàn thành
const fetchCompletedOrders = async () => {
  try {
    const response = await axios.get('/api/orders/completed', {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      params: {
        limit: 50,
        bot_config_id: 1
      }
    })
    
    console.log('Lệnh đã hoàn thành:', response.data)
    
    // Hiển thị TP/SL
    response.data.forEach(order => {
      console.log(`Order ${order.id}:`)
      console.log(`  Stop Loss: ${order.stop_loss_price}`)
      console.log(`  Take Profit: ${order.take_profit_price}`)
      console.log(`  PnL: ${order.pnl} (${order.pnl_percent}%)`)
    })
  } catch (error) {
    console.error('Lỗi:', error)
  }
}
```

### Python

```python
import requests

def get_completed_orders(token, bot_config_id=None, limit=100):
    url = "http://localhost:8000/api/orders/completed"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"limit": limit}
    
    if bot_config_id:
        params["bot_config_id"] = bot_config_id
    
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# Sử dụng
token = "YOUR_TOKEN"
orders = get_completed_orders(token, bot_config_id=1, limit=50)

for order in orders:
    print(f"Order {order['id']}: {order['symbol']} {order['side']}")
    print(f"  Entry: {order['filled_price']}")
    print(f"  Stop Loss: {order['stop_loss_price']}")
    print(f"  Take Profit: {order['take_profit_price']}")
    print(f"  PnL: {order['pnl']} ({order['pnl_percent']}%)")
    print()
```

---

## 6. Tóm Tắt

### ✅ TP/SL
- **Tự động tính toán** khi đặt lệnh thành công
- **Lưu vào database** trong bảng `orders`
- **Trả về trong response** của API đặt lệnh
- Dựa trên `stop_loss_percent` và `take_profit_percent` trong bot config

### ✅ Lịch Sử Lệnh
- **Endpoint mới**: `/api/orders/completed` - Lấy chỉ lệnh đã hoàn thành
- **Endpoint cũ**: `/api/orders/history` - Lấy tất cả lệnh (có filter)
- **Hỗ trợ filter**: bot_config_id, symbol, side, date range
- **Hỗ trợ pagination**: limit, offset
- **Có đầy đủ thông tin**: TP/SL, PnL, timestamps

### 📝 Lưu Ý
- Lệnh đã hoàn thành = `status = "filled"` hoặc `status = "closed"`
- TP/SL được tính dựa trên `filled_price` (giá đã khớp)
- PnL được tính tự động và cập nhật khi lệnh đóng

