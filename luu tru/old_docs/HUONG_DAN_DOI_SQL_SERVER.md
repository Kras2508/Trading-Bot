# Hướng dẫn Đổi Database sang SQL Server

## Bước 1: Cài đặt ODBC Driver

Tải và cài đặt **ODBC Driver 17 for SQL Server**:
- Download: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
- Chọn phiên bản phù hợp với Windows của bạn (x64 hoặc x86)

## Bước 2: Cài đặt Python Package

```bash
pip install pyodbc
```

Hoặc cài đặt tất cả dependencies:
```bash
pip install -r requirements.txt
```

## Bước 3: Chạy Script Đổi Database

```bash
python doi_sang_sql_server.py
```

Script sẽ:
1. Hỏi thông tin kết nối SQL Server
2. Test kết nối
3. Cập nhật file `.env`
4. Tạo tables trong SQL Server

## Bước 4: Cấu hình Thủ công (Nếu cần)

Nếu muốn cấu hình thủ công, chỉnh sửa file `.env`:

### Windows Authentication:
```env
DATABASE_URL=mssql+pyodbc://DESKTOP-MDT6RKU\TGC/BackendAPI_Trading?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

### SQL Server Authentication:
```env
DATABASE_URL=mssql+pyodbc://username:password@DESKTOP-MDT6RKU\TGC/BackendAPI_Trading?driver=ODBC+Driver+17+for+SQL+Server
```

## Bước 5: Restart Server

Sau khi đổi database, restart server:
```bash
python run.py
```

## Kiểm tra

Chạy script kiểm tra:
```bash
python kiem_tra_database.py
```

## Lưu ý

1. **Backup dữ liệu SQLite** trước khi đổi (nếu cần):
   - File: `trading_bot.db`
   - Có thể migrate dữ liệu sau

2. **Database phải tồn tại** trên SQL Server:
   - Tạo database `BackendAPI_Trading` trong SQL Server Management Studio
   - Hoặc script sẽ tự động tạo (nếu có quyền)

3. **Quyền truy cập**:
   - Windows Authentication: Đảm bảo user Windows có quyền truy cập SQL Server
   - SQL Server Authentication: Đảm bảo username/password đúng

4. **ODBC Driver**:
   - Phải cài đặt ODBC Driver 17 for SQL Server
   - Có thể kiểm tra trong "ODBC Data Source Administrator"

## Troubleshooting

### Lỗi: "Driver not found"
- Cài đặt ODBC Driver 17 for SQL Server
- Kiểm tra trong "ODBC Data Source Administrator" (Windows)

### Lỗi: "Cannot open database"
- Kiểm tra database đã được tạo chưa
- Kiểm tra quyền truy cập
- Kiểm tra SQL Server đang chạy

### Lỗi: "Login failed"
- Kiểm tra username/password
- Hoặc kiểm tra Windows Authentication có hoạt động không

