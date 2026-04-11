# Câu Lệnh Expose Frontend Ra Internet

## Frontend đang chạy tại: http://localhost:3000

## Câu Lệnh Ngrok

### Cách 1: Lệnh Đơn Giản

```bash
ngrok http 3000
```

### Cách 2: Với Domain Tĩnh (Nếu có Paid Plan)

```bash
ngrok http 3000 --domain=your-domain.ngrok.app
```

### Cách 3: Với Subdomain Tùy Chỉnh

```bash
ngrok http 3000 --subdomain=trading-bot
```

---

## Sau Khi Chạy

Ngrok sẽ hiển thị:

```
Forwarding   https://abc123.ngrok-free.app -> http://localhost:3000
```

**URL công khai:**
- HTTPS: `https://abc123.ngrok-free.app`
- HTTP: `http://abc123.ngrok-free.app`

---

## Kiểm Tra

Mở browser và truy cập: `https://abc123.ngrok-free.app`

---

## Ngrok Dashboard

Xem tất cả requests tại: `http://127.0.0.1:4040`

---

## Lưu Ý

1. **Cài đặt ngrok** (nếu chưa có):
   - Download: https://ngrok.com/download
   - Xác thực: `ngrok config add-authtoken YOUR_TOKEN`

2. **Backend phải đang chạy** tại `http://127.0.0.1:8000` (frontend sẽ proxy đến)

3. **Frontend phải đang chạy** tại `http://localhost:3000`

---

## Quick Start

```bash
# 1. Chạy backend (nếu chưa chạy)
python run.py

# 2. Chạy frontend (nếu chưa chạy)
cd frontend
npm run dev

# 3. Expose frontend ra internet
ngrok http 3000
```

