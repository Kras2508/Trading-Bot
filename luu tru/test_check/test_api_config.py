"""
Test API config endpoint
"""
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

print("="*60)
print("TEST API CONFIG ENDPOINT")
print("="*60)
print()

# Login
print("Buoc 1: Dang nhap...")
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        params={"username": "admin", "password": "admin123"},
        timeout=5
    )
    if response.status_code != 200:
        print(f"[ERROR] Dang nhap that bai: {response.json()}")
        sys.exit(1)
    token = response.json()["access_token"]
    print("[OK] Dang nhap thanh cong!")
except Exception as e:
    print(f"[ERROR] Loi: {e}")
    sys.exit(1)

# Get configs
print("\nBuoc 2: Lay danh sach configs...")
try:
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/config/", headers=headers, timeout=5)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        configs = response.json()
        print(f"[OK] Tim thay {len(configs)} config(s)")
        for config in configs:
            print(f"  - ID: {config.get('id')}, Name: {config.get('name')}, Symbol: {config.get('symbol')}, Active: {config.get('is_active')}")
    else:
        print(f"[ERROR] Response: {response.text}")
        
except Exception as e:
    print(f"[ERROR] Loi: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*60)

