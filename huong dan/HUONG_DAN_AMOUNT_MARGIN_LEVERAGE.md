# Hướng Dẫn: Amount, Margin và Leverage (Đòn Bẫy)

## 📚 Khái Niệm Cơ Bản

### 1. **Amount (Số Lượng)**
- **Định nghĩa**: Số lượng coin/token bạn muốn mua hoặc bán
- **Đơn vị**: Coin (ví dụ: 0.1 BTC, 100 NEAR, 50 ETH)
- **Ví dụ**: `amount = 0.1` nghĩa là mua/bán 0.1 BTC

### 2. **Position Size (Kích Thước Vị Thế)**
- **Định nghĩa**: Giá trị USD/USDT của position
- **Công thức**: `Position Size = Amount × Entry Price`
- **Ví dụ**: 
  - Amount = 0.1 BTC
  - Entry Price = $50,000
  - Position Size = 0.1 × $50,000 = **$5,000**

### 3. **Leverage (Đòn Bẫy)**
- **Định nghĩa**: Hệ số nhân để tăng kích thước position mà không cần nhiều vốn
- **Spot Trading**: Leverage = 1x (không có đòn bẫy)
- **Futures Trading**: Leverage = 10x, 20x, 50x, 100x, ...
- **Ví dụ**: Leverage 10x nghĩa là bạn có thể mở position gấp 10 lần số tiền bạn có

### 4. **Margin (Ký Quỹ)**
- **Định nghĩa**: Số tiền thực tế cần có trong tài khoản để mở position
- **Công thức**: `Margin = Position Size / Leverage`
- **Ví dụ**:
  - Position Size = $5,000
  - Leverage = 10x
  - Margin = $5,000 / 10 = **$500**

---

## 📊 So Sánh Spot vs Futures

### **Spot Trading (Giao Ngay)**
```
Amount = 0.1 BTC
Entry Price = $50,000
Position Size = 0.1 × $50,000 = $5,000
Leverage = 1x (không có đòn bẫy)
Margin Required = $5,000 / 1 = $5,000
```

**Kết luận**: Cần **$5,000** trong tài khoản để mua 0.1 BTC

### **Futures Trading (Hợp Đồng Tương Lai)**
```
Amount = 0.1 BTC
Entry Price = $50,000
Position Size = 0.1 × $50,000 = $5,000
Leverage = 10x
Margin Required = $5,000 / 10 = $500
```

**Kết luận**: Chỉ cần **$500** trong tài khoản để mở position tương đương 0.1 BTC

---

## 💰 Công Thức Tính Toán

### 1. **Tính Margin từ Amount và Leverage**

```
Margin = (Amount × Entry Price) / Leverage
```

**Ví dụ:**
- Amount = 0.1 BTC
- Entry Price = $50,000
- Leverage = 20x
- **Margin = (0.1 × $50,000) / 20 = $250**

### 2. **Tính Amount từ Margin và Leverage**

```
Amount = (Margin × Leverage) / Entry Price
```

**Ví dụ:**
- Margin = $500
- Leverage = 10x
- Entry Price = $50,000
- **Amount = ($500 × 10) / $50,000 = 0.1 BTC**

### 3. **Tính Position Size**

```
Position Size = Amount × Entry Price
```

**Ví dụ:**
- Amount = 0.1 BTC
- Entry Price = $50,000
- **Position Size = 0.1 × $50,000 = $5,000**

### 4. **Tính PnL (Profit and Loss)**

#### **Spot Trading:**
```
PnL = (Exit Price - Entry Price) × Amount
```

**Ví dụ:**
- Entry Price = $50,000
- Exit Price = $51,000
- Amount = 0.1 BTC
- **PnL = ($51,000 - $50,000) × 0.1 = $100**

#### **Futures Trading:**
```
PnL = (Exit Price - Entry Price) × Amount × Leverage
```

**Ví dụ:**
- Entry Price = $50,000
- Exit Price = $51,000
- Amount = 0.1 BTC
- Leverage = 10x
- **PnL = ($51,000 - $50,000) × 0.1 × 10 = $1,000**

### 5. **Tính ROI (Return on Investment)**

#### **Spot Trading:**
```
ROI = (PnL / Position Size) × 100
```

**Ví dụ:**
- PnL = $100
- Position Size = $5,000
- **ROI = ($100 / $5,000) × 100 = 2%**

#### **Futures Trading:**
```
ROI = (PnL / Margin) × 100
```

**Ví dụ:**
- PnL = $1,000
- Margin = $500
- **ROI = ($1,000 / $500) × 100 = 200%**

---

## 📈 Ví Dụ Thực Tế

### **Ví Dụ 1: Spot Trading**

**Cấu hình:**
- Symbol: BTC/USDT
- Amount: 0.1 BTC
- Entry Price: $50,000
- Trading Mode: Spot
- Leverage: 1x (không có)

**Tính toán:**
- Position Size = 0.1 × $50,000 = **$5,000**
- Margin Required = $5,000 / 1 = **$5,000**
- Cần có **$5,000** trong tài khoản

