"""
Kiem tra chi tiet trades trong lenh
"""
import requests
import json
import sys
import ccxt

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

print("="*60)
print("KIEM TRA CHI TIET TRADES TRONG LENH")
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

# Lay lenh tu database
print("\nBuoc 2: Lay lenh tu database...")
try:
    response = requests.get(
        f"{BASE_URL}/api/orders/",
        headers=headers,
        params={"skip": 0, "limit": 10},
        timeout=5
    )
    
    if response.status_code == 200:
        orders = response.json()
        
        if not orders:
            print("[INFO] Khong co lenh nao")
            sys.exit(0)
        
        order = orders[0]  # Lenh dau tien
        print(f"[OK] Tim thay lenh ID: {order.get('id')}")
        print(f"Exchange Order ID: {order.get('exchange_order_id')}")
        print(f"Symbol: {order.get('symbol')}")
        
        # Lay config de lay API key
        from app.database import SessionLocal
        from app.models.bot_config import BotConfig
        from app.core.security import decrypt_data
        
        db = SessionLocal()
        config = db.query(BotConfig).filter(BotConfig.id == order.get('bot_config_id')).first()
        
        if not config or not config.api_key_encrypted:
            print("[ERROR] Khong tim thay config hoac API key")
            sys.exit(1)
        
        api_key = decrypt_data(config.api_key_encrypted)
        api_secret = decrypt_data(config.api_secret_encrypted)
        
        # Ket noi Binance
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
        
        exchange_order_id = order.get('exchange_order_id')
        symbol = order.get('symbol')
        
        print(f"\nBuoc 4: Lay chi tiet lenh tren Binance...")
        print(f"Exchange Order ID: {exchange_order_id}")
        print(f"Symbol: {symbol}")
        
        # Fetch order details
        binance_order = exchange.fetch_order(exchange_order_id, symbol)
        
        print("\n" + "="*60)
        print("CHI TIET LENH TREN BINANCE:")
        print("="*60)
        print(f"Order ID: {binance_order.get('id')}")
        print(f"Symbol: {binance_order.get('symbol')}")
        print(f"Type: {binance_order.get('type')}")
        print(f"Side: {binance_order.get('side')}")
        print(f"Amount: {binance_order.get('amount')}")
        print(f"Filled: {binance_order.get('filled')}")
        print(f"Remaining: {binance_order.get('remaining')}")
        print(f"Status: {binance_order.get('status')}")
        print(f"Average Price: {binance_order.get('average')}")
        print(f"Cost: {binance_order.get('cost')}")
        
        # Check trades
        trades = binance_order.get('trades', [])
        print(f"\nSo luong Trades (giao dich): {len(trades)}")
        
        if len(trades) > 1:
            print("\n[INFO] Lenh duoc fill thanh nhieu trades!")
            print("Day la binh thuong khi lenh lon hoac thi truong co nhieu nguoi ban.")
            print("\nChi tiet cac trades:")
            print("-" * 60)
            
            total_amount = 0
            total_cost = 0
            
            for i, trade in enumerate(trades, 1):
                trade_amount = trade.get('amount', 0)
                trade_price = trade.get('price', 0)
                trade_cost = trade_amount * trade_price
                
                total_amount += trade_amount
                total_cost += trade_cost
                
                print(f"\nTrade {i}:")
                print(f"  Amount: {trade_amount}")
                print(f"  Price: {trade_price}")
                print(f"  Cost: {trade_cost}")
                print(f"  Time: {trade.get('datetime') or trade.get('timestamp')}")
                print(f"  Fee: {trade.get('fee', {})}")
            
            print("\n" + "-" * 60)
            print(f"Tong cong:")
            print(f"  Total Amount: {total_amount}")
            print(f"  Total Cost: {total_cost}")
            print(f"  Average Price: {total_cost / total_amount if total_amount > 0 else 0}")
        elif len(trades) == 1:
            print("\n[INFO] Lenh duoc fill trong 1 trade duy nhat")
            trade = trades[0]
            print(f"  Amount: {trade.get('amount')}")
            print(f"  Price: {trade.get('price')}")
            print(f"  Cost: {trade.get('amount', 0) * trade.get('price', 0)}")
        else:
            print("\n[WARN] Khong co thong tin trades")
        
        # Check raw_data trong database
        print("\n" + "="*60)
        print("RAW DATA TRONG DATABASE:")
        print("="*60)
        raw_data = order.get('raw_data')
        if raw_data:
            if isinstance(raw_data, dict):
                print(f"Status: {raw_data.get('status')}")
                print(f"Filled: {raw_data.get('filled')}")
                raw_trades = raw_data.get('trades', [])
                if raw_trades:
                    print(f"Trades trong raw_data: {len(raw_trades)}")
                else:
                    print("Khong co trades trong raw_data")
            else:
                print(f"Raw data type: {type(raw_data)}")
        else:
            print("Khong co raw_data")
        
    else:
        print(f"[ERROR] Khong the lay lenh: {response.json()}")
        
except Exception as e:
    print(f"[ERROR] Loi: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*60)
print("\nGIAI THICH:")
print("="*60)
print("1. ORDER = 1 lenh dat mua/ban")
print("2. TRADES = Cac giao dich fill lenh do")
print("3. 1 ORDER co the co nhieu TRADES neu:")
print("   - Lenh lon, can nhieu nguoi ban")
print("   - Thi truong co nhieu nguoi ban o cac muc gia khac nhau")
print("4. Day la binh thuong va khong phai loi!")
print("="*60)

