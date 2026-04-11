# Hướng dẫn Cài đặt và Chạy Backend

## Cách 1: Sử dụng Script Batch (Dễ nhất - Windows)

### Bước 1: Chạy script cài đặt và chạy tự động
```bash
setup_and_run.bat
```

Script này sẽ:
- Tự động cài đặt dependencies
- Tạo file .env nếu chưa có
- Chạy server

### Bước 2: Hoặc chạy từng bước

**Cài đặt dependencies:**
```bash
install.bat
```

**Chạy server:**
```bash
run.bat
```

## Cách 2: Chạy thủ công

### Bước 1: Cài đặt dependencies
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Bước 2: Tạo file .env
Copy file `.env.example` thành `.env`:
```bash
copy .env.example .env
```

Sau đó chỉnh sửa file `.env` và thêm các giá trị cần thiết (ít nhất là SECRET_KEY và ENCRYPTION_KEY).

### Bước 3: Chạy server
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Hoặc sử dụng file run.py:
```bash
python run.py
```

## Cách 3: Sử dụng Virtual Environment (Khuyến nghị)

### Bước 1: Tạo virtual environment
```bash
python -m venv venv
```

### Bước 2: Kích hoạt virtual environment
```bash
venv\Scripts\activate
```

### Bước 3: Cài đặt dependencies
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Bước 4: Tạo file .env
```bash
copy .env.example .env
```

### Bước 5: Chạy server
```bash
python run.py
```

## Kiểm tra Server

Sau khi chạy server, mở trình duyệt và truy cập:

- **API Documentation (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Root**: http://localhost:8000/

## Troubleshooting

### Lỗi: "uvicorn is not recognized"
**Giải pháp:** Chạy `python -m uvicorn` thay vì `uvicorn`

### Lỗi: "pip is not recognized"
**Giải pháp:** Chạy `python -m pip` thay vì `pip`

### Lỗi: "Module not found"
**Giải pháp:** Đảm bảo đã cài đặt dependencies:
```bash
python -m pip install -r requirements.txt
```

### Lỗi: "Python path configuration"
**Giải pháp:** 
- Kiểm tra Python đã được cài đặt đúng chưa
- Thử tạo virtual environment mới
- Hoặc cài đặt lại Python

### Lỗi: Port 8000 đã được sử dụng
**Giải pháp:** Đổi port:
```bash
python -m uvicorn app.main:app --reload --port 8001
```

## Cấu hình tối thiểu trong .env

File `.env` tối thiểu cần có:
```env
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
ENCRYPTION_KEY=your-32-byte-encryption-key-change-this
DATABASE_URL=sqlite:///./trading_bot.db
```

## Sau khi chạy thành công

1. Truy cập http://localhost:8000/docs để xem API documentation
2. Đăng ký user đầu tiên qua API `/api/auth/register`
3. Đăng nhập để lấy JWT token
4. Tạo bot config qua API `/api/config/`
5. Test webhook qua API `/api/webhook/tradingview`

Xem file `QUICKSTART.md` để biết chi tiết các bước tiếp theo!

