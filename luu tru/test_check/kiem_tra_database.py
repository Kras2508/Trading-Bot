"""
Kiem tra thong tin database hien tai
"""
import sys
import os
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("="*60)
print("KIEM TRA DATABASE")
print("="*60)
print()

# 1. Lay config
print("Buoc 1: Lay cau hinh database...")
try:
    from app.core.config import settings
    
    db_url = settings.DATABASE_URL
    print(f"Database URL: {db_url}")
    
    # Phan tich loai database
    if "sqlite" in db_url.lower():
        db_type = "SQLite"
        # Extract file path
        if "///" in db_url:
            db_path = db_url.split("///")[-1]
        elif "//" in db_url:
            db_path = db_url.split("//")[-1]
        else:
            db_path = db_url.replace("sqlite:///", "")
        
        print(f"Loai database: {db_type}")
        print(f"Duong dan file: {db_path}")
        
        # Kiem tra file
        abs_path = Path(db_path).resolve()
        print(f"Duong dan tuyet doi: {abs_path}")
        
        if abs_path.exists():
            file_size = abs_path.stat().st_size
            print(f"[OK] File ton tai")
            print(f"Kich thuoc: {file_size:,} bytes ({file_size / 1024:.2f} KB)")
        else:
            print(f"[WARN] File khong ton tai")
            
    elif "postgresql" in db_url.lower() or "postgres" in db_url.lower():
        db_type = "PostgreSQL"
        print(f"Loai database: {db_type}")
        # Extract connection info (khong hien password)
        if "@" in db_url:
            parts = db_url.split("@")
            if len(parts) == 2:
                user_part = parts[0].split("//")[-1]
                if ":" in user_part:
                    user = user_part.split(":")[0]
                    print(f"User: {user}")
                host_db = parts[1]
                if "/" in host_db:
                    host = host_db.split("/")[0]
                    db_name = host_db.split("/")[1].split("?")[0]
                    print(f"Host: {host}")
                    print(f"Database: {db_name}")
    else:
        db_type = "Unknown"
        print(f"Loai database: {db_type}")
    
except Exception as e:
    print(f"[ERROR] Loi: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 2. Ket noi va kiem tra tables
print("\nBuoc 2: Ket noi database va kiem tra tables...")
try:
    from app.database import engine, SessionLocal
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"[OK] Ket noi thanh cong!")
    print(f"So luong tables: {len(tables)}")
    print(f"\nDanh sach tables:")
    for i, table in enumerate(tables, 1):
        print(f"  {i}. {table}")
        
        # Count rows
        try:
            db = SessionLocal()
            from sqlalchemy import text
            result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"     Rows: {count}")
            db.close()
        except Exception as e:
            print(f"     (Khong the dem rows: {e})")
    
except Exception as e:
    print(f"[ERROR] Loi: {e}")
    import traceback
    traceback.print_exc()

# 3. Kiem tra du lieu cu the
print("\nBuoc 3: Kiem tra du lieu...")
try:
    from app.database import SessionLocal
    from app.models.user import User
    from app.models.bot_config import BotConfig
    from app.models.order import Order
    from app.models.bot_status import BotStatus
    
    db = SessionLocal()
    
    # Users
    user_count = db.query(User).count()
    print(f"Users: {user_count}")
    
    # Configs
    config_count = db.query(BotConfig).count()
    print(f"Bot Configs: {config_count}")
    if config_count > 0:
        configs = db.query(BotConfig).all()
        for config in configs:
            print(f"  - ID: {config.id}, Name: {config.name}, Symbol: {config.symbol}")
    
    # Orders
    order_count = db.query(Order).count()
    print(f"Orders: {order_count}")
    if order_count > 0:
        orders = db.query(Order).all()
        for order in orders:
            print(f"  - ID: {order.id}, Symbol: {order.symbol}, Status: {order.status}")
    
    # Bot Status
    status_count = db.query(BotStatus).count()
    print(f"Bot Status: {status_count}")
    
    db.close()
    
except Exception as e:
    print(f"[ERROR] Loi: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*60)
print("\nTHONG TIN CHI TIET:")
print("="*60)
print(f"Database Type: {db_type if 'db_type' in locals() else 'Unknown'}")
print(f"Database URL: {db_url}")
if 'abs_path' in locals() and abs_path.exists():
    print(f"File Location: {abs_path}")
    print(f"File Size: {abs_path.stat().st_size:,} bytes")
print("="*60)

