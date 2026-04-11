"""
Ví dụ sử dụng API Trading Bot Backend
"""
import requests
import json

# Cấu hình
BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "your-password"

# 1. Đăng ký user (chỉ cần làm 1 lần)
def register_user():
    url = f"{BASE_URL}/api/auth/register"
    data = {
        "username": USERNAME,
        "email": "admin@example.com",
        "password": PASSWORD,
        "is_admin": True
    }
    response = requests.post(url, json=data)
    print("Register:", response.json())
    return response.json()

# 2. Đăng nhập để lấy token
def login():
    url = f"{BASE_URL}/api/auth/login"
    params = {
        "username": USERNAME,
        "password": PASSWORD
    }
    response = requests.post(url, params=params)
    token_data = response.json()
    print("Login:", token_data)
    return token_data["access_token"]

# 3. Tạo bot config
def create_bot_config(token):
    url = f"{BASE_URL}/api/config/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": "BTC Spot Bot",
        "symbol": "BTC/USDT",
        "exchange": "binance",
        "amount": 100.0,
        "leverage": 1,
        "stop_loss_percent": 2.0,
        "take_profit_percent": 5.0,
        "tp_levels": [
            {"percent": 3.0, "close_percent": 50},
            {"percent": 5.0, "close_percent": 50}
        ],
        "enable_trailing": True,
        "trailing_type": "percent",
        "trailing_percent": 1.5,
        "trading_mode": "spot",
        "api_key": "your-api-key",
        "api_secret": "your-api-secret",
        "enable_notifications": True
    }
    response = requests.post(url, headers=headers, json=data)
    print("Create Config:", response.json())
    return response.json()

# 4. Lấy danh sách configs
def list_configs(token):
    url = f"{BASE_URL}/api/config/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print("List Configs:", response.json())
    return response.json()

# 5. Cập nhật config
def update_config(token, config_id):
    url = f"{BASE_URL}/api/config/{config_id}"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "amount": 150.0,
        "stop_loss_percent": 2.5
    }
    response = requests.put(url, headers=headers, json=data)
    print("Update Config:", response.json())
    return response.json()

# 6. Lấy lịch sử lệnh
def get_order_history(token, symbol=None, start_date=None, end_date=None):
    url = f"{BASE_URL}/api/orders/history"
    headers = {"Authorization": f"Bearer {token}"}
    params = {}
    if symbol:
        params["symbol"] = symbol
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    response = requests.get(url, headers=headers, params=params)
    print("Order History:", response.json())
    return response.json()

# 7. Lấy trạng thái bot
def get_bot_status(token, bot_config_id):
    url = f"{BASE_URL}/api/monitoring/status/{bot_config_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    print("Bot Status:", response.json())
    return response.json()

# 8. Tạm dừng bot
def pause_bot(token, bot_config_id):
    url = f"{BASE_URL}/api/monitoring/status/{bot_config_id}/pause"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, headers=headers)
    print("Pause Bot:", response.json())
    return response.json()

# 9. Tiếp tục bot
def resume_bot(token, bot_config_id):
    url = f"{BASE_URL}/api/monitoring/status/{bot_config_id}/resume"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, headers=headers)
    print("Resume Bot:", response.json())
    return response.json()

# 10. Test webhook (simulate TradingView alert)
def test_webhook():
    url = f"{BASE_URL}/api/webhook/tradingview"
    data = {
        "symbol": "BTC/USDT",
        "action": "buy",
        "config": "BTC Spot Bot"
    }
    response = requests.post(url, json=data)
    print("Webhook Response:", response.json())
    return response.json()


if __name__ == "__main__":
    # Uncomment các bước bạn muốn chạy
    
    # Bước 1: Đăng ký (chỉ cần 1 lần)
    # register_user()
    
    # Bước 2: Đăng nhập
    token = login()
    
    # Bước 3: Tạo config
    # config = create_bot_config(token)
    
    # Bước 4: List configs
    # list_configs(token)
    
    # Bước 5: Update config
    # update_config(token, config_id=1)
    
    # Bước 6: Order history
    # get_order_history(token)
    
    # Bước 7: Bot status
    # get_bot_status(token, bot_config_id=1)
    
    # Bước 8: Pause bot
    # pause_bot(token, bot_config_id=1)
    
    # Bước 9: Resume bot
    # resume_bot(token, bot_config_id=1)
    
    # Bước 10: Test webhook
    # test_webhook()

