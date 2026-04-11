# Giải Thích Status Lệnh: "Đã Khớp" vs "Đã Đóng"

## Sự Khác Biệt

### 🔵 **"Đã Khớp" (filled)**

**Ý nghĩa**: Lệnh đã được khớp thành công trên sàn, **nhưng position vẫn đang mở**.

**Ví dụ:**
- Đặt lệnh **MUA** BTC @ 50000 USDT
- Lệnh khớp thành công → Status = **"filled"**
- Bạn **đang giữ** BTC (position đang mở)
- Có thể lỗ/lãi **unrealized** (chưa thực hiện)

**Khi nào có status "filled":**
- ✅ Lệnh mua đã khớp → Đang giữ coin
- ✅ Lệnh bán đã khớp → Đã bán coin (nếu là đóng position thì sẽ thành "closed")

---

### 🟢 **"Đã Đóng" (closed)**

**Ý nghĩa**: Position đã được **đóng hoàn toàn**, không còn giữ coin nữa.

**Ví dụ:**
- Đã mua BTC @ 50000 (status = "filled")
- Đóng position bằng cách bán BTC @ 50100
- Status = **"closed"**
- Không còn giữ BTC nữa
- PnL đã được **realized** (thực hiện)

**Khi nào có status "closed":**
- ✅ Đã đóng position bằng API `/close-order`
- ✅ Đã bán hết coin (spot trading)
- ✅ Đã đóng position (futures trading)

---

## So Sánh Chi Tiết

| Tiêu Chí | "Đã Khớp" (filled) | "Đã Đóng" (closed) |
|----------|-------------------|-------------------|
| **Lệnh đã khớp?** | ✅ Có | ✅ Có |
| **Position đang mở?** | ✅ Có | ❌ Không |
| **Còn giữ coin?** | ✅ Có | ❌ Không |
| **PnL** | Unrealized (chưa thực hiện) | Realized (đã thực hiện) |
| **Có thể đóng?** | ✅ Có (bằng `/close-order`) | ❌ Không (đã đóng rồi) |
| **Có PnL trong DB?** | ⚠️ Có thể = 0 | ✅ Có (từ sàn) |

---

## Ví Dụ Thực Tế

### Scenario 1: Spot Trading

1. **Bước 1**: Đặt lệnh MUA BTC
   ```
   Order ID: 1
   Side: buy
   Price: 50000 USDT
   Status: pending → filled ✅
   ```
   → Bạn **đang giữ** 1 BTC

2. **Bước 2**: Đóng position (bán BTC)
   ```
   Order ID: 1
   Status: filled → closed ✅
   Close price: 50100 USDT
   PnL: +100 USDT (đã thực hiện)
   ```
   → Không còn giữ BTC nữa

---

### Scenario 2: Futures Trading

1. **Bước 1**: Mở long position
   ```
   Order ID: 1
   Side: buy
   Price: 50000 USDT
   Leverage: 10x
   Status: filled ✅
   ```
   → Position đang mở, unrealized PnL thay đổi theo giá

2. **Bước 2**: Đóng position
   ```
   Order ID: 1
   Status: closed ✅
   Close price: 50100 USDT
   PnL: +1000 USDT (realized, với 10x leverage)
   ```
   → Position đã đóng

---

## Trong Hệ Thống

### Khi Đặt Lệnh Thành Công

```python
# Lệnh khớp → status = "filled"
order.status = "filled"
order.filled_price = 50000.0
# Position đang mở
```

### Khi Đóng Lệnh

```python
# Đóng position → status = "closed"
order.status = "closed"
order.closed_at = datetime.now()
order.pnl = 100.0  # PnL từ sàn
# Position đã đóng
```

---

## Lưu Ý

### ⚠️ Quan Trọng

1. **"filled"** không có nghĩa là đã đóng position
   - Chỉ có nghĩa là lệnh đã khớp
   - Position vẫn đang mở

2. **"closed"** mới là đã đóng position
   - Position đã được đóng hoàn toàn
   - PnL đã được thực hiện

3. **PnL**:
   - **filled**: Unrealized PnL (chưa thực hiện, thay đổi theo giá)
   - **closed**: Realized PnL (đã thực hiện, cố định)

---

## Tóm Tắt

| Status | Ý Nghĩa | Position | PnL |
|--------|---------|----------|-----|
| **pending** | Đang chờ khớp | Chưa có | - |
| **filled** | Đã khớp | ✅ Đang mở | Unrealized |
| **closed** | Đã đóng | ❌ Đã đóng | Realized |
| **cancelled** | Đã hủy | Không có | - |

**Kết luận**: 
- **"filled"** = Lệnh đã khớp, position đang mở
- **"closed"** = Position đã đóng hoàn toàn

