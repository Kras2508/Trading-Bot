"""
Script tu dong di chuyển các file không sử dụng vào thư mục luu tru
"""
import os
import shutil
import sys
import glob

sys.stdout.reconfigure(encoding='utf-8')

# Thư mục đích
target_dir = "luu tru"

# Tạo thư mục nếu chưa có
if not os.path.exists(target_dir):
    os.makedirs(target_dir)
    print(f"[OK] Da tao thu muc: {target_dir}")

print("="*60)
print("DI CHUYEN CAC FILE KHONG SU DUNG (TU DONG)")
print("="*60)
print()

# Danh sách file cần di chuyển
files_to_move = {
    # Migration scripts (đã migrate xong)
    "migration": [
        "migrate_sqlite_to_sqlserver.py",
        "migrate_sqlite_to_sqlserver_auto.py",
        "migrate_sqlserver_to_postgresql.py",
        "migrate_sqlserver_to_postgresql_auto.py",
        "doi_sang_sql_server.py",
        "doi_sang_sql_server_auto.py",
        "doi_sang_postgresql_auto.py",
        "migrate_add_ip_whitelist.py",
        "MIGRATE_AUTO.bat",
        "MIGRATE_SQLSERVER_TO_POSTGRESQL.bat",
        "DOI_SANG_POSTGRESQL.bat",
    ],
    
    # Test/Check scripts (đã test xong)
    "test_check": [
        "test_*.py",
        "kiem_tra_*.py",
        "check_db.py",
        "ban_near.py",
    ],
    
    # Old batch files (nhiều biến thể, không dùng nữa)
    "old_batch": [
        "CHAY_NGROK*.bat",
        "CHAY_FRONTEND_NGROK.bat",
        "CHAY_BACKEND_NGROK.bat",
        "RESTART_NGROK.bat",
        "KILL_ALL_NGROK.bat",
        "KIEM_TRA_NGROK.bat",
        "LAY_URL_NGROK.bat",
        "CAI_DAT_NGROK*.bat",
        "FIX_NGROK_*.bat",
        "CHAY_NGAY.bat",
        "CHAY_CUOI_CUNG.bat",
        "CHAY_SERVER_FINAL.bat",
        "CHAY_TRUC_TIEP.bat",
        "CHAY_VENV.bat",
        "RESTART_AND_TEST.bat",
        "RESTART_SERVER.bat",
        "RESTART_FRONTEND.bat",
        "RESTART_FRONTEND_FORCE.bat",
        "RESTART_BACKEND_NAT.bat",
        "KIEM_TRA_NAT.bat",
        "KIEM_TRA_VA_CHAY_LAI.bat",
        "MO_PORT_*.bat",
        "FIX_PORT_8000.bat",
        "SYNC_THOI_GIAN*.bat",
        "KIEM_TRA_THOI_GIAN.bat",
        "KIEM_TRA_POSTGRESQL.bat",
        "GIAI_PHAP_*.bat",
        "BAT_DAU_NHANH.bat",
        "DI_CHUYEN_DU_AN.bat",
        "CURL_DAT_LENH_*.bat",
        "DAT_LENH_CURL.bat",
        "THEM_API_KEY_NHANH.bat",
        "TEST_API.bat",
        "install.bat",
        "setup_and_run.bat",
        "run.bat",
    ],
    
    # Scripts tạm thời
    "temp_scripts": [
        "xoa_tat_ca_bot_config.py",
        "xoa_tat_ca_bot_config_auto.py",
        "XOA_TAT_CA_BOT_CONFIG.bat",
        "THEM_API_KEY_*.py",
        "tao_user_moi.py",
        "TAO_USER_ADMIN.py",
    ],
    
    # Documentation cũ (nhiều file trùng lặp)
    "old_docs": [
        "HUONG_DAN_NGROK*.md",
        "HUONG_DAN_CAI_NGROK*.md",
        "CAU_LENH_NGROK.md",
        "BO_QUA_NGROK_WARNING.md",
        "HUONG_DAN_BO_QUA_WARNING.md",
        "FIX_NGROK_ERROR.md",
        "HUONG_DAN_NAT_*.md",
        "CAU_HINH_NAT_*.md",
        "HUONG_DAN_EXPOSE_NAT.md",
        "HUONG_DAN_TRUY_CAP_TU_BEN_NGOAI.md",
        "HUONG_DAN_FIX_*.md",
        "FIX_*.md",
        "KIEM_TRA_PORT_8000.md",
        "HUONG_DAN_DOI_SQL_SERVER.md",
        "HUONG_DAN_DAT_LENH_CURL.md",
        "CURL_DAT_LENH_SIMPLE.md",
        "HUONG_DAN_DIEN_THONG_TIN_DAT_LENH.md",
        "HUONG_DAN_DAT_LENH_TRUC_TIEP.md",
        "API_DAT_LENH_BINANCE.md",
        "API_DAT_LENH.md",
        "THEM_API_KEY_QUA_SWAGGER.md",
        "HUONG_DAN_THEM_EXCHANGE.md",
        "KET_QUA_TEST.md",
        "HUONG_DAN_SUA_LOI_PYTHON.md",
        "FIX_PYTHON_ERROR.md",
        "README_FIX_PYTHON.txt",
    ],
    
    # PowerShell scripts (nếu không dùng)
    "powershell": [
        "DAT_LENH_AUTO.ps1",
        "FIX_AND_RUN.ps1",
        "FIX_PYTHON_FINAL.ps1",
        "LAY_NGROK_URL.ps1",
        "LAY_NGROK_URL_NHANH.ps1",
    ],
    
    # Other files
    "other": [
        "trading_bot.db",  # SQLite database (đã chuyển sang PostgreSQL)
        "Thanhdt.txt",
        "THONG_TIN_NAT.txt",
        "VI_DU_DAT_LENH.json",
    ],
}

# Flatten list và lọc các file thực sự tồn tại
all_files = []
for category, files in files_to_move.items():
    for file_pattern in files:
        # Handle wildcards
        if '*' in file_pattern:
            matched = glob.glob(file_pattern)
            all_files.extend([(f, category) for f in matched if os.path.isfile(f)])
        else:
            if os.path.isfile(file_pattern):
                all_files.append((file_pattern, category))

# Remove duplicates
all_files = list(set(all_files))

if not all_files:
    print("[INFO] Khong co file nao de di chuyển")
    sys.exit(0)

print(f"Tim thay {len(all_files)} file(s) de di chuyển\n")

# Move files
moved = 0
errors = 0

for file, category in all_files:
    try:
        # Create subdirectory by category
        target_subdir = os.path.join(target_dir, category)
        if not os.path.exists(target_subdir):
            os.makedirs(target_subdir)
        
        target_path = os.path.join(target_subdir, os.path.basename(file))
        
        # Move file
        shutil.move(file, target_path)
        print(f"[OK] {file} -> {target_path}")
        moved += 1
        
    except Exception as e:
        print(f"[ERROR] Khong the di chuyển {file}: {e}")
        errors += 1

print("\n" + "="*60)
print("HOAN TAT!")
print("="*60)
print(f"Da di chuyển: {moved} file(s)")
if errors > 0:
    print(f"Loi: {errors} file(s)")
print(f"Thu muc: {target_dir}/")
print("="*60)

