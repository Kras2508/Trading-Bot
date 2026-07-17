# Hướng dẫn Chuẩn hóa API Response & Luồng Xử lý Exception/Logs

Dự án sử dụng một hệ thống quản lý lỗi ngoại lệ hướng đối tượng (OOP) thống nhất và bộ làm sạch lỗi tự động, tương thích hoàn toàn với cấu trúc Frontend và chuẩn thiết kế RESTful.

---

## 📝 Danh sách các Tệp thuộc Hệ thống Exception/Logs

*   **`app/exceptions/error_code.py`**: Định nghĩa Enum mã lỗi hệ thống dạng `internal_code|http_status_code` (ví dụ: `EXCHANGE_ERROR = '100|400'`, `NOT_FOUND = '3|404'`).
*   **`app/exceptions/error_exception.py`**: Lớp Exception cơ sở `ErrorException`. Tự động dọn dẹp và chuẩn hóa thuộc tính `message` của lỗi ngay khi khởi tạo.
*   **`app/exceptions/logical_exception.py`**: Khai báo các lớp con chuyên biệt kế thừa từ `ErrorException`:
    *   `NotFoundException` (HTTP 404 - Không tìm thấy tài nguyên)
    *   `UnauthorizedException` (HTTP 401 - Chưa xác thực)
    *   `ForbiddenException` (HTTP 403 - Bị cấm truy cập)
    *   `BadRequestException` (HTTP 400 - Yêu cầu không hợp lệ)
    *   `ValidationException` (HTTP 422 - Lỗi dữ liệu đầu vào)
    *   `ExchangeException` (HTTP 400 - Lỗi phát sinh từ sàn giao dịch, mã lỗi nội bộ 100)
*   **`app/utils/error_parser.py`**: Bộ tiện ích Regex & JSON dọn dẹp các thông điệp JSON thô từ CCXT/Binance và de-duplicate các tiền tố lồng ghép phức tạp.
*   **`app/utils/response.py`**: Khai báo helper tạo phản hồi JSON thành công (`success_response`) và lỗi (`error_response`).
*   **`app/services/activity_log_service.py`**: Dịch vụ ghi log tự động dọn dẹp thông điệp ghi vào DB, đồng thời lưu giữ lỗi thô chứa mã lỗi kỹ thuật ban đầu dưới khóa `raw_error` trong cột `details`.
*   **`app/main.py`**: Đăng ký bộ xử lý lỗi ngoại lệ toàn cục cho `ErrorException`, phân loại mức độ ghi log (Warning cho 4xx, Error cho 5xx).

---

## 💡 Cấu trúc Phản hồi Chuẩn (API Response Format)

### 1. Phản hồi Thành công (Success Response) - Mã HTTP 200/201
```json
{
  "success": true,
  "message": "Thông điệp thành công",
  "data": { ... } // Dữ liệu trả về (Object, List hoặc Null)
}
```

### 2. Phản hồi Lỗi (Error Response) - Mã HTTP 4xx/5xx
```json
{
  "success": false,
  "message": "Thông điệp lỗi đã được làm sạch để hiển thị cho người dùng",
  "code": 100, // Mã lỗi hệ thống nội bộ (Mặc định: 0, ExchangeException: 100)
  "detail": "Thông điệp lỗi đã được làm sạch (Trường này dùng để tương thích ngược với Axios parse)"
}
```

---

## 🛠️ Hướng dẫn Sử dụng cho Nhà phát triển (Developer Guide)

### 1. Trả về Response thành công trong Router
Khi viết endpoint mới, hãy sử dụng `success_response`:
```python
from app.utils.response import success_response

@router.get("/your-endpoint")
async def your_route_handler():
    data = {"key": "value"}
    return success_response(data=data, message="Lấy dữ liệu thành công")
```

### 2. Ném lỗi ngoại lệ trong Router / Service
**TUYỆT ĐỐI KHÔNG** sử dụng `raise HTTPException(...)` thô trong router. Hãy sử dụng các lớp ngoại lệ chuyên biệt:

```python
from app.exceptions.logical_exception import NotFoundException, BadRequestException, ExchangeException

# 1. Lỗi không tìm thấy tài nguyên (HTTP 404)
raise NotFoundException(message="Không tìm thấy bot cấu hình")

# 2. Lỗi do yêu cầu không hợp lệ (HTTP 400)
raise BadRequestException(message="Bot hiện đang tạm dừng")

# 3. Lỗi do Binance / CCXT (HTTP 400, code: 100)
# Truyền thêm dữ liệu thô nhận được từ sàn vào error_details để hỗ trợ lưu log kỹ thuật
raise ExchangeException(
    message=f"Failed to place order: {result.get('error')}",
    error_details=result
)
```

### 3. Ghi nhận nhật ký lỗi hoạt động (Activity Logs)
Khi bắt lỗi và ghi nhận nhật ký hoạt động vào database:
*   Trường `message` của log ghi DB sẽ tự động được lọc sạch, ví dụ: `binance: Invalid Api-Key ID.`
*   Khi người dùng click vào xem **Chi tiết (Details)** của dòng log trên giao diện Web UI, phần chi tiết mở rộng (inline row expansion) sẽ tự động hiển thị dữ liệu thô bao gồm cả `"raw_error"` chứa mã lỗi kỹ thuật ban đầu (`"code": -2008` của Binance) nhờ cơ chế lưu trữ tự động của `log_activity`.

```python
# Hệ thống sẽ tự động dọn dẹp message và lưu vết lỗi thô nguyên bản vào details
activity_log_service.log_activity(
    db=db,
    level="error",
    category="trading",
    message=error_msg,
    details=order_result # Chứa thông tin JSON lỗi gốc từ sàn giao dịch
)
```
