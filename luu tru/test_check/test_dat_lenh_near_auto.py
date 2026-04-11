"""
Test dat lenh mua 3 NEAR/USDT Spot gia thi truong (Tự động)
"""
import requests
import json
import sys

# Fix encoding
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

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
        sys.exit(1)
    token = response.json()["access_token"]
    print("[OK] Dang nhap thanh cong!")
except Exception as e:
    print(f"[ERROR] Loi: {e}")
    sys.exit(1)

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
        sys.exit(1)
    
    print(f"[OK] Tim thay config: {near_config['name']} (ID: {near_config['id']})")
    print(f"Symbol: {near_config['symbol']}")
    print(f"Amount: {near_config['amount']}")
    has_api = bool(near_config.get('api_key_encrypted'))
    print(f"Has API: {has_api}")
    
    if not has_api:
        print("\n[WARN] Config chua co API key! Dang them...")
        update_payload = {
            "api_key": "Nk2SufxLinCEYVC98ghNd9sRr3NpdkcgbZgWU1MXn7setQboIlSdDv2gbHmgEWiq",
            "api_secret": "aXUTSRziPY0vZT9q4z6VCddhtxMHDYwDT0Q8pOyJa3igza5bK6HvxjpS4ar4yYD6"
        }
        update_response = requests.put(
            f"{BASE_URL}/api/config/{near_config['id']}",
            headers=headers,
            json=update_payload,
            timeout=10
        )
        if update_response.status_code == 200:
            print("[OK] Da them API key!")
        else:
            print(f"[ERROR] Khong the them API key: {update_response.text}")
            sys.exit(1)
    
except Exception as e:
    print(f"[ERROR] Loi: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

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

try:
    print("Dang dat lenh...")
    response = requests.post(
        f"{BASE_URL}/api/trading/place-order",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    print(f"\nStatus: {response.status_code}")
    result = response.json()
    print(f"\nResponse:\n{json.dumps(result, indent=2, ensure_ascii=False)}")
    
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

