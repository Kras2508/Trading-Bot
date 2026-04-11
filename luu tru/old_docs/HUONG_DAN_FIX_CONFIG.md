# Đã Sửa Lỗi "Không thể tải danh sách configs"

## Vấn đề

SQL Server yêu cầu **ORDER BY** khi sử dụng **OFFSET/LIMIT**.

Lỗi: `MSSQL requires an order_by when using an OFFSET or a non-simple LIMIT clause`

## Đã sửa

✅ Thêm `.order_by(BotConfig.id)` vào query trong `app/routers/config.py`

## Kết quả

API `/api/config/` đã hoạt động bình thường!

## Test lại

1. **Refresh frontend** (F5)
2. Vào trang **"Đặt Lệnh"**
3. Dropdown config sẽ load được danh sách

## Configs có sẵn

- **ID: 1** - Test Bot 095818 (BTC/USDT)
- **ID: 2** - NEAR Spot Bot (NEAR/USDT)

Bạn có thể đặt lệnh ngay!

