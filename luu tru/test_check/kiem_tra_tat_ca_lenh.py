"""
Kiem tra tat ca lenh de tim hieu tai sao co 2 lenh
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

print("="*60)
print("KIEM TRA TAT CA LENH")
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

# Lay tat ca lenh
print("\nBuoc 2: Lay tat ca lenh...")
try:
    response = requests.get(
        f"{BASE_URL}/api/orders/",
        headers=headers,
        params={"skip": 0, "limit": 100},
        timeout=5
    )
    
    if response.status_code == 200:
        orders = response.json()
        print(f"[OK] Tim thay {len(orders)} lenh(s)")
        
        if len(orders) == 0:
            print("[INFO] Khong co lenh nao")
            sys.exit(0)
        
        print("\n" + "="*60)
        print("DANH SACH TAT CA LENH:")
        print("="*60)
        
        for i, order in enumerate(orders, 1):
            print(f"\n--- LENH {i} ---")
            print(f"Order ID: {order.get('id')}")
            print(f"Exchange Order ID: {order.get('exchange_order_id')}")
            print(f"Bot Config ID: {order.get('bot_config_id')}")
            print(f"Symbol: {order.get('symbol')}")
            print(f"Side: {order.get('side')}")
            print(f"Order Type: {order.get('order_type')}")
            print(f"Amount: {order.get('amount')}")
            print(f"Filled Amount: {order.get('filled_amount')}")
            print(f"Price: {order.get('price')}")
            print(f"Filled Price: {order.get('filled_price')}")
            print(f"Status: {order.get('status')}")
            print(f"Created At: {order.get('created_at')}")
            print(f"Updated At: {order.get('updated_at')}")
            
            # Check raw_data
            if order.get('raw_data'):
                raw = order.get('raw_data')
                if isinstance(raw, dict):
                    print(f"Exchange Status: {raw.get('status')}")
                    print(f"Exchange Info: {raw.get('info', {})}")
        
        # Phan tich
        print("\n" + "="*60)
        print("PHAN TICH:")
        print("="*60)
        
        if len(orders) > 1:
            print(f"[WARN] Co {len(orders)} lenh duoc tao!")
            
            # Group by symbol
            by_symbol = {}
            for order in orders:
                symbol = order.get('symbol')
                if symbol not in by_symbol:
                    by_symbol[symbol] = []
                by_symbol[symbol].append(order)
            
            for symbol, symbol_orders in by_symbol.items():
                if len(symbol_orders) > 1:
                    print(f"\n[WARN] Symbol {symbol} co {len(symbol_orders)} lenh:")
                    for order in symbol_orders:
                        print(f"  - ID: {order.get('id')}, Status: {order.get('status')}, Amount: {order.get('amount')}, Created: {order.get('created_at')}")
            
            # Check duplicate exchange_order_id
            exchange_ids = [o.get('exchange_order_id') for o in orders if o.get('exchange_order_id')]
            if len(exchange_ids) != len(set(exchange_ids)):
                print("\n[WARN] Co lenh trung Exchange Order ID!")
                from collections import Counter
                duplicates = [item for item, count in Counter(exchange_ids).items() if count > 1]
                print(f"  Duplicate IDs: {duplicates}")
        
        # Check timing
        if len(orders) >= 2:
            times = [o.get('created_at') for o in orders if o.get('created_at')]
            if len(times) >= 2:
                print(f"\nThoi gian tao lenh:")
                for i, order in enumerate(orders[:2], 1):
                    print(f"  Lenh {i}: {order.get('created_at')}")
        
    else:
        print(f"[ERROR] Khong the lay danh sach lenh: {response.json()}")
        
except Exception as e:
    print(f"[ERROR] Loi: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*60)

