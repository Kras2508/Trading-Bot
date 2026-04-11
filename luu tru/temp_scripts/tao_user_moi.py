"""
Tao user moi de dang nhap
"""
import sys
import requests

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

print("="*60)
print("TAO USER MOI")
print("="*60)
print()

# Thong tin user moi
username = "admin"
email = "admin@example.com"
password = "admin123"

print(f"Username: {username}")
print(f"Email: {email}")
print(f"Password: {password}")
print()

# Check if server is running
print("Buoc 1: Kiem tra server...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=2)
    if response.status_code == 200:
        print("[OK] Server dang chay")
    else:
        print("[ERROR] Server khong hoat dong")
        sys.exit(1)
except Exception as e:
    print(f"[ERROR] Khong the ket noi server: {e}")
    print("Vui long chay backend server truoc!")
    sys.exit(1)

# Register user
print(f"\nBuoc 2: Dang ky user '{username}'...")
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password
        },
        timeout=5
    )
    
    if response.status_code == 201:
        print("[OK] Da tao user thanh cong!")
        print(f"\nThong tin dang nhap:")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
    elif response.status_code == 400:
        result = response.json()
        if "already exists" in result.get("detail", "").lower():
            print(f"[WARN] User '{username}' da ton tai")
            print("Dang thu dang nhap...")
            
            # Try login
            login_response = requests.post(
                f"{BASE_URL}/api/auth/login",
                params={"username": username, "password": password},
                timeout=5
            )
            
            if login_response.status_code == 200:
                print("[OK] Dang nhap thanh cong!")
                print(f"\nThong tin dang nhap:")
                print(f"  Username: {username}")
                print(f"  Password: {password}")
            else:
                print(f"[ERROR] Password khong dung")
                print(f"\nBan co the:")
                print(f"1. Dung frontend de tao user moi")
                print(f"2. Hoac reset password trong database")
        else:
            print(f"[ERROR] {result.get('detail')}")
    else:
        print(f"[ERROR] Status: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"[ERROR] Loi: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("HUONG DAN DANG NHAP:")
print("="*60)
print(f"1. Mo frontend: http://localhost:3000")
print(f"2. Nhap:")
print(f"   Username: {username}")
print(f"   Password: {password}")
print(f"3. Click 'Dang nhap'")
print("="*60)

