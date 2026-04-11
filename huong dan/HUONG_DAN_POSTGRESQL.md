# Hướng Dẫn Chuyển Đổi Sang PostgreSQL

## Yêu Cầu

1. **PostgreSQL đã được cài đặt và đang chạy**
2. **Đã tạo database** (hoặc có quyền tạo database)
3. **Đã cài đặt psycopg2-binary**: `pip install psycopg2-binary`

## Các Bước Chuyển Đổi

### Cách 1: Sử dụng Script Tự Động (Khuyến nghị)

1. **Chạy script:**
   ```bash
   DOI_SANG_POSTGRESQL.bat
   ```
   Hoặc:
   ```bash
   python doi_sang_postgresql_auto.py
   ```

2. **Nhập thông tin PostgreSQL:**
   - Host (mặc định: `localhost`)
   - Port (mặc định: `5432`)
   - Database (mặc định: `trading_bot`)
   - Username (mặc định: `postgres`)
   - Password (mặc định: `postgres`)

3. **Script sẽ tự động:**
   - Test kết nối PostgreSQL
   - Cập nhật file `.env` với connection string mới
   - Tạo tất cả tables trong PostgreSQL

### Cách 2: Cấu Hình Thủ Công

1. **Tạo database trong PostgreSQL:**
   ```sql
   CREATE DATABASE trading_bot;
   ```

2. **Cập nhật file `.env`:**
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/trading_bot
   ```

3. **Restart server** để áp dụng thay đổi

## Format Connection String

```
postgresql://username:password@host:port/database
```

**Ví dụ:**
```
postgresql://postgres:mypassword@localhost:5432/trading_bot
postgresql://user:pass@192.168.1.100:5432/trading_bot
```

## Lưu Ý

1. **Logic không thay đổi**: Tất cả logic code vẫn giữ nguyên vì sử dụng SQLAlchemy ORM
2. **Dữ liệu cũ**: Nếu có dữ liệu trong SQL Server, cần migrate thủ công hoặc export/import
3. **Backup**: Nên backup dữ liệu trước khi chuyển đổi
4. **Tables**: Script sẽ tự động tạo tables nếu chưa có

## Kiểm Tra

Sau khi chuyển đổi, kiểm tra:

1. **Server chạy không lỗi:**
   ```bash
   python run.py
   ```

2. **Test API:**
   - Health check: `http://localhost:8000/health`
   - API Docs: `http://localhost:8000/docs`

3. **Kiểm tra database:**
   ```sql
   \dt  -- List tables trong PostgreSQL
   SELECT * FROM users LIMIT 1;
   ```

## Quay Lại SQL Server

Nếu muốn quay lại SQL Server, chạy:
```bash
doi_sang_sql_server_auto.py
```

Hoặc cập nhật `.env`:
```env
DATABASE_URL=mssql+pyodbc://server/database?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

## Troubleshooting

### Lỗi: "psycopg2 not found"
```bash
pip install psycopg2-binary
```

### Lỗi: "Connection refused"
- Kiểm tra PostgreSQL đang chạy: `pg_isready`
- Kiểm tra firewall/port 5432

### Lỗi: "Database does not exist"
- Tạo database: `CREATE DATABASE trading_bot;`

### Lỗi: "Permission denied"
- Kiểm tra username/password
- Kiểm tra quyền truy cập database

