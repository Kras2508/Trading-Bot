"""
Test dat lenh mua NEAR/USDT Spot (Tim minimum notional)
"""
import requests
import json
import sys
import ccxt

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

print("="*60)
print("KIEM TRA MINIMUM NOTIONAL VA TEST DAT LENH")
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

# Lay config tu database
print("\nBuoc 2: Lay config NEAR...")
try:
    from app.database import SessionLocal
    from app.models.bot_config import BotConfig
    from app.core.security import decrypt_data
    
    db = SessionLocal()
    config_db = db.query(BotConfig).filter(BotConfig.id == 2).first()
    
    if not config_db or not config_db.api_key_encrypted:
        print("[ERROR] Config khong co API key!")
        sys.exit(1)
    
    api_key = decrypt_data(config_db.api_key_encrypted)
    api_secret = decrypt_data(config_db.api_secret_encrypted)
    
    print(f"[OK] Config: {config_db.name} - {config_db.symbol}")
    
except Exception as e:
    print(f"[ERROR] Loi: {e}")
    sys.exit(1)

# Ket noi Binance
print("\nBuoc 3: Ket noi Binance...")
try:
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'options': {
            'adjustForTimeDifference': True,
            'defaultType': 'spot'
        }
    })
    
    print("[OK] Ket noi thanh cong!")
    
    # Lay thong tin market
    print("\nBuoc 4: Lay thong tin market NEAR/USDT...")
    markets = exchange.load_markets()
    market = markets.get('NEAR/USDT')
    
    if not market:
        print("[ERROR] Khong tim thay market NEAR/USDT!")
        sys.exit(1)
    
    # Lay minimum notional
    limits = market.get('limits', {})
    cost_min = limits.get('cost', {}).get('min')
    
    ticker = exchange.fetch_ticker('NEAR/USDT')
    current_price = ticker['last']
    
    print(f"Gia hien tai: {current_price} USDT")
    if cost_min:
        print(f"Minimum notional: {cost_min} USDT")
        min_amount = cost_min / current_price
        print(f"Can mua toi thieu: {min_amount:.4f} NEAR")
    else:
        print("[WARN] Khong co thong tin minimum notional")
        print("[INFO] Thuong la 5-10 USDT cho spot trading")
        cost_min = 5.0  # Default
        min_amount = cost_min / current_price
        print(f"Uoc tinh can mua toi thieu: {min_amount:.4f} NEAR (~{cost_min} USDT)")
    
    # Check balance
    balance = exchange.fetch_balance()
    usdt_free = balance['free'].get('USDT', 0)
    
    print(f"\nSo du USDT: {usdt_free}")
    
    if usdt_free < cost_min:
        print(f"\n[WARN] Khong du so du de dat lenh!")
        print(f"Can it nhat: {cost_min} USDT")
        print(f"Hien co: {usdt_free} USDT")
        print(f"Thieu: {cost_min - usdt_free:.2f} USDT")
        print("\n[INFO] Khong the test dat lenh vi khong du so du.")
        sys.exit(0)
    
    # Test dat lenh voi so luong phu hop
    test_amount = min_amount * 1.1  # Mua nhieu hon minimum mot chut
    if test_amount * current_price > usdt_free:
        test_amount = usdt_free / current_price * 0.95  # 95% so du
    
    print(f"\nBuoc 5: Test dat lenh...")
    print(f"Amount: {test_amount:.4f} NEAR")
    print(f"Estimated cost: {test_amount * current_price:.2f} USDT")
    print()
    
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "bot_config_id": 2,
        "side": "buy",
        "amount": round(test_amount, 4),
        "order_type": "market"
    }
    
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
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
        print(f"Amount: {result.get('amount')} NEAR")
        print(f"Price: {result.get('filled_price')} USDT")
        print(f"Stop Loss: {result.get('stop_loss')} USDT")
        print(f"Take Profit: {result.get('take_profit')} USDT")
    else:
        print("\n[ERROR] Dat lenh that bai!")
        print(f"Error: {result.get('detail')}")
        
except Exception as e:
    print(f"\n[ERROR] Loi: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*60)

