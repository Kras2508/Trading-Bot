"""
Test dat lenh mua 5 NEAR/USDT Spot gia thi truong
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

print("="*60)
print("TEST DAT LENH: Mua 5 NEAR/USDT Spot - Gia thi truong")
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
    if response.status_code != 200:
        print(f"[ERROR] Khong the lay configs: {response.json()}")
        sys.exit(1)
    
    configs = response.json()
    if not isinstance(configs, list):
        print(f"[ERROR] Response khong phai list: {type(configs)}")
        sys.exit(1)
    
    near_config = None
    for config in configs:
        if isinstance(config, dict) and "NEAR" in config.get('symbol', '').upper():
            near_config = config
            break
    
    if not near_config:
        print("[ERROR] Khong tim thay config NEAR!")
        print(f"Available configs: {[c.get('name', 'N/A') for c in configs]}")
        sys.exit(1)
    
    print(f"[OK] Tim thay config: {near_config.get('name')} (ID: {near_config.get('id')})")
    print(f"Symbol: {near_config.get('symbol')}")
    print(f"Amount: {near_config.get('amount')}")
    
except Exception as e:
    print(f"[ERROR] Loi: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Kiem tra so du
print("\nBuoc 3: Kiem tra so du...")
try:
    from app.database import SessionLocal
    from app.models.bot_config import BotConfig
    from app.core.security import decrypt_data
    import ccxt
    
    db = SessionLocal()
    config_db = db.query(BotConfig).filter(BotConfig.id == near_config['id']).first()
    
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
    print(f"Gia NEAR hien tai: {current_price} USDT")
    print(f"Can de mua 5 NEAR: {5 * current_price:.2f} USDT")
    
    if usdt_free < 5 * current_price:
        print(f"\n[WARN] Khong du so du!")
        print(f"Can: {5 * current_price:.2f} USDT")
        print(f"Co: {usdt_free} USDT")
        print(f"Thieu: {5 * current_price - usdt_free:.2f} USDT")
        sys.exit(1)
    
    print("[OK] Du so du de mua 5 NEAR")
    
except Exception as e:
    print(f"[WARN] Khong the kiem tra so du: {e}")
    print("[INFO] Tiep tuc dat lenh...")

# Dat lenh
print("\nBuoc 4: Dat lenh mua 5 NEAR/USDT...")
print("[WARN] Day la lenh THAT tren Binance!")
print()

payload = {
    "bot_config_id": near_config['id'],
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
        print(f"Total Cost: {(result.get('filled_price') or result.get('price') or 0) * 5:.2f} USDT")
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

