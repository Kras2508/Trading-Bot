"""
Kiem tra ket noi SQL Server
"""
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("KIEM TRA KET NOI SQL SERVER")
print("="*60)
print()

# Thong tin SQL Server
sql_server = input("SQL Server (e.g., DESKTOP-MDT6RKU\\TGC hoac localhost) [DESKTOP-MDT6RKU\\TGC]: ").strip()
if not sql_server:
    sql_server = "DESKTOP-MDT6RKU\\TGC"

sql_database = input("Database [BackendAPI_Trading]: ").strip()
if not sql_database:
    sql_database = "BackendAPI_Trading"

print()
print(f"Server: {sql_server}")
print(f"Database: {sql_database}")
print()

# Test connection
sql_server_url = f"mssql+pyodbc://{sql_server}/{sql_database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"

print("Dang test ket noi...")
try:
    from sqlalchemy import create_engine, text, inspect
    
    engine = create_engine(sql_server_url, echo=False)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT @@VERSION"))
        version = result.scalar()
        print(f"[OK] Ket noi thanh cong!")
        print(f"SQL Server: {version[:100]}...")
        
        # List tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\n[OK] Tim thay {len(tables)} tables:")
        for table in tables:
            # Count records
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"  - {table}: {count} records")
        
        print("\n" + "="*60)
        print("KET NOI THANH CONG!")
        print("="*60)
        print(f"\nBan co the chay script migrate:")
        print("python migrate_sqlserver_to_postgresql_auto.py")
        print("\nHoac cap nhat thong tin SQL Server trong script:")
        print(f"  sql_server = \"{sql_server}\"")
        print(f"  sql_database = \"{sql_database}\"")
        
except ImportError:
    print("[ERROR] Chua cai dat pyodbc!")
    print("Chay: pip install pyodbc")
except Exception as e:
    print(f"[ERROR] Khong the ket noi: {e}")
    print("\nKiem tra:")
    print("1. SQL Server da chay chua?")
    print("2. Ten server/instance co dung khong?")
    print("3. Database co ton tai khong?")
    print("4. Co quyen truy cap khong?")
    print("\nThu cac ten server khac:")
    print("  - localhost")
    print("  - localhost\\SQLEXPRESS")
    print("  - .\\SQLEXPRESS")
    print("  - (local)")

