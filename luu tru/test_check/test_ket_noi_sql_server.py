"""
Test ket noi SQL Server voi nhieu format khac nhau
"""
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("="*60)
print("TEST KET NOI SQL SERVER")
print("="*60)
print()

# Cac format thu
formats = [
    # Format 1: Server\Instance
    ("DESKTOP-MDT6RKU\\TGC", "BackendAPI_Trading"),
    # Format 2: localhost
    ("localhost", "BackendAPI_Trading"),
    # Format 3: . (local)
    (".", "BackendAPI_Trading"),
    # Format 4: localhost\TGC
    ("localhost\\TGC", "BackendAPI_Trading"),
    # Format 5: DESKTOP-MDT6RKU
    ("DESKTOP-MDT6RKU", "BackendAPI_Trading"),
]

print("Dang thu ket noi voi cac format khac nhau...")
print()

for server, database in formats:
    print(f"Thu: {server} / {database}")
    
    # Windows Auth
    connection_string = f"mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    
    try:
        from sqlalchemy import create_engine, text
        
        engine = create_engine(connection_string, echo=False, connect_args={"timeout": 5})
        with engine.connect() as conn:
            result = conn.execute(text("SELECT @@VERSION"))
            version = result.scalar()
            print(f"[OK] Ket noi thanh cong!")
            print(f"SQL Server Version: {version[:80]}...")
            
            # Check database
            result = conn.execute(text(f"SELECT name FROM sys.databases WHERE name = '{database}'"))
            db_exists = result.fetchone()
            if db_exists:
                print(f"[OK] Database '{database}' ton tai")
            else:
                print(f"[WARN] Database '{database}' chua ton tai")
            
            print(f"\n[SUCCESS] Connection string dung:")
            print(f"  {connection_string}")
            print()
            
            # Update .env
            import os
            env_vars = {}
            if os.path.exists(".env"):
                with open(".env", "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            env_vars[key.strip()] = value.strip()
            
            env_vars["DATABASE_URL"] = connection_string
            
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
            
            with open(".env", "w", encoding="utf-8") as f:
                f.write(env_content)
            print("[OK] Da cap nhat file .env")
            
            # Create tables
            print("\nTao tables...")
            from app.database import Base
            from app.models import user, bot_config, bot_status, order, activity_log
            
            Base.metadata.create_all(bind=engine)
            print("[OK] Da tao tables")
            
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"Tables: {', '.join(tables)}")
            
            break
            
    except Exception as e:
        error_msg = str(e)
        if "Server is not found" in error_msg or "not accessible" in error_msg:
            print(f"[FAIL] Khong tim thay server")
        elif "Login failed" in error_msg:
            print(f"[FAIL] Login that bai")
        elif "Cannot open database" in error_msg:
            print(f"[FAIL] Khong the mo database")
        else:
            print(f"[FAIL] {error_msg[:100]}")
        print()
        continue

print("="*60)
print("\nHUONG DAN:")
print("="*60)
print("1. Kiem tra SQL Server da chay:")
print("   - Mo SQL Server Configuration Manager")
print("   - Kiem tra SQL Server (TGC) service dang chay")
print()
print("2. Kiem tra SQL Server Browser:")
print("   - Mo SQL Server Configuration Manager")
print("   - Kiem tra SQL Server Browser service dang chay")
print()
print("3. Kiem tra SQL Server Authentication:")
print("   - Mo SQL Server Management Studio")
print("   - Connect voi: DESKTOP-MDT6RKU\\TGC")
print("   - Neu connect duoc, copy chinh xac server name")
print()
print("4. Kiem tra TCP/IP:")
print("   - Mo SQL Server Configuration Manager")
print("   - SQL Server Network Configuration > Protocols for TGC")
print("   - Enable TCP/IP")
print("   - Restart SQL Server service")
print()
print("5. Thu ket noi bang SQL Server Management Studio:")
print("   - Server name: DESKTOP-MDT6RKU\\TGC")
print("   - Neu connect duoc, server name dung")
print("   - Neu khong, thu: localhost, ., hoac IP address")
print("="*60)

