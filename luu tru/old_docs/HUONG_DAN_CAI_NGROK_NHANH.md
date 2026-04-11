# Hướng Dẫn Cài Đặt Ngrok Nhanh

## Cách 1: Download Trực Tiếp (Khuyến Nghị)

1. **Truy cập**: https://ngrok.com/download
2. **Download**: Chọn Windows (64-bit)
3. **Giải nén**: Lấy file `ngrok.exe`
4. **Đặt vào thư mục project**: Copy `ngrok.exe` vào thư mục `D:\Website Docusaurus\BackendAPI_Trading\`
5. **Xác thực**:
   - Đăng ký: https://dashboard.ngrok.com/signup
   - Lấy token: https://dashboard.ngrok.com/get-started/your-authtoken
   - Chạy: `ngrok.exe config add-authtoken YOUR_TOKEN`

## Cách 2: Dùng Script

Chạy file:
```bash
CAI_DAT_NGROK.bat
```

## Sau Khi Cài Đặt

Chạy:
```bash
CHAY_NGROK_NHANH.bat
```

Hoặc trực tiếp:
```bash
ngrok.exe http 3000
```

## Kiểm Tra

Sau khi chạy ngrok, bạn sẽ thấy:
```
Forwarding   https://abc123.ngrok-free.app -> http://localhost:3000
```

URL công khai: `https://abc123.ngrok-free.app`

