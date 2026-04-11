"""
Kiem tra trang thai lenh
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

print("="*60)
print("KIEM TRA TRANG THAI LENH")
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

# Kiem tra lenh tu database
print("\nBuoc 2: Lay thong tin lenh tu database...")
order_id = 1  # Order ID vua dat

try:
    # Lay danh sach orders
    response = requests.get(
        f"{BASE_URL}/api/orders/",
        headers=headers,
        params={"skip": 0, "limit": 10},
        timeout=5
    )
    
    if response.status_code == 200:
        orders = response.json()
        print(f"[OK] Tim thay {len(orders)} lenh(s)")
        
        # Tim lenh co ID = 1
        target_order = None
        for order in orders:
            if order.get('id') == order_id:
                target_order = order
                break
        
        if target_order:
            print("\n" + "="*60)
            print("THONG TIN LENH TU DATABASE:")
            print("="*60)
            print(f"Order ID: {target_order.get('id')}")
            print(f"Exchange Order ID: {target_order.get('exchange_order_id')}")
            print(f"Symbol: {target_order.get('symbol')}")
            print(f"Side: {target_order.get('side')}")
            print(f"Order Type: {target_order.get('order_type')}")
            print(f"Amount: {target_order.get('amount')}")
            print(f"Filled Amount: {target_order.get('filled_amount')}")
            print(f"Price: {target_order.get('price')}")
            print(f"Filled Price: {target_order.get('filled_price')}")
            print(f"Status: {target_order.get('status')}")
            print(f"Stop Loss: {target_order.get('stop_loss_price')}")
            print(f"Take Profit: {target_order.get('take_profit_price')}")
            print(f"Created At: {target_order.get('created_at')}")
            
            # Kiem tra tren exchange
            if target_order.get('exchange_order_id'):
                print("\n" + "="*60)
                print("KIEM TRA TREN BINANCE...")
                print("="*60)
                
                check_response = requests.get(
                    f"{BASE_URL}/api/trading/check-order/{order_id}",
                    headers=headers,
                    timeout=10
                )
                
                if check_response.status_code == 200:
                    check_result = check_response.json()
                    exchange_order = check_result.get('order', {})
                    
                    print(f"Exchange Status: {exchange_order.get('status')}")
                    print(f"Filled: {exchange_order.get('filled', 0)}")
                    print(f"Remaining: {exchange_order.get('remaining', 0)}")
                    print(f"Average Price: {exchange_order.get('average')}")
                    print(f"Cost: {exchange_order.get('cost')}")
                    
                    if exchange_order.get('trades'):
                        print(f"\nTrades: {len(exchange_order.get('trades', []))} trade(s)")
                        for i, trade in enumerate(exchange_order.get('trades', [])[:3], 1):
                            print(f"  Trade {i}: {trade.get('amount')} @ {trade.get('price')}")
                else:
                    print(f"[WARN] Khong the kiem tra tren exchange: {check_response.json()}")
        else:
            print(f"[WARN] Khong tim thay lenh co ID = {order_id}")
            print("\nDanh sach lenh:")
            for order in orders[:5]:
                print(f"  ID: {order.get('id')}, Symbol: {order.get('symbol')}, Status: {order.get('status')}")
    else:
        print(f"[ERROR] Khong the lay danh sach lenh: {response.json()}")
        
except Exception as e:
    print(f"[ERROR] Loi: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*60)

