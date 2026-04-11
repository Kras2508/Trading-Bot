# Hướng Dẫn Cài Đặt Ngrok Authtoken

## Lỗi: ERR_NGROK_4018

Ngrok yêu cầu đăng ký tài khoản và cài đặt authtoken để sử dụng.

---

## Cách 1: Dùng Script Tự Động (Khuyến Nghị)

Chạy file:
```bash
CAI_DAT_NGROK_AUTHTOKEN.bat
```

Script sẽ hướng dẫn từng bước.

---

## Cách 2: Làm Thủ Công

### Bước 1: Đăng Ký Tài Khoản

1. Truy cập: **https://dashboard.ngrok.com/signup**
2. Đăng ký tài khoản (miễn phí)
3. Xác thực email

### Bước 2: Lấy Authtoken

1. Đăng nhập: **https://dashboard.ngrok.com**
2. Vào: **https://dashboard.ngrok.com/get-started/your-authtoken**
3. Copy authtoken (chuỗi ký tự dài)

### Bước 3: Cài Đặt Authtoken

Mở terminal và chạy:

```bash
ngrok config add-authtoken YOUR_AUTHTOKEN
```

**Ví dụ:**
```bash
C:\ngrok\ngrok.exe config add-authtoken 2abc123def456ghi789jkl012mno345pqr678
```

---

## Kiểm Tra

Sau khi cài đặt, chạy:

```bash
ngrok version
```

Nếu hiển thị version → Đã cài đặt thành công!

---

## Sau Khi Cài Đặt

Chạy ngrok để expose frontend:

```bash
CHAY_NGROK_NHANH.bat
```

Hoặc trực tiếp:

```bash
C:\ngrok\ngrok.exe http 3000
```

---

## Lưu Ý

- ✅ Tài khoản ngrok **miễn phí**
- ✅ Authtoken chỉ cần cài **1 lần**
- ✅ Authtoken được lưu tự động
- ⚠️ Không chia sẻ authtoken với người khác

---

## Troubleshooting

### Lỗi: "ngrok: command not found"

**Giải pháp:**
- Dùng đường dẫn đầy đủ: `C:\ngrok\ngrok.exe`
- Hoặc thêm ngrok vào PATH

### Lỗi: "authtoken invalid"

**Giải pháp:**
- Kiểm tra lại authtoken đã copy đúng chưa
- Lấy authtoken mới từ dashboard
- Đảm bảo đã đăng nhập đúng tài khoản

### Lỗi: "authtoken already installed"

**Giải pháp:**
- Authtoken đã được cài đặt rồi
- Có thể chạy ngrok ngay: `ngrok http 3000`

