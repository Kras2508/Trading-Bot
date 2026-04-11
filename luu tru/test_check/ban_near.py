"""
Ban NEAR/USDT Spot gia thi truong
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

print("="*60)
print("BAN NEAR/USDT Spot - Gia thi truong")
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

# Kiem tra so du NEAR
print("\nBuoc 2: Kiem tra so du NEAR...")
try:
    from app.database import SessionLocal
    from app.models.bot_config import BotConfig
    from app.core.security import decrypt_data
    import ccxt
    
    db = SessionLocal()
    config_db = db.query(BotConfig).filter(BotConfig.id == 2).first()
    
    if not config_db or not config_db.api_key_encrypted:
        print("[ERROR] Config khong co API key!")
        sys.exit(1)
    
    api_key = decrypt_data(config_db.api_key_encrypted)
    api_secret = decrypt_data(config_db.api_secret_encrypted)
    
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'adjustForTimeDifference': True,
            'defaultType': 'spot'
        }
    })
    
    balance = exchange.fetch_balance()
    near_free = balance['free'].get('NEAR', 0)
    
    ticker = exchange.fetch_ticker('NEAR/USDT')
    current_price = ticker['last']
    
    print(f"So du NEAR: {near_free}")
    print(f"Gia NEAR hien tai: {current_price} USDT")
    
    if near_free < 0.1:
        print(f"\n[ERROR] Khong du NEAR de ban!")
        print(f"Can it nhat: 0.1 NEAR")
        sys.exit(1)
    
    # Ban toan bo hoac 5 NEAR (neu co)
    amount_to_sell = min(5.0, near_free * 0.99)  # 99% de tranh loi lam tron
    
    print(f"\nSo luong co the ban: {near_free} NEAR")
    print(f"Se ban: {amount_to_sell:.4f} NEAR")
    print(f"Gia tri uoc tinh: {amount_to_sell * current_price:.2f} USDT")
    
except Exception as e:
    print(f"[ERROR] Loi: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Ban NEAR
print(f"\nBuoc 3: Ban {amount_to_sell:.4f} NEAR/USDT...")
print("[WARN] Day la lenh THAT tren Binance!")
print()

payload = {
    "bot_config_id": 2,
    "side": "sell",
    "amount": round(amount_to_sell, 4),
    "order_type": "market"
}

print(f"Payload: {json.dumps(payload, indent=2)}")
print()

try:
    print("Dang dat lenh ban...")
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
        print("[SUCCESS] Ban NEAR thanh cong!")
        print("="*60)
        print(f"Order ID: {result.get('order_id')}")
        print(f"Exchange Order ID: {result.get('exchange_order_id')}")
        print(f"Symbol: {result.get('symbol')}")
        print(f"Side: {result.get('side')}")
        print(f"Amount: {result.get('amount')} NEAR")
        print(f"Price: {result.get('filled_price') or result.get('price')} USDT")
        print(f"Total Value: {(result.get('filled_price') or result.get('price') or 0) * result.get('amount', 0):.2f} USDT")
        print("\n[OK] Lenh ban da duoc dat thanh cong tren Binance!")
    else:
        print("\n" + "="*60)
        print("[ERROR] Ban NEAR that bai!")
        print("="*60)
        print(f"Error: {result.get('detail')}")
        
except Exception as e:
    print(f"\n[ERROR] Loi: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*60)

