"""
Script tu dong doi database tu SQL Server sang PostgreSQL
"""
import sys
import os

# Them thu muc goc project vao sys.path de tim duoc module 'app'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("="*60)
print("DOI DATABASE SANG POSTGRESQL (TU DONG)")
print("="*60)
print()

# Thong tin mac dinh PostgreSQL
host = "localhost"
port = 5432
database = "trading_bot"
username = "postgres"
password = "123"  # Password da duoc cung cap

print("Thong tin PostgreSQL:")
print(f"Host: {host}")
print(f"Port: {port}")
print(f"Database: {database}")
print(f"Username: {username}")
print(f"Password: {'*' * len(password)}")
print()


# Connection string PostgreSQL (ket noi den database 'postgres' de tao database moi)
connection_string_postgres = f"postgresql://{username}:{password}@{host}:{port}/postgres"
connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"

print(f"Connection String: postgresql://{username}:***@{host}:{port}/{database}")
print()

# Test connection to PostgreSQL server
print("Buoc 1: Test ket noi den PostgreSQL server...")
try:
    from sqlalchemy import create_engine, text
    
    # Ket noi den database 'postgres' (database mac dinh)
    engine_postgres = create_engine(connection_string_postgres, echo=False)
    with engine_postgres.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"[OK] Ket noi thanh cong den PostgreSQL server!")
        print(f"PostgreSQL Version: {version[:100]}...")
        
except ImportError:
    print("[ERROR] Chua cai dat psycopg2-binary!")
    print("Chay lenh: pip install psycopg2-binary")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Khong the ket noi den PostgreSQL server: {e}")
    print("\nKiem tra:")
    print("1. PostgreSQL da chay chua?")
    print("2. Host/Port co dung khong?")
    print("3. Username/Password co dung khong?")
    sys.exit(1)

# Check and create database if not exists
print(f"\nBuoc 2: Kiem tra database '{database}'...")
try:
    # Check if database exists
    with engine_postgres.connect() as conn:
        result = conn.execute(text("""
            SELECT 1 FROM pg_database WHERE datname = :dbname
        """), {"dbname": database})
        db_exists = result.fetchone()
    
    if db_exists:
        print(f"[OK] Database '{database}' da ton tai!")
    else:
        print(f"[INFO] Database '{database}' chua ton tai, dang tao...")
        # Create database - use psycopg2 directly with autocommit
        # CREATE DATABASE cannot run inside a transaction block
        import psycopg2
        conn_psycopg2 = psycopg2.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database='postgres'  # Connect to default database
        )
        conn_psycopg2.autocommit = True
        cursor = conn_psycopg2.cursor()
        try:
            cursor.execute(f'CREATE DATABASE "{database}"')
            print(f"[OK] Da tao database '{database}' thanh cong!")
        finally:
            cursor.close()
            conn_psycopg2.close()
        
except Exception as e:
    print(f"[ERROR] Loi khi kiem tra/tao database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test connection to target database
print(f"\nBuoc 3: Test ket noi den database '{database}'...")
try:
    engine = create_engine(connection_string, echo=False)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT current_database()"))
        current_db = result.scalar()
        print(f"[OK] Ket noi thanh cong den database: {current_db}")
        
except Exception as e:
    print(f"[ERROR] Khong the ket noi den database '{database}': {e}")
    print("\nKiem tra quyen truy cap database")
    sys.exit(1)

# Read existing .env if exists
env_vars = {}
if os.path.exists(".env"):
    print("\nBuoc 4: Doc file .env hien tai...")
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()
    print("[OK] Da doc file .env")

# Update DATABASE_URL
env_vars["DATABASE_URL"] = connection_string

# Write .env
print("\nBuoc 5: Cap nhat file .env...")
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
    sys.exit(1)

# Create tables
print("\nBuoc 6: Tao tables trong PostgreSQL...")
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
    print(f"\nTables da tao ({len(tables)}):")
    for table in tables:
        print(f"  - {table}")
    
except Exception as e:
    print(f"[ERROR] Loi khi tao tables: {e}")
    import traceback
    traceback.print_exc()
    print("\n[INFO] Co the tables da ton tai hoac co loi. Kiem tra trong PostgreSQL client")

print("\n" + "="*60)
print("HOAN TAT!")
print("="*60)
print("Database da duoc doi sang PostgreSQL")
print("Vui long restart server de ap dung thay doi")
print("="*60)

