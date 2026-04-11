"""
Script tạo user admin đầu tiên
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("="*60)
print("Tạo User Admin Đầu Tiên")
print("="*60)
print()

username = input("Nhập username: ").strip()
email = input("Nhập email: ").strip()
password = input("Nhập password: ").strip()

if not username or not email or not password:
    print("❌ Vui lòng nhập đầy đủ thông tin!")
    exit(1)

data = {
    "username": username,
    "email": email,
    "password": password,
    "is_admin": True
}

try:
    response = requests.post(f"{BASE_URL}/api/auth/register", json=data, timeout=5)
    
    if response.status_code == 201:
        user = response.json()
        print(f"\n✅ Tạo user thành công!")
        print(f"ID: {user['id']}")
        print(f"Username: {user['username']}")
        print(f"Email: {user['email']}")
        print(f"Admin: {user['is_admin']}")
        print()
        print("Bây giờ bạn có thể đăng nhập với username và password này.")
    elif response.status_code == 400:
        print(f"\n⚠️  User đã tồn tại: {response.json()}")
    else:
        print(f"\n❌ Lỗi: {response.json()}")
except Exception as e:
    print(f"\n❌ Lỗi kết nối: {e}")
    print("Đảm bảo server đang chạy tại http://127.0.0.1:8000")

