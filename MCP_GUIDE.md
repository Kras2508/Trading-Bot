# Hướng dẫn Tích hợp & Khởi chạy TradingView MCP Signal Bridge

Tài liệu này hướng dẫn thiết lập và chạy cầu nối **TradingView MCP Signal Bridge** — tự động đọc chỉ báo từ TradingView Desktop và gửi tín hiệu về Backend Trading Bot.

> Mọi đường dẫn và cấu hình đều được đọc từ file `.env` — **không hardcode** bất kỳ path nào trong code.

---

## 📋 Bước 0: Cấu hình file `.env`

Thêm các biến sau vào file `.env` của dự án:

```env
# MCP Signal Bridge
MCP_REPO_PATH=./tradingview-mcp           # Đường dẫn tới repo tradingview-mcp (đã clone trong project)
MCP_BOT_CONFIG=Tên_Bot_Config_Trong_DB    # Tên cấu hình Bot trong Dashboard
MCP_BACKEND_URL=http://localhost:8000     # URL Backend (mặc định localhost)
MCP_POLL_INTERVAL=3.0                     # Chu kỳ quét chỉ báo (giây)
MCP_RSI_BUY_THRESHOLD=30.0               # Ngưỡng RSI bắn lệnh MUA
MCP_RSI_SELL_THRESHOLD=70.0              # Ngưỡng RSI bắn lệnh BÁN

TRADINGVIEW_EXE_PATH=D:\Study\TradingView\TradingView.exe  # Đường dẫn TradingView Desktop
```

> `WEBHOOK_PASSPHRASE` đã có sẵn trong `.env` — Bridge tự đọc biến này để gắn vào payload.

---

## ⚠️ Lưu ý quan trọng về TradingView Desktop

Bản TradingView cài từ **Microsoft Store (MSIX)** bị Windows sandbox và **không thể** nhận tham số `--remote-debugging-port=9222`.

**Workaround**: Copy TradingView.exe ra folder thông thường:

```powershell
# Lấy path cài đặt
$src = (Get-AppxPackage -Name 'TradingView.Desktop').InstallLocation

# Copy ra D:\Study\TradingView
Copy-Item "$src\*" "D:\Study\TradingView" -Recurse -Force
```

Sau đó set trong `.env`:
```env
TRADINGVIEW_EXE_PATH=D:\Study\TradingView\TradingView.exe
```

---

## 🚀 Bước 1: Khởi chạy TradingView Desktop ở chế độ Debug

```cmd
scripts\launch_tv_debug.bat
```

Script tự đọc `TRADINGVIEW_EXE_PATH` từ `.env`, kill instance cũ, rồi launch với debug port.

**Kiểm tra**: Mở `http://127.0.0.1:9222/json/version` trong trình duyệt — nếu thấy JSON là thành công.

---

## 🤖 Bước 2: Khởi chạy Python Signal Bridge Worker

Script tự đọc toàn bộ cấu hình từ `.env`:

```bash
python scripts/tradingview_mcp_bridge.py
```

Hoặc override tham số cụ thể:

```bash
python scripts/tradingview_mcp_bridge.py --bot-config "My_Bot" --interval 5.0
```

---

## 📊 Bước 3: Kiểm tra kết quả

Khi RSI thỏa điều kiện, Bridge tự đóng gói payload và gửi tới `/api/webhook/tradingview`:

```json
{
  "symbol": "BTCUSDT",
  "action": "buy",
  "config": "Tên_Bot_Config_Trong_DB",
  "passphrase": "(đọc từ WEBHOOK_PASSPHRASE trong .env)",
  "details": { "rsi": 28.5, "source": "MCP_Bridge" }
}
```

Kiểm tra kết quả tại trang **Activity Logs** hoặc **Orders** trên Dashboard.

---

## 💡 Lưu ý

- **Backend KHÔNG bị sửa đổi**: Bridge gửi qua endpoint webhook hiện có, hoàn toàn tương thích.
- **Không hardcode path**: Mọi đường dẫn nằm trong `.env`.
- **Bảo mật**: Bridge chạy 100% local, không gửi dữ liệu ra ngoài internet.
- **`tradingview-mcp`** đã được clone vào `./tradingview-mcp/` trong project root.
