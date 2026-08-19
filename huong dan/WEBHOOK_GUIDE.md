# Hướng Dẫn Tính Năng Webhook & Biểu Đồ TradingView

Tài liệu này tóm tắt ngắn gọn cấu trúc các thành phần đã hoàn thành, chức năng của từng file và hướng dẫn cấu hình sử dụng tính năng TradingView Webhook.

---

## 1. Cấu trúc thư mục các file mới và thay đổi

Dưới đây là cấu trúc thư mục của dự án cho thấy vị trí các file được thêm mới hoặc chỉnh sửa:

```text
Trading-Bot/
├── app/
│   ├── models/
│   │   └── system_setting.py        # [NEW] CSDL cấu hình Passphrase & IP Whitelist động
│   ├── routers/
│   │   └── webhook.py               # [MODIFY] Xử lý Webhook (Đảo vị thế, đóng vị thế & check DB)
│   ├── services/
│   │   └── order_sync_worker.py     # [NEW] Worker quét sàn đồng bộ lệnh chạy nền mỗi 30 giây
│   └── main.py                      # [MODIFY] Khởi chạy sync worker & nạp cài đặt mặc định
│
└── frontend/
    ├── index.html                   # [MODIFY] Nhúng script thư viện TradingView global
    └── src/
        └── pages/
            ├── Trading.jsx          # [MODIFY] Biểu đồ 100% chiều cao, tối ưu nhập liệu Symbol
            └── WebhookConnect.jsx   # [MODIFY] UI cấu hình Passphrase & IP Whitelist trực tiếp
```

---

## 2. Chi tiết chức năng từng file

### 📁 Backend (FastAPI)
*   **system_setting.py**: Định nghĩa bảng lưu trữ mật khẩu bảo mật (Passphrase) và danh sách IP Whitelist. Giúp thay đổi trực tiếp qua giao diện web mà không cần sửa file cấu hình `.env` hay khởi động lại server.
*   **order_sync_worker.py**: Worker chạy ngầm mỗi 30 giây để tự động đồng bộ trạng thái lệnh. Nếu vị thế trên sàn đã đóng (do chạm SL/TP hoặc do bạn đóng tay) hoặc lệnh giả lập chạm SL/TP, Worker sẽ cập nhật trạng thái trong database sang `closed` để bot tiếp tục nhận tín hiệu mới.
*   **webhook.py**: Cải tiến bộ nhận tín hiệu webhook:
    *   Hỗ trợ tự động **Đảo vị thế** (đóng vị thế cũ trước khi mở vị thế ngược chiều).
    *   Hỗ trợ tín hiệu **Đóng vị thế** (`action: "close"` hoặc `"exit"`).
    *   Xác thực Passphrase và kiểm tra Whitelist IP từ database.
*   **main.py**: Khởi tạo cấu hình bảo mật mặc định trong DB ở lần đầu chạy và đăng ký khởi động tác vụ chạy nền sync worker.

### 📁 Frontend (React / Vite)
*   **index.html**: Nhúng thư viện TradingView global trong thẻ `<head>` giúp biểu đồ load tức thì khi chuyển trang, tránh lỗi màn hình xám/trắng khi reload.
*   **Trading.jsx**: Nhúng biểu đồ TradingView kéo giãn 100% khít khung card. Chỉ reload biểu đồ khi bấm **Enter** hoặc chọn từ gợi ý Symbol (tránh giật lag khi gõ phím). Sửa lỗi click gợi ý không điền được giá trị.
*   **WebhookConnect.jsx**: Giao diện kết nối tinh giản (xóa bỏ simulator chạy thử nghiệm). Bổ sung form cập nhật Passphrase và bật/tắt IP Whitelist trực tiếp.

---

## 3. Ý nghĩa và Cơ chế hoạt động của Webhook Passphrase

### 🛡️ Ý nghĩa bảo mật:
- Khi bot chạy thực tế, đường dẫn Webhook URL (ví dụ: `https://your-public-url.loca.lt/api/webhook/tradingview`) sẽ được mở công khai trên Internet để TradingView có thể kết nối và gửi tín hiệu.
- Nếu không có cơ chế bảo vệ, bất kỳ ai biết hoặc quét được link này đều có thể gửi lệnh mua/bán giả mạo để tiêu tiền trong tài khoản Binance của bạn.
- **Passphrase** đóng vai trò là một **Mật khẩu bảo mật**. Chỉ các yêu cầu có chứa đúng cụm từ Passphrase này mới được bot chấp nhận xử lý. Mọi yêu cầu sai mật khẩu sẽ bị từ chối ngay lập tức (lỗi HTTP 401 Unauthorized) và ghi nhận vào Nhật ký cảnh báo hệ thống.

### ⚙️ Cơ chế tự động & Cách sử dụng:
*   **Tự động sinh khi cài đặt**: Khi bot khởi chạy lần đầu tiên, nếu bạn chưa cấu hình passphrase trong file `.env`, hệ thống sẽ **tự động tạo ngẫu nhiên một mật khẩu bảo mật cực kỳ an toàn gồm 32 ký tự (Hex)** và lưu vào cơ sở dữ liệu. Người dùng hoàn toàn không cần lo lắng về việc thiết lập ban đầu.
*   **Nút "Tạo ngẫu nhiên" trên Web UI**: Tại trang **Kết nối TradingView**, bên cạnh ô nhập Passphrase đã được bổ sung thêm nút **Tạo ngẫu nhiên**. Chỉ cần một cú click chuột, hệ thống sẽ sinh ngay mật khẩu 16 ký tự an toàn điền vào ô để bạn lưu lại cấu hình mới.
*   **Cấu hình trên TradingView**: Khi tạo Alert trên TradingView, trong ô **Message**, bạn phải khai báo cặp khóa `"passphrase": "mật_khẩu_của_bạn"` khớp chính xác với mật khẩu bảo mật đang hoạt động của bot.

---

## 4. Hướng dẫn cấu hình Webhook (TradingView Alert)

Khi tạo cảnh báo (Alert) trên TradingView, hãy cấu hình như sau:

1.  **Webhook URL**:
    *   Sử dụng URL public của bot (mở qua LocalTunnel hoặc Ngrok), ví dụ: `https://your-public-url.loca.lt/api/webhook/tradingview`
2.  **Mật khẩu bảo mật (Passphrase)**:
    *   Lấy passphrase hiển thị tại mục **Cấu hình Bảo mật Webhook** trên Web UI (hệ thống đã tự động tạo ngẫu nhiên một chuỗi bảo mật an toàn cho bạn khi khởi chạy lần đầu). Bạn có thể sao chép hoặc đổi mới tùy ý.
3.  **Cú pháp JSON gửi tin nhắn (Alert Message)**:
    *   **Mở lệnh BUY (Long)**:
        ```json
        {
          "symbol": "BTC/USDT",
          "action": "buy",
          "config": "Tên Bot Config của bạn",
          "passphrase": "mật_khẩu_webhook_của_bạn"
        }
        ```
    *   **Đảo vị thế sang SELL (Short)**:
        ```json
        {
          "symbol": "BTC/USDT",
          "action": "sell",
          "config": "Tên Bot Config của bạn",
          "passphrase": "mật_khẩu_webhook_của_bạn"
        }
        ```
        *(Bot sẽ tự động đóng lệnh BUY cũ trước, sau đó tự đặt lệnh SELL mới)*
    *   **Đóng vị thế (Exit)**:
        ```json
        {
          "symbol": "BTC/USDT",
          "action": "exit",
          "config": "Tên Bot Config của bạn",
          "passphrase": "mật_khẩu_webhook_của_bạn"
        }
        ```
