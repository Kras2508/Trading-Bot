"""
Script tu dong copy toan bo du lieu tu SQL Server sang PostgreSQL
"""
import sys
import os
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("="*60)
print("MIGRATE DU LIEU TU SQL SERVER SANG POSTGRESQL (TU DONG)")
print("="*60)
print()

# Thong tin SQL Server (nguon) - MAC DINH
sql_server = "localhost"  # Da test thanh cong
sql_database = "BackendAPI_Trading"
use_windows_auth = True

# Thong tin PostgreSQL (dich) - MAC DINH
pg_host = "localhost"
pg_port = 5432
pg_username = "postgres"
pg_password = "1"
pg_database = "trading_bot"

print("=== THONG TIN SQL SERVER (NGUON) ===")
print(f"Server: {sql_server}")
print(f"Database: {sql_database}")
print(f"Authentication: Windows Authentication")
print()

print("=== THONG TIN POSTGRESQL (DICH) ===")
print(f"Host: {pg_host}")
print(f"Port: {pg_port}")
print(f"Database: {pg_database}")
print(f"Username: {pg_username}")
print(f"Password: {'*' * len(pg_password)}")
print()

# Connection strings
if use_windows_auth:
    sql_server_url = f"mssql+pyodbc://{sql_server}/{sql_database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
else:
    sql_user = "sa"
    sql_pass = "your_password"
    sql_server_url = f"mssql+pyodbc://{sql_user}:{sql_pass}@{sql_server}/{sql_database}?driver=ODBC+Driver+17+for+SQL+Server"

postgresql_url = f"postgresql://{pg_username}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"

print("="*60)
print("THONG TIN KET NOI")
print("="*60)
print(f"SQL Server: {sql_server_url.replace('trusted_connection=yes', '***')}")
print(f"PostgreSQL: postgresql://{pg_username}:***@{pg_host}:{pg_port}/{pg_database}")
print()

# Test connections
print("Buoc 1: Test ket noi...")
try:
    from sqlalchemy import create_engine, text, inspect
    
    # Test SQL Server
    print("  - Ket noi SQL Server...")
    engine_sql = create_engine(sql_server_url, echo=False)
    with engine_sql.connect() as conn:
        result = conn.execute(text("SELECT @@VERSION"))
        version = result.scalar()
        print(f"    [OK] SQL Server: {version[:50]}...")
    
    # Test PostgreSQL
    print("  - Ket noi PostgreSQL...")
    engine_pg = create_engine(postgresql_url, echo=False)
    with engine_pg.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"    [OK] PostgreSQL: {version[:50]}...")
        
except Exception as e:
    print(f"[ERROR] Loi ket noi: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Get table list
print("\nBuoc 2: Lay danh sach tables...")
inspector_sql = inspect(engine_sql)
inspector_pg = inspect(engine_pg)

tables_sql = inspector_sql.get_table_names()
tables_pg = inspector_pg.get_table_names()

print(f"  SQL Server: {len(tables_sql)} tables")
for table in tables_sql:
    print(f"    - {table}")

print(f"  PostgreSQL: {len(tables_pg)} tables")
for table in tables_pg:
    print(f"    - {table}")

# Tables to migrate (in order due to foreign keys)
tables_order = ['users', 'bot_configs', 'bot_status', 'orders', 'activity_logs']

print("\nBuoc 3: Bat dau migrate du lieu...")
print("="*60)

total_records = 0

for table_name in tables_order:
    if table_name not in tables_sql:
        print(f"\n[{table_name}] Khong ton tai trong SQL Server, bo qua...")
        continue
    
    if table_name not in tables_pg:
        print(f"\n[{table_name}] Khong ton tai trong PostgreSQL, bo qua...")
        continue
    
    print(f"\n[{table_name}] Dang migrate...")
    
    try:
        # Get data from SQL Server
        with engine_sql.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {table_name}"))
            rows = result.fetchall()
            columns = result.keys()
        
        if not rows:
            print(f"  [INFO] Khong co du lieu")
            continue
        
        print(f"  [INFO] Tim thay {len(rows)} records")
        
        # Clear existing data in PostgreSQL (optional - comment out if you want to keep existing)
        with engine_pg.connect() as conn:
            conn.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))
            conn.commit()
        print(f"  [INFO] Da xoa du lieu cu trong PostgreSQL")
        
        # Insert data into PostgreSQL using bulk insert (FAST)
        print(f"  [INFO] Dang insert {len(rows)} records (bulk mode)...")
        
        inserted = 0
        skipped = 0
        errors = 0
        
        # Prepare data for bulk insert
        rows_data = []
        for row in rows:
            row_dict = {}
            for col, val in zip(columns, row):
                if val is None:
                    row_dict[col] = None
                elif isinstance(val, datetime):
                    row_dict[col] = val
                else:
                    row_dict[col] = val
            rows_data.append(row_dict)
        
        # Bulk insert using executemany (much faster)
        try:
            with engine_pg.connect() as conn:
                columns_str = ', '.join([f'"{col}"' for col in columns])
                placeholders = ', '.join([f':{col}' for col in columns])
                insert_sql = f'INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})'
                
                # Use executemany for bulk insert
                conn.execute(text(insert_sql), rows_data)
                conn.commit()
                inserted = len(rows_data)
                print(f"  [OK] Da insert {inserted} records (bulk insert)")
                
        except Exception as e:
            # If bulk insert fails, try one by one
            error_msg = str(e).lower()
            print(f"  [WARN] Bulk insert that bai, dang insert tung record...")
            
            with engine_pg.connect() as conn:
                columns_str = ', '.join([f'"{col}"' for col in columns])
                placeholders = ', '.join([f':{col}' for col in columns])
                insert_sql = f'INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})'
                
                for idx, row_dict in enumerate(rows_data, 1):
                    try:
                        conn.execute(text(insert_sql), row_dict)
                        conn.commit()
                        inserted += 1
                        
                        if inserted % 100 == 0:
                            print(f"    [INFO] Da insert {inserted}/{len(rows)} records...")
                        
                    except Exception as e2:
                        error_msg2 = str(e2).lower()
                        if 'duplicate' in error_msg2 or 'unique' in error_msg2 or 'violates unique constraint' in error_msg2:
                            skipped += 1
                            conn.rollback()
                        elif 'foreign key' in error_msg2 or 'violates foreign key' in error_msg2:
                            errors += 1
                            conn.rollback()
                            if errors <= 3:
                                print(f"    [WARN] Foreign key error (record {idx}): {str(e2)[:100]}")
                        else:
                            errors += 1
                            conn.rollback()
                            if errors <= 3:
                                print(f"    [ERROR] Loi khi insert record {idx}: {str(e2)[:100]}")
            
            print(f"  [OK] Da insert {inserted} records")
            if skipped > 0:
                print(f"  [INFO] Da bo qua {skipped} records (trung lap)")
            if errors > 0:
                print(f"  [WARN] Co {errors} records bi loi")
        
        total_records += inserted
        
    except Exception as e:
        print(f"  [ERROR] Loi khi migrate {table_name}: {e}")
        import traceback
        traceback.print_exc()
        print(f"  [WARN] Tiep tuc voi table tiep theo...")

print("\n" + "="*60)
print("HOAN TAT MIGRATION!")
print("="*60)
print(f"Tong so records da migrate: {total_records}")
print("="*60)
print("\nVui long restart server de ap dung thay doi")

