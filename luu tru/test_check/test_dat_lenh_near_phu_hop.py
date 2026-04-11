"""
Test dat lenh mua NEAR/USDT voi so luong phu hop so du
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

print("="*60)
print("TEST DAT LENH: Mua NEAR/USDT (So luong phu hop)")
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
    sys.exit(1)

headers = {"Authorization": f"Bearer {token}"}

# Kiem tra so du va tinh so luong co the mua
print("\nKiem tra so du...")
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
    usdt_free = balance['free'].get('USDT', 0)
    
    ticker = exchange.fetch_ticker('NEAR/USDT')
    current_price = ticker['last']
    
    print(f"So du USDT: {usdt_free}")
    print(f"Gia NEAR: {current_price} USDT")
    
    # Tinh so luong co the mua (95% so du de an toan)
    max_amount = (usdt_free * 0.95) / current_price
    test_amount = min(2.5, max_amount)  # Test voi 2.5 NEAR hoac so luong toi da
    
    print(f"\nCo the mua toi da: {max_amount:.2f} NEAR")
    print(f"Test voi: {test_amount:.2f} NEAR")
    print(f"Chi phi uoc tinh: {test_amount * current_price:.2f} USDT")
    
except Exception as e:
    print(f"[WARN] Khong the kiem tra so du: {e}")
    test_amount = 2.5  # Default
    print(f"[INFO] Su dung so luong mac dinh: {test_amount} NEAR")

# Dat lenh
print(f"\nDat lenh mua {test_amount:.2f} NEAR/USDT...")
print("[WARN] Day la lenh THAT tren Binance!")
print()

payload = {
    "bot_config_id": 2,
    "side": "buy",
    "amount": round(test_amount, 2),
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
        print(f"Total Cost: {(result.get('filled_price') or result.get('price') or 0) * result.get('amount', 0):.2f} USDT")
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

