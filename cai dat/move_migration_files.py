"""
Script di chuyển các file migration vào thư mục migrate
"""
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Thư mục đích
target_dir = "migrate"
source_dir = "luu tru/migration"

# Tạo thư mục nếu chưa có
if not os.path.exists(target_dir):
    os.makedirs(target_dir)
    print(f"[OK] Da tao thu muc: {target_dir}")

print("="*60)
print("DI CHUYEN CAC FILE MIGRATION")
print("="*60)
print()

# Kiểm tra thư mục nguồn
if not os.path.exists(source_dir):
    print(f"[INFO] Khong tim thay thu muc: {source_dir}")
    print("[INFO] Co the cac file da duoc di chuyển hoac chua co")
    sys.exit(0)

# Lấy danh sách file trong thư mục migration
files_to_move = []
if os.path.exists(source_dir):
    for file in os.listdir(source_dir):
        file_path = os.path.join(source_dir, file)
        if os.path.isfile(file_path):
            files_to_move.append(file_path)

if not files_to_move:
    print("[INFO] Khong co file nao de di chuyển")
    sys.exit(0)

print(f"Tim thay {len(files_to_move)} file(s) trong {source_dir}:\n")
for f in sorted(files_to_move):
    print(f"  - {os.path.basename(f)}")
print()

# Move files
moved = 0
errors = 0

for file_path in files_to_move:
    try:
        file_name = os.path.basename(file_path)
        target_path = os.path.join(target_dir, file_name)
        
        # Move file
        shutil.move(file_path, target_path)
        print(f"[OK] {file_name} -> {target_path}")
        moved += 1
        
    except Exception as e:
        print(f"[ERROR] Khong the di chuyển {file_name}: {e}")
        errors += 1

# Xóa thư mục migration nếu rỗng
try:
    if os.path.exists(source_dir) and not os.listdir(source_dir):
        os.rmdir(source_dir)
        print(f"\n[OK] Da xoa thu muc rong: {source_dir}")
except:
    pass

print("\n" + "="*60)
print("HOAN TAT!")
print("="*60)
print(f"Da di chuyển: {moved} file(s)")
if errors > 0:
    print(f"Loi: {errors} file(s)")
print(f"Thu muc: {target_dir}/")
print("="*60)

