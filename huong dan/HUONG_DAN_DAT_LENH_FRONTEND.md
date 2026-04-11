# Hướng dẫn Đặt Lệnh trên Frontend

## Cách Đặt Lệnh

### Bước 1: Đăng nhập
1. Mở trình duyệt: **http://localhost:3000**
2. Đăng nhập với:
   - Username: `admin`
   - Password: `admin123`

### Bước 2: Vào trang Đặt Lệnh
1. Click vào menu **"Đặt Lệnh"** ở sidebar bên trái
2. Hoặc truy cập trực tiếp: **http://localhost:3000/trading**

### Bước 3: Chọn Bot Config
1. Ở cột bên trái, chọn **Bot Config** từ dropdown
2. Chọn config có API key đã được thêm (ví dụ: "NEAR Spot Bot")
3. Thông tin config sẽ hiển thị:
   - Symbol
   - Amount mặc định
   - SL/TP percentages

### Bước 4: Điền thông tin lệnh
1. **Side**: Chọn Buy (Mua) hoặc Sell (Bán)
2. **Order Type**: 
   - **Market**: Giá thị trường (khuyến nghị)
   - **Limit**: Giá chỉ định (cần nhập giá)
3. **Amount**: Số lượng (để trống sẽ dùng amount từ config)
4. **Price**: Chỉ cần khi chọn Limit order

### Bước 5: Đặt lệnh
1. Kiểm tra lại thông tin
2. Click nút **"Đặt Lệnh"**
3. Đợi kết quả (thành công hoặc lỗi)

## Ví dụ: Mua 5 NEAR

1. Chọn Bot Config: "NEAR Spot Bot - NEAR/USDT"
2. Side: **Buy**
3. Order Type: **Market**
4. Amount: **5**
5. Click **"Đặt Lệnh"**

## Ví dụ: Bán NEAR

1. Chọn Bot Config: "NEAR Spot Bot - NEAR/USDT"
2. Side: **Sell**
3. Order Type: **Market**
4. Amount: **5** (hoặc để trống để bán hết)
5. Click **"Đặt Lệnh"**

## Lưu ý

⚠️ **Cảnh báo**: Đây là lệnh THẬT trên Binance!

- Kiểm tra số dư trước khi đặt lệnh
- Đảm bảo bot config đã có API key/secret
- Market order sẽ fill ngay lập tức
- Limit order cần giá đạt mức chỉ định mới fill

## Xem kết quả

Sau khi đặt lệnh thành công:
1. Vào trang **"Orders"** để xem lịch sử lệnh
2. Hoặc vào **"Monitoring"** để xem trạng thái bot

## Troubleshooting

### Lỗi: "Bot config missing API credentials"
- Bot config chưa có API key/secret
- Cần thêm API key vào config trước

### Lỗi: "Insufficient balance"
- Không đủ số dư
- Kiểm tra số dư trên Binance

### Lỗi: "Filter failure: NOTIONAL"
- Giá trị lệnh quá nhỏ
- Binance yêu cầu minimum 5 USDT cho spot trading

