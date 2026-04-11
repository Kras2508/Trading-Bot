"""
Kiem tra so du tai khoan Binance
"""
import requests
import json
import sys
import ccxt

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

print("="*60)
print("KIEM TRA SO DU TAI KHOAN BINANCE")
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

# Lay config NEAR tu database truc tiep
print("\nBuoc 2: Lay config NEAR...")
try:
    from app.database import SessionLocal
    from app.models.bot_config import BotConfig
    from app.core.security import decrypt_data
    from app.core.config import settings
    
    db = SessionLocal()
    config_db = db.query(BotConfig).filter(BotConfig.id == 2).first()
    
    if not config_db:
        print("[ERROR] Khong tim thay config ID 2!")
        sys.exit(1)
    
    print(f"Config: {config_db.name} (ID: {config_db.id})")
    print(f"Symbol: {config_db.symbol}")
    
    if not config_db.api_key_encrypted or not config_db.api_secret_encrypted:
        print("[ERROR] Config chua co API key!")
        sys.exit(1)
    
    # Decrypt API keys
    api_key = decrypt_data(config_db.api_key_encrypted)
    api_secret = decrypt_data(config_db.api_secret_encrypted)
    
    print("\nBuoc 3: Ket noi Binance...")
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
    
    print("\nBuoc 4: Lay so du...")
    balance = exchange.fetch_balance()
    
    print("\n" + "="*60)
    print("SO DU TAI KHOAN:")
    print("="*60)
    
    # Show USDT balance
    if 'USDT' in balance['total']:
        usdt_total = balance['total']['USDT']
        usdt_free = balance['free']['USDT']
        usdt_used = balance['used']['USDT']
        print(f"\nUSDT:")
        print(f"  Total: {usdt_total}")
        print(f"  Free:  {usdt_free}")
        print(f"  Used:  {usdt_used}")
    
    # Show NEAR balance
    if 'NEAR' in balance['total']:
        near_total = balance['total']['NEAR']
        near_free = balance['free']['NEAR']
        print(f"\nNEAR:")
        print(f"  Total: {near_total}")
        print(f"  Free:  {near_free}")
    
    # Show other currencies with balance > 0
    print("\nCac loai tien khac (co so du):")
    for currency, amount in balance['total'].items():
        if amount > 0 and currency not in ['USDT', 'NEAR']:
            print(f"  {currency}: {amount}")
    
    # Check current NEAR price
    print("\nBuoc 5: Lay gia NEAR/USDT hien tai...")
    ticker = exchange.fetch_ticker('NEAR/USDT')
    current_price = ticker['last']
    print(f"Gia hien tai: {current_price} USDT")
    
    # Calculate how much NEAR can buy
    if 'USDT' in balance['free']:
        usdt_available = balance['free']['USDT']
        near_can_buy = usdt_available / current_price if current_price > 0 else 0
        print(f"\nSo du USDT kha dung: {usdt_available}")
        print(f"Co the mua duoc: {near_can_buy:.4f} NEAR")
        print(f"\nDe mua 3 NEAR can: {3 * current_price:.2f} USDT")
        
        if usdt_available < 3 * current_price:
            print(f"\n[WARN] Khong du so du! Can it nhat {3 * current_price:.2f} USDT")
            print(f"       Hien co: {usdt_available} USDT")
            print(f"       Thieu: {3 * current_price - usdt_available:.2f} USDT")
    
except Exception as e:
    print(f"\n[ERROR] Loi: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*60)

