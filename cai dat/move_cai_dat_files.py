"""
Script di chuyển các file cài đặt vào thư mục cai dat
"""
import os
import shutil
import sys
import glob

sys.stdout.reconfigure(encoding='utf-8')

# Thư mục đích
target_dir = "cai dat"

# Tạo thư mục nếu chưa có
if not os.path.exists(target_dir):
    os.makedirs(target_dir)
    print(f"[OK] Da tao thu muc: {target_dir}")

print("="*60)
print("DI CHUYEN CAC FILE CAI DAT")
print("="*60)
print()

# Danh sách file cài đặt cần di chuyển
files_to_move = [
    # Batch files cài đặt
    "CAI_DAT.bat",
    "TAO_VENV_VA_CAI_DAT.bat",
    "CAI_DAT_MAY_MOI.bat",
    
    # Scripts cài đặt
    "move_docs_to_huong_dan.py",
    "move_migration_files.py",
    "move_unused_files.py",
    "move_unused_files_auto.py",
    "move_cai_dat_files.py",  # File này cũng sẽ tự di chuyển
]

# Tìm các file thực sự tồn tại
existing_files = []
for file in files_to_move:
    if os.path.isfile(file):
        existing_files.append(file)

if not existing_files:
    print("[INFO] Khong co file nao de di chuyển")
    sys.exit(0)

print(f"Tim thay {len(existing_files)} file(s) de di chuyển:\n")
for f in sorted(existing_files):
    print(f"  - {f}")
print()

# Move files
moved = 0
errors = 0

for file in existing_files:
    try:
        # Không di chuyển file đang chạy
        if file == "move_cai_dat_files.py":
            continue
            
        target_path = os.path.join(target_dir, os.path.basename(file))
        
        # Nếu file đã tồn tại trong thư mục đích, thêm số vào tên
        if os.path.exists(target_path):
            base, ext = os.path.splitext(os.path.basename(file))
            counter = 1
            while os.path.exists(target_path):
                target_path = os.path.join(target_dir, f"{base}_{counter}{ext}")
                counter += 1
        
        # Move file
        shutil.move(file, target_path)
        print(f"[OK] {file} -> {target_path}")
        moved += 1
        
    except Exception as e:
        print(f"[ERROR] Khong the di chuyển {file}: {e}")
        errors += 1

# Di chuyển file này cuối cùng
try:
    if os.path.exists("move_cai_dat_files.py"):
        target_path = os.path.join(target_dir, "move_cai_dat_files.py")
        shutil.move("move_cai_dat_files.py", target_path)
        print(f"[OK] move_cai_dat_files.py -> {target_path}")
        moved += 1
except Exception as e:
    print(f"[ERROR] Khong the di chuyển move_cai_dat_files.py: {e}")
    errors += 1

print("\n" + "="*60)
print("HOAN TAT!")
print("="*60)
print(f"Da di chuyển: {moved} file(s)")
if errors > 0:
    print(f"Loi: {errors} file(s)")
print(f"Thu muc: {target_dir}/")
print("="*60)

