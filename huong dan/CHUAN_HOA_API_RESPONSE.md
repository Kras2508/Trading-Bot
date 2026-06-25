# Hướng dẫn Chuẩn hóa API Response & Luồng Xử lý Exception

Tài liệu này tóm tắt các thay đổi đã thực hiện và hướng dẫn cách sử dụng cấu trúc chuẩn hóa phản hồi (API Response) mới cho các nhà phát triển trong dự án.

---

## 📝 Danh sách các Tệp thay đổi (Files changed)

*   `[NEW]` app/utils/response.py — Khai báo các hàm helper tạo phản hồi JSON thành công và lỗi.
*   `[MOD]` app/main.py — Đăng ký các bộ bắt lỗi toàn cục (Global Exception Handlers) để tự động chuẩn hóa lỗi.
*   `[MOD]` app/core/middleware.py — Khắc phục lỗi ném ngoại lệ trong IPWhitelistMiddleware.
*   `[MOD]` app/routers/monitoring.py — Triển khai thử nghiệm thành công trên endpoint `/health`.

---

## 💡 Cấu trúc Phản hồi Chuẩn (API Response Format)

Toàn bộ các phản hồi từ API của hệ thống giờ đây được thống nhất theo cấu trúc sau:

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
  "message": "Thông điệp thông báo lỗi",
  "errors": { ... } // Chi tiết lỗi (Object, List hoặc Null)
}
```

---

## 🛠️ Hướng dẫn Sử dụng cho Developer

### 1. Trả về Response thành công trong Router
Khi viết endpoint mới, hãy import `success_response` và sử dụng như sau:

```python
from app.utils.response import success_response

@router.get("/your-endpoint")
async def your_route_handler():
    data = {"example_key": "example_value"}
    return success_response(data=data, message="Lấy dữ liệu thành công")
```
*Lưu ý:* `success_response` đã được bọc `jsonable_encoder` bên trong, vì vậy bạn có thể truyền trực tiếp đối tượng phức tạp như kiểu dữ liệu `datetime` hoặc đối tượng cơ sở dữ liệu SQLAlchemy mà không lo bị lỗi serialize.

### 2. Trả về Response lỗi
Đối với các lỗi xảy ra trong quá trình xử lý logic ở Router hoặc Service:
*   **Trong Router/Service:** Chỉ cần ném lỗi qua `HTTPException` như bình thường.
    ```python
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Không tìm thấy bot cấu hình")
    ```
    Hệ thống bắt lỗi toàn cục (`app/main.py`) sẽ **tự động** bắt lấy ngoại lệ này và chuyển đổi sang định dạng JSON lỗi chuẩn hóa (`{"success": false, "message": "...", "errors": null}`).

*   **Trong Middleware:** Nếu bạn viết Middleware mới, do không thể sử dụng `raise HTTPException` (Starlette không bắt được lỗi từ middleware qua handler), hãy import `error_response` và `return` trực tiếp:
    ```python
    from app.utils.response import error_response
    return error_response(message="Không có quyền truy cập", status_code=403)
    ```
