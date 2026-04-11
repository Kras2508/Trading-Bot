"""
Script test đặt lệnh trực tiếp lên Binance
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("="*60)
print("TEST ĐẶT LỆNH TRỰC TIẾP LÊN BINANCE")
print("="*60)
print()

# Login
print("Bước 1: Đăng nhập...")
username = input("Username: ").strip()
password = input("Password: ").strip()

try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        params={"username": username, "password": password},
        timeout=5
    )
    if response.status_code != 200:
        print(f"[ERROR] Đăng nhập thất bại: {response.json()}")
        exit(1)
    token = response.json()["access_token"]
    print("[OK] Đăng nhập thành công!")
except Exception as e:
    print(f"[ERROR] Lỗi: {e}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# List configs
print("\nBước 2: Lấy danh sách bot configs...")
try:
    response = requests.get(f"{BASE_URL}/api/config/", headers=headers, timeout=5)
    configs = response.json()
    print(f"[OK] Tìm thấy {len(configs)} configs")
    
    if not configs:
        print("[ERROR] Chưa có bot config nào!")
        exit(1)
    
    print("\nDanh sách configs:")
    for i, config in enumerate(configs, 1):
        has_api = "✅" if config.get('api_key_encrypted') else "❌"
        print(f"{i}. {has_api} {config['name']} - {config['symbol']} ({config['exchange']})")
    
    choice = input("\nChọn config (số): ").strip()
    selected_config = configs[int(choice) - 1]
    
    if not selected_config.get('api_key_encrypted'):
        print("[ERROR] Config này chưa có API key/secret!")
        print("Vui lòng cập nhật config với API key/secret từ Binance.")
        exit(1)
    
    print(f"[OK] Đã chọn: {selected_config['name']}")
    
except Exception as e:
    print(f"[ERROR] Lỗi: {e}")
    exit(1)

# Place order
print("\nBước 3: Đặt lệnh trực tiếp...")
print("⚠️  CẢNH BÁO: Đây là lệnh THẬT trên Binance!")
print()

side = input("Side (buy/sell) [buy]: ").strip() or "buy"
order_type = input("Order type (market/limit) [market]: ").strip() or "market"

amount = None
price = None

if order_type == "limit":
    price_input = input("Price: ").strip()
    if price_input:
        price = float(price_input)

amount_input = input(f"Amount (Enter để dùng {selected_config['amount']}): ").strip()
if amount_input:
    amount = float(amount_input)

payload = {
    "bot_config_id": selected_config['id'],
    "side": side,
    "order_type": order_type
}

if amount:
    payload["amount"] = amount
if price:
    payload["price"] = price

print(f"\nPayload: {json.dumps(payload, indent=2)}")
confirm = input("\n⚠️  Xác nhận đặt lệnh THẬT? (yes/no): ")
if confirm.lower() != "yes":
    print("Đã hủy.")
    exit(0)

try:
    print("\nĐang đặt lệnh...")
    response = requests.post(
        f"{BASE_URL}/api/trading/place-order",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    print(f"\nStatus: {response.status_code}")
    result = response.json()
    print(f"Response:\n{json.dumps(result, indent=2)}")
    
    if response.status_code == 200:
        print("\n[SUCCESS] Đặt lệnh thành công!")
        print(f"Order ID: {result.get('order_id')}")
        print(f"Exchange Order ID: {result.get('exchange_order_id')}")
        print(f"Price: {result.get('filled_price') or result.get('price')}")
        print(f"Stop Loss: {result.get('stop_loss')}")
        print(f"Take Profit: {result.get('take_profit')}")
    else:
        print("\n[ERROR] Đặt lệnh thất bại!")
        print(f"Error: {result.get('detail')}")
        
except Exception as e:
    print(f"\n[ERROR] Lỗi: {e}")

print()
print("="*60)
print("Hoàn thành!")
print("="*60)

