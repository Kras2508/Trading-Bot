# Hướng Dẫn Đặt Lệnh Trading

## Mục Lục
1. [Đặt Lệnh Trên Web (Frontend)](#1-đặt-lệnh-trên-web-frontend)
2. [Đặt Lệnh Qua API (Backend)](#2-đặt-lệnh-qua-api-backend)

---

## 1. Đặt Lệnh Trên Web (Frontend)

### Bước 1: Đăng Nhập

1. Mở trình duyệt và truy cập: `http://localhost:3000`
2. Đăng nhập với thông tin:
   - **Username**: `admin`
   - **Password**: `admin123` (hoặc password bạn đã tạo)

### Bước 2: Vào Trang Đặt Lệnh

1. Click vào menu **"Đặt Lệnh"** ở sidebar bên trái
2. Hoặc truy cập trực tiếp: `http://localhost:3000/trading`

### Bước 3: Chọn Bot Config

1. Trong phần **"Chọn Bot Config"**, chọn bot config từ dropdown
   - Format hiển thị: `BINANCE - Tên Bot` (ví dụ: `BINANCE - Thanhdt`)
   - Bot config phải có:
     - ✅ API Key và Secret Key đã được thêm
     - ✅ Trạng thái Active
     - ✅ Bot không bị Pause

2. Sau khi chọn, thông tin config sẽ hiển thị:
   - **Sàn**: Binance, Bitget, etc.
   - **Symbol mặc định**: NEAR/USDT
   - **Amount mặc định**: 5
   - **SL/TP**: Stop Loss và Take Profit percentages

### Bước 4: Điền Thông Tin Lệnh

#### 4.1. Side (Hướng lệnh)
- **Buy (Mua)**: Mua coin/token
- **Sell (Bán)**: Bán coin/token

#### 4.2. Symbol (Cặp giao dịch)
- **Tự động điền**: Symbol từ config sẽ tự động điền vào
- **Tìm kiếm**: Gõ để tìm kiếm symbol
  - Nếu config có API key: Tự động tải danh sách symbols từ exchange
  - Nếu không có API key: Dùng danh sách symbols phổ biến
- **Override**: Có thể nhập symbol khác để override symbol từ config
  - Ví dụ: Config có `BTC/USDT`, nhưng muốn đặt lệnh `ETH/USDT`
- **Để trống**: Sẽ dùng symbol từ config

#### 4.3. Order Type (Loại lệnh)
- **Market (Giá thị trường)**: Đặt lệnh ngay với giá hiện tại
  - Không cần nhập giá
  - Được fill ngay lập tức
- **Limit (Giá chỉ định)**: Đặt lệnh với giá cụ thể
  - Cần nhập giá trong trường **Price**
  - Chờ giá đạt mức chỉ định mới fill

#### 4.4. Amount (Số lượng)
- Nhập số lượng coin/token muốn mua/bán
- **Để trống**: Sẽ dùng amount từ config
- Ví dụ: `5` (5 NEAR), `0.1` (0.1 BTC)

#### 4.5. Price (Giá - Chỉ cho Limit Order)
- Chỉ hiển thị khi chọn **Limit Order**
- Nhập giá muốn đặt lệnh
- Ví dụ: `3.5` (3.5 USDT cho 1 NEAR)

### Bước 5: Đặt Lệnh

1. Kiểm tra lại thông tin:
   - ✅ Bot config đã chọn
   - ✅ Side (Buy/Sell)
   - ✅ Symbol
   - ✅ Order Type
   - ✅ Amount
   - ✅ Price (nếu là Limit)

2. Click nút **"Đặt Lệnh"**

3. Chờ kết quả:
   - **Thành công**: Hiển thị thông báo xanh với Order ID
   - **Lỗi**: Hiển thị thông báo đỏ với chi tiết lỗi

### Bước 6: Kiểm Tra Lệnh

1. Vào trang **"Orders"** để xem lịch sử lệnh
2. Hoặc vào **"Monitoring"** để xem trạng thái bot

---

## 2. Đặt Lệnh Qua API (Backend)

### Yêu Cầu

- Backend đang chạy tại: `http://127.0.0.1:8000`
- Có JWT token (lấy từ API login)
- Bot config đã được tạo và có API credentials

### Bước 1: Lấy JWT Token

#### 1.1. Đăng Nhập

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 1.2. Lưu Token

Lưu `access_token` để dùng cho các request tiếp theo.

### Bước 2: Lấy Danh Sách Bot Configs

```bash
curl -X GET "http://127.0.0.1:8000/api/config/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Thanhdt",
    "symbol": "NEAR/USDT",
    "exchange": "binance",
    "amount": 5.0,
    "trading_mode": "spot",
    "is_active": true,
    ...
  }
]
```

Lưu `id` của bot config muốn dùng.

### Bước 3: Đặt Lệnh

#### 3.1. Market Order (Lệnh thị trường)

```bash
curl -X POST "http://127.0.0.1:8000/api/trading/place-order" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_config_id": 1,
    "side": "buy",
    "symbol": "NEAR/USDT",
    "amount": 5,
    "order_type": "market"
  }'
```

**Request Body:**
- `bot_config_id` (required): ID của bot config
- `side` (required): `"buy"` hoặc `"sell"`
- `symbol` (optional): Symbol muốn trade. Nếu không có, dùng symbol từ config
- `amount` (optional): Số lượng. Nếu không có, dùng amount từ config
- `order_type` (required): `"market"` hoặc `"limit"`

**Response (Thành công):**
```json
{
  "status": "success",
  "order_id": 123,
  "exchange_order_id": "12345678",
  "symbol": "NEAR/USDT",
  "side": "buy",
  "order_type": "market",
  "amount": 5.0,
  "price": 3.45,
  "filled_price": 3.45,
  "stop_loss": 3.38,
  "take_profit": 3.62,
  "order_status": "filled"
}
```

#### 3.2. Limit Order (Lệnh giới hạn)

```bash
curl -X POST "http://127.0.0.1:8000/api/trading/place-order" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_config_id": 1,
    "side": "buy",
    "symbol": "NEAR/USDT",
    "amount": 5,
    "price": 3.4,
    "order_type": "limit"
  }'
```

**Request Body:**
- Tất cả như Market Order
- `price` (required cho limit): Giá muốn đặt lệnh

**Response:**
```json
{
  "status": "success",
  "order_id": 124,
  "exchange_order_id": "12345679",
  "symbol": "NEAR/USDT",
  "side": "buy",
  "order_type": "limit",
  "amount": 5.0,
  "price": 3.4,
  "filled_price": null,
  "stop_loss": 3.33,
  "take_profit": 3.57,
  "order_status": "pending"
}
```

### Bước 4: Kiểm Tra Trạng Thái Lệnh

```bash
curl -X GET "http://127.0.0.1:8000/api/trading/check-order/123" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "order_id": 123,
  "exchange_order_id": "12345678",
  "status": "filled",
  "filled": 5.0,
  "remaining": 0.0,
  "order_data": {...}
}
```

### Bước 5: Xem Lịch Sử Lệnh

```bash
curl -X GET "http://127.0.0.1:8000/api/orders/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Ví Dụ Thực Tế

### Ví Dụ 1: Mua 5 NEAR/USDT với giá thị trường

**Trên Web:**
1. Chọn Bot Config: `BINANCE - Thanhdt`
2. Side: `Buy (Mua)`
3. Symbol: `NEAR/USDT` (hoặc để trống)
4. Order Type: `Market (Giá thị trường)`
5. Amount: `5`
6. Click "Đặt Lệnh"

**Qua API:**
```bash
curl -X POST "http://127.0.0.1:8000/api/trading/place-order" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_config_id": 1,
    "side": "buy",
    "amount": 5,
    "order_type": "market"
  }'
```

### Ví Dụ 2: Bán 3 BTC/USDT với giá 50000 USDT

**Trên Web:**
1. Chọn Bot Config có symbol BTC/USDT
2. Side: `Sell (Bán)`
3. Symbol: `BTC/USDT`
4. Order Type: `Limit (Giá chỉ định)`
5. Amount: `3`
6. Price: `50000`
7. Click "Đặt Lệnh"

**Qua API:**
```bash
curl -X POST "http://127.0.0.1:8000/api/trading/place-order" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_config_id": 2,
    "side": "sell",
    "symbol": "BTC/USDT",
    "amount": 3,
    "price": 50000,
    "order_type": "limit"
  }'
