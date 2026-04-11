"""
Test ket noi PostgreSQL nhanh
"""
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Thong tin
host = "localhost"
port = 5432
username = "postgres"
password = "1"

print("="*60)
print("TEST KET NOI POSTGRESQL")
print("="*60)
print()
print(f"Host: {host}")
print(f"Port: {port}")
print(f"Username: {username}")
print(f"Password: {'*' * len(password)}")
print()

# Test connection
print("Dang test ket noi...")
try:
    from sqlalchemy import create_engine, text
    
    # Ket noi den database 'postgres' (database mac dinh)
    connection_string = f"postgresql://{username}:{password}@{host}:{port}/postgres"
    
    engine = create_engine(connection_string, echo=False)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"[OK] Ket noi thanh cong!")
        print(f"PostgreSQL: {version.split(',')[0]}")
        
        # List databases
        print("\nDanh sach databases:")
        result = conn.execute(text("""
            SELECT datname 
            FROM pg_database 
            WHERE datistemplate = false
            ORDER BY datname
        """))
        databases = [row[0] for row in result]
        
        for db in databases:
            print(f"  - {db}")
        
        # Check trading_bot database
        if "trading_bot" in databases:
            print("\n[OK] Database 'trading_bot' da ton tai!")
            
            # Check tables
            print("\nKiem tra tables trong 'trading_bot'...")
            conn_db = create_engine(
                f"postgresql://{username}:{password}@{host}:{port}/trading_bot",
                echo=False
            ).connect()
            
            result = conn_db.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            if tables:
                print(f"[OK] Co {len(tables)} table(s):")
                for table in tables:
                    print(f"  - {table}")
            else:
                print("[INFO] Chua co table nao")
            conn_db.close()
        else:
            print("\n[INFO] Database 'trading_bot' chua ton tai")
            print("Chay script doi_sang_postgresql_auto.py de tao")
        
except ImportError:
    print("[ERROR] Chua cai dat psycopg2-binary!")
    print("Chay: pip install psycopg2-binary")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Loi: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("HOAN TAT!")
print("="*60)

