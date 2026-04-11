# Hướng dẫn Triển khai và Vận hành

## 1. Cài đặt Môi trường

### Yêu cầu hệ thống
- Python 3.8 trở lên
- PostgreSQL (khuyến nghị) hoặc SQLite
- Server có thể truy cập từ internet (cho webhook TradingView)

### Cài đặt Dependencies

```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Cài đặt packages
pip install -r requirements.txt
```

## 2. Cấu hình

### Tạo file .env

Copy file `.env.example` thành `.env` và điền thông tin:

```bash
cp .env.example .env
```

### Các thông tin cần cấu hình:

1. **Database**
   - SQLite (mặc định): `DATABASE_URL=sqlite:///./trading_bot.db`
   - PostgreSQL: `DATABASE_URL=postgresql://user:password@localhost/trading_bot`

2. **Security**
   - `SECRET_KEY`: Tạo key ngẫu nhiên (ít nhất 32 ký tự)
   - `ENCRYPTION_KEY`: Tạo key ngẫu nhiên (32 bytes)

3. **Telegram**
   - Tạo bot qua BotFather trên Telegram
   - Lấy `TELEGRAM_BOT_TOKEN`
   - Lấy `TELEGRAM_CHAT_ID` (có thể dùng @userinfobot)
   - Bật `ENABLE_TELEGRAM=True`

4. **IP Whitelist** (tùy chọn)
   - `ENABLE_IP_WHITELIST=True`
   - `ALLOWED_IPS=your-ip-address,another-ip`

## 3. Khởi tạo Database

Database sẽ tự động tạo khi chạy lần đầu. Nếu muốn dùng Alembic migrations:

```bash
# Khởi tạo Alembic (nếu chưa có)
alembic init alembic

# Tạo migration
alembic revision --autogenerate -m "Initial migration"

# Chạy migration
alembic upgrade head
```

## 4. Chạy Ứng dụng

### Development

```bash
python run.py
```

Hoặc:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production với Gunicorn

```bash
pip install gunicorn

gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120
```

### Production với Systemd (Linux)

Tạo file `/etc/systemd/system/trading-bot-api.service`:

```ini
[Unit]
Description=Trading Bot Backend API
After=network.target

[Service]
User=your-user
WorkingDirectory=/path/to/BackendAPI_Trading
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Khởi động service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable trading-bot-api
sudo systemctl start trading-bot-api
sudo systemctl status trading-bot-api
```

## 5. Cấu hình Nginx (Reverse Proxy)

Tạo file `/etc/nginx/sites-available/trading-bot-api`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Kích hoạt:

```bash
sudo ln -s /etc/nginx/sites-available/trading-bot-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 6. SSL/HTTPS với Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 7. Tạo User đầu tiên

Sử dụng API hoặc script:

```bash
# Đăng ký user
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "your-secure-password",
    "is_admin": true
  }'

# Đăng nhập để lấy token
curl -X POST "http://localhost:8000/api/auth/login?username=admin&password=your-secure-password"
```

## 8. Tạo Bot Config đầu tiên

```bash
curl -X POST "http://localhost:8000/api/config/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "BTC Spot Bot",
    "symbol": "BTC/USDT",
    "exchange": "binance",
    "amount": 100.0,
    "stop_loss_percent": 2.0,
    "take_profit_percent": 5.0,
    "trading_mode": "spot",
    "api_key": "your-api-key",
    "api_secret": "your-api-secret",
    "enable_notifications": true
  }'
```

## 9. Cấu hình TradingView Webhook

1. Tạo alert trong TradingView
2. Webhook URL: `https://your-domain.com/api/webhook/tradingview`
3. Alert Message:

```json
{
  "symbol": "BTC/USDT",
  "action": "buy",
  "config": "BTC Spot Bot"
}
```

## 10. Monitoring và Logs

### Xem logs

```bash
# Application logs
tail -f logs/app.log

# System logs (nếu dùng systemd)
sudo journalctl -u trading-bot-api -f
```

### Health Check

```bash
curl http://localhost:8000/health
```

### API Documentation

- Swagger UI: `http://your-domain.com/docs`
- ReDoc: `http://your-domain.com/redoc`

## 11. Backup Database

### SQLite

```bash
cp trading_bot.db trading_bot_backup_$(date +%Y%m%d).db
```

### PostgreSQL

```bash
pg_dump -U user trading_bot > backup_$(date +%Y%m%d).sql
```

## 12. Troubleshooting

### Lỗi kết nối database
- Kiểm tra `DATABASE_URL` trong `.env`
- Đảm bảo database service đang chạy
- Kiểm tra quyền truy cập

### Webhook không nhận được request
- Kiểm tra firewall
- Kiểm tra IP whitelist (nếu bật)
- Kiểm tra logs để xem request có đến không

### Telegram không gửi được thông báo
- Kiểm tra `TELEGRAM_BOT_TOKEN` và `TELEGRAM_CHAT_ID`
- Đảm bảo bot đã được thêm vào chat/group
- Kiểm tra `ENABLE_TELEGRAM=True`

### Lỗi mã hóa/giải mã
- Đảm bảo `ENCRYPTION_KEY` không thay đổi sau khi đã lưu data
- Nếu thay đổi key, cần mã hóa lại tất cả API keys trong database

## 13. Bảo mật

1. **Luôn sử dụng HTTPS** trong production
2. **Thay đổi SECRET_KEY và ENCRYPTION_KEY** từ giá trị mặc định
3. **Bật IP whitelist** cho webhook nếu có thể
4. **Giới hạn CORS_ORIGINS** thay vì `["*"]`
5. **Sử dụng strong passwords** cho database
6. **Backup định kỳ** database
7. **Giám sát logs** để phát hiện bất thường

## 14. Cập nhật

```bash
# Pull code mới
git pull

# Cài đặt dependencies mới
pip install -r requirements.txt

# Chạy migrations (nếu có)
alembic upgrade head

# Restart service
sudo systemctl restart trading-bot-api
```