```

### Ví Dụ 3: Override Symbol (Dùng symbol khác với config)

**Trên Web:**
1. Chọn Bot Config có symbol `BTC/USDT`
2. Symbol: Nhập `ETH/USDT` (override)
3. Các thông tin khác giữ nguyên
4. Click "Đặt Lệnh"

**Qua API:**
```bash
curl -X POST "http://127.0.0.1:8000/api/trading/place-order" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bot_config_id": 1,
    "side": "buy",
    "symbol": "ETH/USDT",
    "amount": 0.1,
    "order_type": "market"
  }'
```

---

## Lưu Ý Quan Trọng

### ⚠️ Cảnh Báo

1. **Đây là lệnh THẬT**: Lệnh sẽ được đặt trực tiếp trên exchange (Binance, Bitget, etc.)
2. **Kiểm tra kỹ**: Đảm bảo thông tin đúng trước khi đặt lệnh
3. **Số dư**: Đảm bảo tài khoản có đủ số dư
4. **API Key**: Bot config phải có API Key và Secret Key hợp lệ
5. **Quyền API**: API Key phải có quyền Trading (không cần Withdraw)

### ✅ Yêu Cầu

- Bot config phải **Active** (`is_active: true`)
- Bot không được **Pause** (`is_paused: false`)
- Bot config phải có **API credentials**
- JWT token phải **còn hiệu lực** (24 giờ)

### ❌ Lỗi Thường Gặp

1. **"Bot config missing API credentials"**
   - Giải pháp: Thêm API Key và Secret Key vào bot config

2. **"Account has insufficient balance"**
   - Giải pháp: Nạp thêm tiền vào tài khoản exchange

3. **"Filter failure: NOTIONAL"**
   - Giải pháp: Tăng amount (tối thiểu 5 USDT cho Binance)

4. **"401 Unauthorized"**
   - Giải pháp: Đăng nhập lại để lấy token mới

5. **"Bot is paused"**
   - Giải pháp: Resume bot từ trang Monitoring

---

## Swagger UI (API Documentation)

Truy cập: `http://127.0.0.1:8000/docs`

- Xem tất cả API endpoints
- Test API trực tiếp trên browser
- Xem request/response examples

---

## Hỗ Trợ

Nếu gặp vấn đề, kiểm tra:
1. Backend đang chạy: `http://127.0.0.1:8000`
2. Frontend đang chạy: `http://localhost:3000`
3. Database kết nối thành công
4. API Key/Secret Key hợp lệ
5. Logs trong console/terminal

