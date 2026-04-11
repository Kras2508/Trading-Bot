"""
Test authentication token
"""
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

print("="*60)
print("TEST AUTHENTICATION TOKEN")
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
    print(f"[OK] Dang nhap thanh cong!")
    print(f"Token: {token[:50]}...")
except Exception as e:
    print(f"[ERROR] Loi: {e}")
    sys.exit(1)

# Test token với config endpoint
print("\nBuoc 2: Test token voi config endpoint...")
try:
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/config/", headers=headers, timeout=5)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("[OK] Token hop le!")
        configs = response.json()
        print(f"Tim thay {len(configs)} config(s)")
    elif response.status_code == 403:
        print("[ERROR] 403 Forbidden - Token khong hop le hoac khong co quyen")
        print(f"Response: {response.text}")
    elif response.status_code == 401:
        print("[ERROR] 401 Unauthorized - Token khong hop le hoac da het han")
        print(f"Response: {response.text}")
    else:
        print(f"[ERROR] Status: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"[ERROR] Loi: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*60)

