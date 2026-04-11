# Hướng Dẫn Cài Đặt Trên Máy Mới

## Yêu Cầu Hệ Thống

- **Windows 10/11** hoặc **Linux/Mac**
- **Python 3.8+**
- **PostgreSQL 12+** (hoặc SQLite nếu không có PostgreSQL)
- **Node.js 16+** (cho frontend)
- **Git** (để clone code)

---

## Bước 1: Cài Đặt Python

### Windows:
1. Tải Python từ: https://www.python.org/downloads/
2. Chạy installer, **quan trọng**: Tick vào "Add Python to PATH"
3. Kiểm tra: Mở CMD/PowerShell, chạy:
   ```bash
   python --version
   ```
   Phải hiển thị: `Python 3.8.x` hoặc cao hơn

### Linux/Mac:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Mac
brew install python3
```

---

## Bước 2: Cài Đặt PostgreSQL (Khuyến nghị)

### Windows:
1. Tải PostgreSQL từ: https://www.postgresql.org/download/windows/
2. Chạy installer, nhớ **password của user postgres**
3. Cài đặt hoàn tất, PostgreSQL sẽ chạy tự động

### Linux:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Khởi động service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Mac:
```bash
brew install postgresql
brew services start postgresql
```

### Tạo Database:
```sql
-- Mở PostgreSQL client (pgAdmin hoặc psql)
CREATE DATABASE trading_bot;
```

---

## Bước 3: Clone/Copy Code

### Cách 1: Clone từ Git
```bash
git clone https://github.com/huongnghiepdulieu/BackendAPI_Trading.git
cd BackendAPI_Trading
```

### Cách 2: Copy thủ công
- Copy toàn bộ thư mục `BackendAPI_Trading` sang máy mới
- Đảm bảo giữ nguyên cấu trúc thư mục

---

## Bước 4: Cài Đặt Dependencies Backend

### Windows:
```bash
# Tạo virtual environment (khuyến nghị)
python -m venv venv

# Kích hoạt virtual environment
venv\Scripts\activate

# Cài đặt packages
pip install -r requirements.txt
```

### Linux/Mac:
```bash
# Tạo virtual environment
python3 -m venv venv

# Kích hoạt virtual environment
source venv/bin/activate

# Cài đặt packages
pip install -r requirements.txt
```

**Lưu ý**: Nếu gặp lỗi khi cài `psycopg2-binary` trên Windows:
```bash
# Cài đặt Visual C++ Build Tools trước
# Hoặc dùng pre-compiled wheel
pip install psycopg2-binary --only-binary :all:
```

---

## Bước 5: Cấu Hình Database

### Tạo file `.env` trong thư mục gốc:

```env
# Database
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/trading_bot
# Hoặc SQLite (nếu không có PostgreSQL):
# DATABASE_URL=sqlite:///./trading_bot.db

# App
APP_NAME=Trading Bot Backend
DEBUG=False

# Security - QUAN TRỌNG: Thay đổi các giá trị này!
SECRET_KEY=your-random-secret-key-min-32-chars-change-this-in-production
ENCRYPTION_KEY=your-random-32-byte-encryption-key-change-this

# CORS
CORS_ORIGINS=["*"]

# IP Whitelist
ENABLE_IP_WHITELIST=False
ALLOWED_IPS=

# Telegram (Optional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
ENABLE_TELEGRAM=False

# Exchange
DEFAULT_EXCHANGE=binance
```

**Lưu ý quan trọng:**
- Thay `your_password` bằng password PostgreSQL của bạn
- Thay `SECRET_KEY` và `ENCRYPTION_KEY` bằng các giá trị ngẫu nhiên (dùng để mã hóa JWT và API keys)

---

## Bước 6: Tạo Tables trong Database

### Nếu dùng PostgreSQL:
```bash
# Chạy script tự động
python doi_sang_postgresql_auto.py
```

Hoặc thủ công:
```bash
python -c "from app.database import Base; from app.models import *; from app.database import engine; Base.metadata.create_all(bind=engine)"
```

### Nếu dùng SQLite:
Tables sẽ tự động tạo khi chạy server lần đầu.

---

## Bước 7: Tạo User Đăng Nhập

```bash
python tao_user_trong_db.py
```

Hoặc tạo thủ công qua API:
```bash
# Chạy server trước
python run.py

# Trong terminal khác, tạo user
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin123",
    "is_admin": true
  }'
```

---

## Bước 8: Cài Đặt Frontend

```bash
cd frontend

# Cài đặt dependencies
npm install

# Hoặc nếu dùng yarn
yarn install
```

---

## Bước 9: Chạy Backend

### Windows:
```bash
# Cách 1: Dùng batch file
CHAY_SERVER.bat

