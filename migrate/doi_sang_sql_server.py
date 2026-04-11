"""
Script de doi database tu SQLite sang SQL Server
"""
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("="*60)
print("DOI DATABASE SANG SQL SERVER")
print("="*60)
print()

print("Thong tin tu SQL Server Management Studio:")
print("  Server: DESKTOP-MDT6RKU\\TGC")
print("  Database: BackendAPI_Trading")
print("  SQL Server Version: 16.0.1000.6 (SQL Server 2022)")
print()

# Thong tin ket noi
print("Nhap thong tin ket noi SQL Server:")
print("(Neu de trong se dung gia tri mac dinh)")
print()

server = input("Server [DESKTOP-MDT6RKU\\TGC]: ").strip() or "DESKTOP-MDT6RKU\\TGC"
database = input("Database [BackendAPI_Trading]: ").strip() or "BackendAPI_Trading"

use_windows_auth = input("Su dung Windows Authentication? (y/n) [y]: ").strip().lower() or "y"

if use_windows_auth == "y":
    # Windows Authentication
    # Format: mssql+pyodbc://server/database?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
    connection_string = f"mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    print("\n[INFO] Su dung Windows Authentication")
else:
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"

print(f"\nConnection String: {connection_string}")
print()

# Test connection
print("Buoc 1: Test ket noi...")
try:
    from sqlalchemy import create_engine, text
    
    engine = create_engine(connection_string, echo=False)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT @@VERSION"))
        version = result.scalar()
        print(f"[OK] Ket noi thanh cong!")
        print(f"SQL Server Version: {version[:100]}...")
        
        # Check if database exists
        result = conn.execute(text(f"SELECT name FROM sys.databases WHERE name = '{database}'"))
        db_exists = result.fetchone()
        if db_exists:
            print(f"[OK] Database '{database}' da ton tai")
        else:
            print(f"[WARN] Database '{database}' chua ton tai")
            create = input(f"Co muon tao database '{database}' khong? (y/n): ").strip().lower()
            if create == "y":
                conn.execute(text(f"CREATE DATABASE [{database}]"))
                conn.commit()
                print(f"[OK] Da tao database '{database}'")
        
except ImportError:
    print("[ERROR] Chua cai dat pyodbc!")
    print("Chay lenh: pip install pyodbc")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Khong the ket noi: {e}")
    print("\nKiem tra:")
    print("1. SQL Server da chay chua?")
    print("2. Database 'BackendAPI_Trading' da duoc tao chua?")
    print("3. Da cai dat ODBC Driver 17 for SQL Server chua?")
    print("   Download: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")
    print("4. Co quyen truy cap database khong?")
    sys.exit(1)

# Update .env file
print("\nBuoc 2: Cap nhat file .env...")

# Read existing .env if exists
env_vars = {}
if os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()

# Update DATABASE_URL
env_vars["DATABASE_URL"] = connection_string

# Write .env
env_content = f"""# Database
DATABASE_URL={connection_string}

# App
APP_NAME=Trading Bot Backend
DEBUG=False

# Security
SECRET_KEY={env_vars.get('SECRET_KEY', 'your-secret-key-change-in-production-min-32-chars-12345')}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
CORS_ORIGINS=["*"]

# IP Whitelist
ENABLE_IP_WHITELIST=False
ALLOWED_IPS=

# Telegram
TELEGRAM_BOT_TOKEN={env_vars.get('TELEGRAM_BOT_TOKEN', '')}
TELEGRAM_CHAT_ID={env_vars.get('TELEGRAM_CHAT_ID', '')}
ENABLE_TELEGRAM=False

# Exchange
DEFAULT_EXCHANGE=binance

# Encryption
ENCRYPTION_KEY={env_vars.get('ENCRYPTION_KEY', 'your-32-byte-encryption-key-change-this')}
"""

try:
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)
    print("[OK] Da cap nhat file .env")
except Exception as e:
    print(f"[ERROR] Khong the ghi file .env: {e}")

# Create tables
print("\nBuoc 3: Tao tables trong SQL Server...")
try:
    from app.database import Base
    from app.models import user, bot_config, bot_status, order, activity_log
    
    # Recreate engine with new connection string
    engine = create_engine(connection_string, echo=False)
    Base.metadata.create_all(bind=engine)
    print("[OK] Da tao tables thanh cong!")
    
    # Verify tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\nTables da tao: {', '.join(tables)}")
    
except Exception as e:
    print(f"[ERROR] Loi khi tao tables: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("HOAN TAT!")
print("="*60)
print("Database da duoc doi sang SQL Server")
print("Vui long restart server de ap dung thay doi")
print("="*60)
