"""
Script kiem tra PostgreSQL don gian
"""
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("="*60)
print("KIEM TRA POSTGRESQL")
print("="*60)
print()

# Doc thong tin tu .env neu co
host = "localhost"
port = 5432
username = "postgres"
password = "postgres"
database = "trading_bot"

# Doc tu .env neu co DATABASE_URL
if os.path.exists(".env"):
    print("Doc thong tin tu file .env...")
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("DATABASE_URL="):
                db_url = line.split("=", 1)[1].strip()
                if db_url.startswith("postgresql://"):
                    # Parse: postgresql://user:pass@host:port/db
                    try:
                        url_part = db_url.replace("postgresql://", "")
                        if "@" in url_part:
                            auth_part, rest = url_part.split("@", 1)
                            if ":" in auth_part:
                                username, password = auth_part.split(":", 1)
                            if "/" in rest:
                                host_port, database = rest.split("/", 1)
                                if ":" in host_port:
                                    host, port_str = host_port.split(":", 1)
                                    try:
                                        port = int(port_str)
                                    except:
                                        pass
                                else:
                                    host = host_port
                    except:
                        pass
                print(f"  Tim thay DATABASE_URL trong .env")
                break

print(f"Host: {host}")
print(f"Port: {port}")
print(f"Username: {username}")
print(f"Database: {database}")
print()

# Test connection
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
        print(f"PostgreSQL Version: {version.split(',')[0]}")
        
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
            marker = " <-- DANG SU DUNG" if db == database else ""
            print(f"  - {db}{marker}")
        
        # Check if target database exists
        if database in databases:
            print(f"\n[OK] Database '{database}' da ton tai!")
            
            # Check tables in this database
            print(f"\nBuoc 3: Kiem tra tables trong database '{database}'...")
            try:
                connection_string_db = f"postgresql://{username}:{password}@{host}:{port}/{database}"
                engine_db = create_engine(connection_string_db, echo=False)
                
                with engine_db.connect() as conn_db:
                    result = conn_db.execute(text("""
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
                        print("[INFO] Chay script doi_sang_postgresql_auto.py de tao tables")
                    
            except Exception as e:
                print(f"[ERROR] Khong the ket noi den database '{database}': {e}")
        else:
            print(f"\n[INFO] Database '{database}' chua ton tai")
            print("[INFO] Tao database bang lenh:")
            print(f"  CREATE DATABASE {database};")
            print("\nHoac chay script doi_sang_postgresql_auto.py de tu dong tao")
        
except Exception as e:
    print(f"[ERROR] Khong the lay danh sach databases: {e}")

print("\n" + "="*60)
print("HOAN TAT!")
print("="*60)

