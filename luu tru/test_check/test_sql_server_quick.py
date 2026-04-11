"""
Test ket noi SQL Server nhanh
"""
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("TEST KET NOI SQL SERVER")
print("="*60)
print()

# Cac ten server thuong gap
servers_to_try = [
    "DESKTOP-MDT6RKU\\TGC",
    "localhost",
    "localhost\\SQLEXPRESS",
    ".\\SQLEXPRESS",
    "(local)",
    "(local)\\SQLEXPRESS"
]

database = "BackendAPI_Trading"

print(f"Database: {database}")
print("\nDang thu ket noi voi cac server...")
print()

connected = False

for server in servers_to_try:
    print(f"Thu: {server}...", end=" ")
    try:
        from sqlalchemy import create_engine, text
        
        sql_url = f"mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
        engine = create_engine(sql_url, echo=False, connect_args={"timeout": 5})
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT @@VERSION"))
            version = result.scalar()
            print(f"[OK] Ket noi thanh cong!")
            print(f"     SQL Server: {version[:80]}...")
            
            # Count tables
            result = conn.execute(text("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
            """))
            table_count = result.scalar()
            print(f"     Tables: {table_count}")
            
            # List tables
            result = conn.execute(text("""
                SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """))
            tables = [row[0] for row in result]
            print(f"     Danh sach: {', '.join(tables)}")
            
            connected = True
            print("\n" + "="*60)
            print("KET NOI THANH CONG!")
            print("="*60)
            print(f"Server: {server}")
            print(f"Database: {database}")
            print("\nBan co the chay migrate voi server nay!")
            break
            
    except Exception as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower() or "not found" in error_msg.lower():
            print("[FAIL] Khong tim thay server")
        else:
            print(f"[FAIL] {error_msg[:60]}...")

if not connected:
    print("\n" + "="*60)
    print("KHONG KET NOI DUOC!")
    print("="*60)
    print("\nKiem tra:")
    print("1. SQL Server da chay chua? (SQL Server Configuration Manager)")
    print("2. SQL Server Browser service da chay chua?")
    print("3. Ten server/instance co dung khong?")
    print("\nBan co the:")
    print("- Chay SQL Server Management Studio (SSMS) de xem ten server chinh xac")
    print("- Hoac chay: sqlcmd -L (de xem danh sach SQL Server instances)")

