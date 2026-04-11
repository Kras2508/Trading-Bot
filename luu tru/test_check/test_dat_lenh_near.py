"""
Test dat lenh mua 3 NEAR/USDT Spot gia thi truong
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

print("="*60)
print("TEST DAT LENH: Mua 3 NEAR/USDT Spot - Gia thi truong")
print("="*60)
print()

# Login
print("Buoc 1: Dang nhap...")
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        params={"username": "testuser", "password": "testpass123"},
        timeout=5
    )
    if response.status_code != 200:
        print(f"[ERROR] Dang nhap that bai: {response.json()}")
        exit(1)
    token = response.json()["access_token"]
    print("[OK] Dang nhap thanh cong!")
except Exception as e:
    print(f"[ERROR] Loi: {e}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# Lay config NEAR
print("\nBuoc 2: Lay config NEAR...")
try:
    response = requests.get(f"{BASE_URL}/api/config/", headers=headers, timeout=5)
    configs = response.json()
    
    near_config = None
    for config in configs:
        if "NEAR" in config['symbol'].upper():
            near_config = config
            break
    
    if not near_config:
        print("[ERROR] Khong tim thay config NEAR!")
        exit(1)
    
    print(f"[OK] Tim thay config: {near_config['name']} (ID: {near_config['id']})")
    print(f"Symbol: {near_config['symbol']}")
    print(f"Amount: {near_config['amount']}")
    print(f"Has API: {bool(near_config.get('api_key_encrypted'))}")
    
except Exception as e:
    print(f"[ERROR] Loi: {e}")
    exit(1)

# Dat lenh
print("\nBuoc 3: Dat lenh mua 3 NEAR/USDT...")
print("[WARN] Day la lenh THAT tren Binance!")
print()

payload = {
    "bot_config_id": near_config['id'],
    "side": "buy",
    "amount": 3.0,
    "order_type": "market"
}

print(f"Payload: {json.dumps(payload, indent=2)}")
print()

confirm = input("[WARN] Xac nhan dat lenh THAT? (yes/no): ")
if confirm.lower() != "yes":
    print("Da huy.")
    exit(0)

try:
    print("\nDang dat lenh...")
    response = requests.post(
        f"{BASE_URL}/api/trading/place-order",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    print(f"\nStatus: {response.status_code}")
    result = response.json()
    print(f"\nResponse:\n{json.dumps(result, indent=2)}")
    
    if response.status_code == 200:
        print("\n" + "="*60)
        print("[SUCCESS] Dat lenh thanh cong!")
        print("="*60)
        print(f"Order ID: {result.get('order_id')}")
        print(f"Exchange Order ID: {result.get('exchange_order_id')}")
        print(f"Symbol: {result.get('symbol')}")
        print(f"Side: {result.get('side')}")
        print(f"Amount: {result.get('amount')}")
        print(f"Price: {result.get('filled_price') or result.get('price')}")
        print(f"Stop Loss: {result.get('stop_loss')}")
        print(f"Take Profit: {result.get('take_profit')}")
        print(f"Status: {result.get('order_status')}")
        print("\n[OK] Lenh da duoc dat thanh cong tren Binance!")
    else:
        print("\n" + "="*60)
        print("[ERROR] Dat lenh that bai!")
        print("="*60)
        print(f"Error: {result.get('detail')}")
        
except Exception as e:
    print(f"\n[ERROR] Loi: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*60)

