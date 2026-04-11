"""
Test dat lenh mua 5 NEAR/USDT (Don gian)
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

print("="*60)
print("TEST DAT LENH: Mua 5 NEAR/USDT")
print("="*60)
print()

# Login
print("Dang nhap...")
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
    print("[INFO] Kiem tra server da chay chua?")
    sys.exit(1)

headers = {"Authorization": f"Bearer {token}"}

# Dat lenh truc tiep voi config ID 2 (NEAR)
print("\nDat lenh mua 5 NEAR/USDT...")
print("[WARN] Day la lenh THAT tren Binance!")
print()

payload = {
    "bot_config_id": 2,  # NEAR config
    "side": "buy",
    "amount": 5.0,
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
    
    print(f"Status: {response.status_code}")
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

