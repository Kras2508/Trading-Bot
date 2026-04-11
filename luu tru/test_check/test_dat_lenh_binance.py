"""
Script test đặt lệnh trên Binance (CẨN THẬN - Sẽ đặt lệnh thật!)
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("="*60)
print("TEST ĐẶT LỆNH TRÊN BINANCE")
print("="*60)
print()
print("⚠️  CẢNH BÁO: Script này sẽ đặt lệnh THẬT trên Binance!")
print("⚠️  Chỉ test với số tiền nhỏ và API key testnet!")
print()

confirm = input("Bạn có chắc muốn tiếp tục? (yes/no): ")
if confirm.lower() != "yes":
    print("Đã hủy.")
    exit(0)

print()
print("Bước 1: Đăng nhập...")
username = input("Username: ").strip()
password = input("Password: ").strip()

# Login
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        params={"username": username, "password": password},
        timeout=5
    )
    if response.status_code != 200:
        print(f"❌ Đăng nhập thất bại: {response.json()}")
        exit(1)
    token = response.json()["access_token"]
    print("✅ Đăng nhập thành công!")
except Exception as e:
    print(f"❌ Lỗi: {e}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

print()
print("Bước 2: Kiểm tra bot configs...")
try:
    response = requests.get(f"{BASE_URL}/api/config/", headers=headers, timeout=5)
    configs = response.json()
    print(f"✅ Tìm thấy {len(configs)} configs")
    
    if not configs:
        print("❌ Chưa có bot config nào!")
        print("Vui lòng tạo config trước (có API key/secret)")
        exit(1)
    
    print("\nDanh sách configs:")
    for i, config in enumerate(configs, 1):
        print(f"{i}. {config['name']} - {config['symbol']} - {config['exchange']}")
    
    choice = input("\nChọn config (số): ").strip()
    selected_config = configs[int(choice) - 1]
    print(f"✅ Đã chọn: {selected_config['name']}")
    
except Exception as e:
    print(f"❌ Lỗi: {e}")
    exit(1)

print()
print("Bước 3: Test đặt lệnh...")
print("⚠️  Lưu ý: Đây là lệnh THẬT trên Binance!")
print()

side = input("Side (buy/sell) [buy]: ").strip() or "buy"
symbol = selected_config['symbol']

payload = {
    "symbol": symbol,
    "action": side,
    "config": selected_config['name']
}

print(f"\nPayload: {json.dumps(payload, indent=2)}")
confirm2 = input("\nXác nhận đặt lệnh? (yes/no): ")
if confirm2.lower() != "yes":
    print("Đã hủy.")
    exit(0)

try:
    print("\nĐang gửi request...")
    response = requests.post(
        f"{BASE_URL}/api/webhook/tradingview",
        json=payload,
        timeout=30
    )
    
    print(f"\nStatus: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if response.status_code == 200:
        print("\n✅ Đặt lệnh thành công!")
        print(f"Order ID: {result.get('order_id')}")
        print(f"Price: {result.get('price')}")
        print(f"Stop Loss: {result.get('stop_loss')}")
        print(f"Take Profit: {result.get('take_profit')}")
    else:
        print("\n❌ Đặt lệnh thất bại!")
        print(f"Error: {result.get('detail')}")
        
except Exception as e:
    print(f"\n❌ Lỗi: {e}")

print()
print("="*60)
print("Hoàn thành!")
print("="*60)

