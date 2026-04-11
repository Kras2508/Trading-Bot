"""
Test dat lenh mua NEAR/USDT Spot (So luong phu hop voi so du)
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

print("="*60)
print("TEST DAT LENH: Mua NEAR/USDT Spot - Gia thi truong")
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

# Dat lenh
print("\nBuoc 2: Dat lenh mua NEAR/USDT...")
print("[INFO] So du hien co: ~3.52 USDT")
print("[INFO] Gia NEAR: ~1.885 USDT")
print("[INFO] Co the mua: ~1.5 NEAR")
print()

# Test với 1.5 NEAR (an toàn hơn)
amount = 1.5

payload = {
    "bot_config_id": 2,  # NEAR config
    "side": "buy",
    "amount": amount,
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
        print(f"Amount: {result.get('amount')} NEAR")
        print(f"Price: {result.get('filled_price') or result.get('price')} USDT")
        print(f"Total Cost: {(result.get('filled_price') or result.get('price') or 0) * amount:.2f} USDT")
        print(f"Stop Loss: {result.get('stop_loss')} USDT")
        print(f"Take Profit: {result.get('take_profit')} USDT")
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

