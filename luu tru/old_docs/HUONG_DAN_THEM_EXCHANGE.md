# Hướng Dẫn Thêm Exchange và API Credentials

## Tính năng mới

✅ **Chọn sàn giao dịch**: Binance, Bitget, OKX, Bybit, Gate.io, KuCoin, Huobi, Coinbase Pro, Kraken, Bitfinex

✅ **Nhập API Key và Secret Key**: Tự động mã hóa và lưu an toàn

✅ **IP Whitelist**: Nhập danh sách IP được phép cho API

## Cách sử dụng

### 1. Tạo Bot Config mới

1. Vào trang **Bot Configs**
2. Click **"Tạo Config Mới"**
3. Điền thông tin:
   - **Tên Bot**: Tên mô tả
   - **Symbol**: Ví dụ `BTC/USDT`, `NEAR/USDT`
   - **Sàn Giao Dịch**: Chọn sàn (Binance, Bitget, ...)
   - **Amount**: Số tiền đặt lệnh
   - **Stop Loss %**: Phần trăm dừng lỗ
   - **Take Profit %**: Phần trăm chốt lời
   - **Trading Mode**: Spot hoặc Futures

### 2. Thêm API Credentials (Tùy chọn)

Trong form tạo config, có phần **"API Credentials"**:

- **API Key**: Nhập API Key từ sàn giao dịch
- **Secret Key**: Nhập Secret Key từ sàn giao dịch
- **IP Whitelist**: Nhập IP được phép (phân cách bằng dấu phẩy)

**Ví dụ IP Whitelist:**
```
1.2.3.4, 5.6.7.8, 192.168.1.100
```

### 3. Lấy API Key từ các sàn

#### Binance:
1. Đăng nhập Binance
2. Vào **API Management**
3. Tạo API Key mới
4. Copy **API Key** và **Secret Key**
5. Thiết lập IP whitelist trên Binance (nếu cần)

#### Bitget:
1. Đăng nhập Bitget
2. Vào **API Management** > **Create API**
3. Copy **API Key** và **Secret Key**
4. Thiết lập IP whitelist trên Bitget (nếu cần)

### 4. Lưu ý

- **API Key và Secret Key** sẽ được **mã hóa** trước khi lưu vào database
- **IP Whitelist** chỉ để tham khảo, bạn vẫn cần thiết lập trên sàn giao dịch
- Có thể tạo config mà không cần API credentials (để thêm sau)

## Các sàn được hỗ trợ

- ✅ Binance
- ✅ Bitget
- ✅ OKX (OKEx)
- ✅ Bybit
- ✅ Gate.io
- ✅ KuCoin
- ✅ Huobi
- ✅ Coinbase Pro
- ✅ Kraken
- ✅ Bitfinex

*Hệ thống sử dụng CCXT library, hỗ trợ hơn 100 sàn giao dịch. Nếu sàn bạn cần không có trong danh sách, có thể thêm vào form.*

