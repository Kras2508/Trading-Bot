"""
Script test API Trading Bot Backend
"""
import requests
import json
import sys
from datetime import datetime

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

BASE_URL = "http://127.0.0.1:8000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health():
    """Test health endpoint"""
    print_section("1. Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_root():
    """Test root endpoint"""
    print_section("2. Root Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_register():
    """Test register endpoint"""
    print_section("3. Register User")
    try:
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "is_admin": False
        }
        response = requests.post(f"{BASE_URL}/api/auth/register", json=data, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            print(f"[OK] User created: {response.json()}")
            return True, None
        elif response.status_code == 400:
            print(f"[WARN] User may already exist: {response.json()}")
            return True, None  # User exists, can still login
        else:
            print(f"[ERROR] Error: {response.json()}")
            return False, None
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False, None

def test_login():
    """Test login endpoint"""
    print_section("4. Login")
    try:
        params = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", params=params, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"[OK] Login successful!")
            print(f"Token: {token[:50]}...")
            return True, token
        else:
            print(f"[ERROR] Error: {response.json()}")
            return False, None
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False, None

def test_get_me(token):
    """Test get current user"""
    print_section("5. Get Current User")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"[OK] User info: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"[ERROR] Error: {response.json()}")
            return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def test_list_configs(token):
    """Test list bot configs"""
    print_section("6. List Bot Configs")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/config/", headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            configs = response.json()
            print(f"[OK] Found {len(configs)} configs")
            if configs:
                print(f"First config: {json.dumps(configs[0], indent=2)}")
            return True
        else:
            print(f"[ERROR] Error: {response.json()}")
            return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def test_create_config(token):
    """Test create bot config"""
    print_section("7. Create Bot Config")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "name": f"Test Bot {datetime.now().strftime('%H%M%S')}",
            "symbol": "BTC/USDT",
            "exchange": "binance",
            "amount": 100.0,
            "leverage": 1,
            "stop_loss_percent": 2.0,
            "take_profit_percent": 5.0,
            "trading_mode": "spot",
            "enable_notifications": False
        }
        response = requests.post(f"{BASE_URL}/api/config/", headers=headers, json=data, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            config = response.json()
            print(f"[OK] Config created: ID={config['id']}, Name={config['name']}")
            return True, config['id']
        else:
            print(f"[ERROR] Error: {response.json()}")
            return False, None
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False, None

def test_list_orders(token):
    """Test list orders"""
    print_section("8. List Orders")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/orders/", headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            orders = response.json()
            print(f"[OK] Found {len(orders)} orders")
            return True
        else:
            print(f"[ERROR] Error: {response.json()}")
            return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def test_monitoring_status(token):
    """Test monitoring status"""
    print_section("9. Monitoring Status")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/monitoring/status", headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            statuses = response.json()
            print(f"[OK] Found {len(statuses)} bot statuses")
            if statuses:
                print(f"First status: {json.dumps(statuses[0], indent=2, default=str)}")
            return True
        else:
            print(f"[ERROR] Error: {response.json()}")
            return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def test_webhook():
    """Test webhook endpoint (no auth required)"""
    print_section("10. Webhook Endpoint")
    try:
        data = {
            "symbol": "BTC/USDT",
            "action": "buy",
            "config": "Test Bot"
        }
        response = requests.post(f"{BASE_URL}/api/webhook/tradingview", json=data, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code in [200, 400, 404]:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print("[OK] Webhook endpoint is accessible")
            return True
        else:
            print(f"[ERROR] Error: {response.json()}")
            return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  TRADING BOT BACKEND API TEST")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test 1: Health
    results.append(("Health Check", test_health()))
    
    # Test 2: Root
    results.append(("Root Endpoint", test_root()))
    
    # Test 3: Register
    success, _ = test_register()
    results.append(("Register", success))
    
    # Test 4: Login
    success, token = test_login()
    results.append(("Login", success))
    
    if not token:
        print("\n[ERROR] Cannot continue without token. Please check login.")
        return
    
    # Test 5: Get Me
    results.append(("Get Current User", test_get_me(token)))
    
    # Test 6: List Configs
    results.append(("List Configs", test_list_configs(token)))
    
    # Test 7: Create Config
    success, config_id = test_create_config(token)
    results.append(("Create Config", success))
    
    # Test 8: List Orders
    results.append(("List Orders", test_list_orders(token)))
    
    # Test 9: Monitoring
    results.append(("Monitoring Status", test_monitoring_status(token)))
    
    # Test 10: Webhook
    results.append(("Webhook", test_webhook()))
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! API is working correctly.")
    else:
        print(f"\n[WARN] {total - passed} test(s) failed. Please check the errors above.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")