**Kết quả khi giá tăng 2%:**
- Exit Price = $51,000
- PnL = ($51,000 - $50,000) × 0.1 = **$100**
- ROI = ($100 / $5,000) × 100 = **2%**

---

### **Ví Dụ 2: Futures Trading với Leverage 10x**

**Cấu hình:**
- Symbol: BTC/USDT
- Amount: 0.1 BTC
- Entry Price: $50,000
- Trading Mode: Futures
- Leverage: 10x

**Tính toán:**
- Position Size = 0.1 × $50,000 = **$5,000**
- Margin Required = $5,000 / 10 = **$500**
- Chỉ cần có **$500** trong tài khoản

**Kết quả khi giá tăng 2%:**
- Exit Price = $51,000
- PnL = ($51,000 - $50,000) × 0.1 × 10 = **$1,000**
- ROI = ($1,000 / $500) × 100 = **200%**

**So sánh:**
- Spot: Lãi $100 (2%)
- Futures 10x: Lãi $1,000 (200%) - **gấp 10 lần!**

---

### **Ví Dụ 3: Futures Trading với Leverage 20x**

**Cấu hình:**
- Symbol: BTC/USDT
- Amount: 0.1 BTC
- Entry Price: $50,000
- Trading Mode: Futures
- Leverage: 20x

**Tính toán:**
- Position Size = 0.1 × $50,000 = **$5,000**
- Margin Required = $5,000 / 20 = **$250**
- Chỉ cần có **$250** trong tài khoản

**Kết quả khi giá tăng 2%:**
- Exit Price = $51,000
- PnL = ($51,000 - $50,000) × 0.1 × 20 = **$2,000**
- ROI = ($2,000 / $250) × 100 = **800%**

**⚠️ Cảnh báo**: Leverage cao = Lãi cao NHƯNG cũng = Lỗ cao!

---

## ⚠️ Rủi Ro Khi Dùng Leverage

### **Ví Dụ: Leverage 10x, Giá Giảm 10%**

**Cấu hình:**
- Amount: 0.1 BTC
- Entry Price: $50,000
- Leverage: 10x
- Margin: $500

**Kết quả:**
- Exit Price = $45,000 (giảm 10%)
- PnL = ($45,000 - $50,000) × 0.1 × 10 = **-$5,000**
- ROI = (-$5,000 / $500) × 100 = **-1000%**

**Kết luận**: Mất hết margin ($500) và còn nợ thêm $4,500! ⚠️

### **Liquidation (Thanh Lý)**
- Khi giá giảm quá nhiều, sàn sẽ tự động đóng position (liquidation)
- Với leverage 10x, chỉ cần giá giảm ~10% là có thể bị liquidation
- Với leverage 20x, chỉ cần giá giảm ~5% là có thể bị liquidation

---

## 🎯 Trong Hệ Thống Trading Bot

### **Cấu Hình Bot Config**

```json
{
  "name": "BTC Futures 10x",
  "symbol": "BTCUSDT",
  "amount": 0.1,           // Số lượng BTC
  "leverage": 10,         // Đòn bẫy 10x
  "trading_mode": "futures",
  "stop_loss_percent": 4.0,
  "take_profit_percent": 4.0
}
```

**Tính toán:**
- Giả sử Entry Price = $50,000
- Position Size = 0.1 × $50,000 = **$5,000**
- Margin Required = $5,000 / 10 = **$500**
- Stop Loss = $50,000 × (1 - 4%) = **$48,000**
- Take Profit = $50,000 × (1 + 4%) = **$52,000**

**Kết quả:**
- Nếu giá đạt TP ($52,000):
  - PnL = ($52,000 - $50,000) × 0.1 × 10 = **$2,000**
  - ROI = ($2,000 / $500) × 100 = **400%**
  
- Nếu giá đạt SL ($48,000):
  - PnL = ($48,000 - $50,000) × 0.1 × 10 = **-$2,000**
  - ROI = (-$2,000 / $500) × 100 = **-400%**

---

## 📝 Tóm Tắt

### **Công Thức Chính:**

1. **Position Size** = Amount × Entry Price
2. **Margin** = Position Size / Leverage
3. **PnL (Spot)** = (Exit - Entry) × Amount
4. **PnL (Futures)** = (Exit - Entry) × Amount × Leverage
5. **ROI (Spot)** = (PnL / Position Size) × 100
6. **ROI (Futures)** = (PnL / Margin) × 100

### **Lưu Ý:**

✅ **Leverage cao** = Lãi cao NHƯNG rủi ro cao  
✅ **Margin** là số tiền thực tế cần có  
✅ **Amount** là số lượng coin/token  
✅ **Position Size** là giá trị USD của position  
⚠️ **Cẩn thận với leverage cao** - có thể mất hết vốn!

---

## 🔗 Liên Kết

- [Hướng Dẫn PnL Từ Sàn](./HUONG_DAN_PNL_TU_SAN.md)
- [Hướng Dẫn TP/SL](./HUONG_DAN_TP_SL_VA_LICH_SU_LENH.md)

