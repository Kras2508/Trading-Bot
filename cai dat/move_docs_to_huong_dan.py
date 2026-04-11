"""
Script di chuyển các file hướng dẫn vào thư mục huong dan
"""
import os
import shutil
import sys
import glob

sys.stdout.reconfigure(encoding='utf-8')

# Thư mục đích
target_dir = "huong dan"

# Tạo thư mục nếu chưa có
if not os.path.exists(target_dir):
    os.makedirs(target_dir)
    print(f"[OK] Da tao thu muc: {target_dir}")

print("="*60)
print("DI CHUYEN CAC FILE HUONG DAN")
print("="*60)
print()

# Tìm tất cả các file .md trong thư mục gốc
md_files = glob.glob("*.md")
txt_files = glob.glob("*.txt")

# Loại bỏ các file đã được di chuyển vào luu tru
excluded_files = set()
if os.path.exists("luu tru/old_docs"):
    for root, dirs, files in os.walk("luu tru/old_docs"):
        for file in files:
            excluded_files.add(file)

# Lọc các file cần di chuyển
files_to_move = []
for file in md_files + txt_files:
    if os.path.basename(file) not in excluded_files and os.path.isfile(file):
        files_to_move.append(file)

if not files_to_move:
    print("[INFO] Khong co file nao de di chuyển")
    sys.exit(0)

print(f"Tim thay {len(files_to_move)} file(s) de di chuyển:\n")
for f in sorted(files_to_move):
    print(f"  - {f}")
print()

# Move files
moved = 0
errors = 0

for file in files_to_move:
    try:
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

print("\n" + "="*60)
print("HOAN TAT!")
print("="*60)
print(f"Da di chuyển: {moved} file(s)")
if errors > 0:
    print(f"Loi: {errors} file(s)")
print(f"Thu muc: {target_dir}/")
print("="*60)