# Cách 2: Chạy trực tiếp
python run.py

# Cách 3: Chạy trên port 80 (cần quyền Admin)
CHAY_BACKEND_PORT80.bat
```

### Linux/Mac:
```bash
python run.py
# Hoặc
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Kiểm tra**: Mở trình duyệt: http://localhost:8000/docs

---

## Bước 10: Chạy Frontend

### Windows:
```bash
cd frontend
CHAY_FRONTEND.bat
```

### Linux/Mac:
```bash
cd frontend
npm run dev
```

**Kiểm tra**: Mở trình duyệt: http://localhost:3000

---

## Bước 11: Đăng Nhập

1. Mở trình duyệt: http://localhost:3000
2. Đăng nhập với:
   - **Username**: `admin` (hoặc user bạn đã tạo)
   - **Password**: `admin123` (hoặc password bạn đã đặt)

---

## Troubleshooting

### Lỗi: "Module not found"
```bash
# Đảm bảo đã kích hoạt virtual environment
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Cài lại dependencies
pip install -r requirements.txt
```

### Lỗi: "Cannot connect to PostgreSQL"
1. Kiểm tra PostgreSQL đang chạy:
   ```bash
   # Windows: Services -> PostgreSQL
   # Linux: sudo systemctl status postgresql
   ```

2. Kiểm tra connection string trong `.env`:
   ```
   DATABASE_URL=postgresql://postgres:password@localhost:5432/trading_bot
   ```

3. Test kết nối:
   ```bash
   python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://postgres:password@localhost:5432/trading_bot'); print('OK')"
   ```

### Lỗi: "Port 8000 already in use"
```bash
# Windows: Tìm và kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill
```

### Lỗi: "Frontend không kết nối được backend"
1. Kiểm tra backend đang chạy: http://localhost:8000/health
2. Kiểm tra `vite.config.js`:
   ```javascript
   proxy: {
     '/api': {
       target: 'http://localhost:8000',
       changeOrigin: true
     }
   }
   ```

### Lỗi: "Permission denied" khi chạy trên port 80
- Windows: Chạy CMD/PowerShell với quyền Administrator
- Linux: Dùng `sudo` hoặc thay đổi port khác

---

## Checklist Cài Đặt

- [ ] Python 3.8+ đã cài đặt
- [ ] PostgreSQL đã cài đặt và chạy
- [ ] Database `trading_bot` đã tạo
- [ ] Code đã clone/copy
- [ ] Virtual environment đã tạo và kích hoạt
- [ ] Dependencies đã cài đặt (`pip install -r requirements.txt`)
- [ ] File `.env` đã tạo và cấu hình
- [ ] Tables đã tạo trong database
- [ ] User đăng nhập đã tạo
- [ ] Backend chạy được (http://localhost:8000/docs)
- [ ] Frontend dependencies đã cài (`npm install`)
- [ ] Frontend chạy được (http://localhost:3000)
- [ ] Đăng nhập thành công

---

## Cấu Hình Nâng Cao

### Chạy Backend như Service (Windows)
1. Tạo file `start_backend.bat`:
   ```batch
   @echo off
   cd /d "%~dp0"
   call venv\Scripts\activate
   python run.py
   ```

2. Tạo Windows Service hoặc dùng Task Scheduler

### Chạy Backend như Service (Linux)
Tạo systemd service file: `/etc/systemd/system/trading-bot.service`
```ini
[Unit]
Description=Trading Bot Backend
After=network.target postgresql.service

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/BackendAPI_Trading
Environment="PATH=/path/to/BackendAPI_Trading/venv/bin"
ExecStart=/path/to/BackendAPI_Trading/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Sau đó:
```bash
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
```

---

## Liên Hệ & Hỗ Trợ

Nếu gặp vấn đề, kiểm tra:
1. File log trong thư mục `logs/`
2. Console output của backend và frontend
3. File `.env` có đúng format không
4. Database connection string có đúng không

---

## Tóm Tắt Nhanh

```bash
# 1. Cài Python, PostgreSQL, Node.js

# 2. Clone code
git clone https://github.com/huongnghiepdulieu/BackendAPI_Trading.git
cd BackendAPI_Trading

# 3. Cài backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# 4. Cấu hình .env
# Tạo file .env với DATABASE_URL, SECRET_KEY, etc.

# 5. Tạo database và tables
python doi_sang_postgresql_auto.py

# 6. Tạo user
python tao_user_trong_db.py

# 7. Chạy backend
python run.py

# 8. Cài frontend (terminal khác)
cd frontend
npm install
npm run dev

# 9. Đăng nhập: http://localhost:3000
```

