"""
Script kiem tra ket noi PostgreSQL va xem database da tao chua
"""
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("="*60)
print("KIEM TRA POSTGRESQL")
print("="*60)
print()

# Thong tin mac dinh
host = "localhost"
port = 5432
username = "postgres"
password = "postgres"

print("Nhap thong tin PostgreSQL:")
print("(Nhan Enter de su dung gia tri mac dinh)")
print()

host_input = input(f"Host [{host}]: ").strip()
if host_input:
    host = host_input

port_input = input(f"Port [{port}]: ").strip()
if port_input:
    try:
        port = int(port_input)
    except ValueError:
        print(f"[WARN] Port khong hop le, su dung mac dinh: {port}")

username_input = input(f"Username [{username}]: ").strip()
if username_input:
    username = username_input

password_input = input(f"Password [{password}]: ").strip()
if password_input:
    password = password_input

print()
print(f"Host: {host}")
print(f"Port: {port}")
print(f"Username: {username}")
print()

# Test connection to PostgreSQL server (khong can database cu the)
print("Buoc 1: Test ket noi den PostgreSQL server...")
try:
    from sqlalchemy import create_engine, text
    
    # Ket noi den database 'postgres' (database mac dinh)
    connection_string = f"postgresql://{username}:{password}@{host}:{port}/postgres"
    
    engine = create_engine(connection_string, echo=False)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"[OK] Ket noi thanh cong den PostgreSQL server!")
        print(f"PostgreSQL Version: {version[:100]}...")
        
except ImportError:
    print("[ERROR] Chua cai dat psycopg2-binary!")
    print("Chay lenh: pip install psycopg2-binary")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Khong the ket noi: {e}")
    print("\nKiem tra:")
    print("1. PostgreSQL da chay chua?")
    print("2. Host/Port co dung khong?")
    print("3. Username/Password co dung khong?")
    sys.exit(1)

# List all databases
print("\nBuoc 2: Danh sach databases...")
try:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT datname 
            FROM pg_database 
            WHERE datistemplate = false
            ORDER BY datname
        """))
        databases = [row[0] for row in result]
        
        print(f"[OK] Tim thay {len(databases)} database(s):")
        for db in databases:
            print(f"  - {db}")
        
        # Check for common trading bot database names
        common_names = ['trading_bot', 'backendapi_trading', 'tradingbot']
        found = False
        for name in common_names:
            if name in databases:
                print(f"\n[INFO] Tim thay database co ten tuong tu: {name}")
                found = True
        
        if not found:
            print("\n[INFO] Khong tim thay database nao co ten 'trading_bot'")
            print("[INFO] Co the tao database bang lenh:")
            print("  CREATE DATABASE trading_bot;")
        
except Exception as e:
    print(f"[ERROR] Khong the lay danh sach databases: {e}")

# Check specific database if user wants
print("\nBuoc 3: Kiem tra database cu the...")
database_name = input("Nhap ten database de kiem tra (hoac Enter de bo qua): ").strip()

if database_name:
    try:
        connection_string_db = f"postgresql://{username}:{password}@{host}:{port}/{database_name}"
        engine_db = create_engine(connection_string_db, echo=False)
        
        with engine_db.connect() as conn:
            # Check if database exists and is accessible
            result = conn.execute(text("SELECT current_database()"))
            current_db = result.scalar()
            print(f"[OK] Ket noi thanh cong den database: {current_db}")
            
            # List tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            if tables:
                print(f"[OK] Tim thay {len(tables)} table(s):")
                for table in tables:
                    print(f"  - {table}")
            else:
                print("[INFO] Database chua co table nao")
                print("[INFO] Co the chay script doi_sang_postgresql_auto.py de tao tables")
            
    except Exception as e:
        print(f"[ERROR] Khong the ket noi den database '{database_name}': {e}")
        print("[INFO] Database co the chua duoc tao. Tao database bang lenh:")
        print(f"  CREATE DATABASE {database_name};")

print("\n" + "="*60)
print("HOAN TAT!")
print("="*60)

