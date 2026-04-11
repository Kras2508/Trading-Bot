# Hướng dẫn Sửa Lỗi Python

## Vấn đề
Python đang tìm thư mục `Lib` ở sai vị trí (`C:\Users\TGC\Lib` thay vì trong thư mục cài đặt Python).

## Giải pháp

### Giải pháp 1: Di chuyển dự án (Nhanh nhất)

**Chạy script:**
```bash
DI_CHUYEN_DU_AN.bat
```

Hoặc thủ công:
1. Tạo thư mục mới: `C:\TradingBot`
2. Copy toàn bộ file từ `D:\Website Docusaurus\BackendAPI_Trading` sang `C:\TradingBot`
3. Mở terminal ở `C:\TradingBot`
4. Chạy: `python -m pip install -r requirements.txt --user`
5. Chạy: `python run.py`

### Giải pháp 2: Cài lại Python

1. **Gỡ Python hiện tại:**
   - Control Panel > Programs > Uninstall Python 3.11

2. **Tải Python mới:**
   - Truy cập: https://www.python.org/downloads/
   - Tải Python 3.11.x
   - **QUAN TRỌNG:** Khi cài đặt, chọn "Add Python to PATH"

3. **Cài đặt lại:**
   - Chạy installer
   - Chọn "Install for all users" (nếu có thể)
   - Đảm bảo "Add Python to PATH" được chọn

4. **Kiểm tra:**
   ```bash
   python --version
   python -m pip --version
   ```

5. **Chạy lại dự án:**
   ```bash
   python -m pip install -r requirements.txt
   python run.py
   ```

### Giải pháp 3: Sử dụng Python từ Microsoft Store

1. Mở Microsoft Store
2. Tìm "Python 3.11"
3. Cài đặt
4. Mở PowerShell mới
5. Chạy:
   ```bash
   python -m pip install -r requirements.txt
   python run.py
   ```

### Giải pháp 4: Kiểm tra và xóa file cấu hình sai

Có thể có file `.pth` hoặc cấu hình Python ở `C:\Users\TGC\` gây xung đột:

1. Kiểm tra:
   - `C:\Users\TGC\Lib\`
   - `C:\Users\TGC\DLLs\`
   - `C:\Users\TGC\pyvenv.cfg`

2. Nếu có, xóa hoặc đổi tên các thư mục/file này

3. Thử chạy lại Python

## Khuyến nghị

**Cách nhanh nhất:** Di chuyển dự án sang thư mục khác (ví dụ: `C:\TradingBot`)

**Cách tốt nhất:** Cài lại Python đúng cách với "Add Python to PATH"

## Sau khi sửa

Chạy:
```bash
python -m pip install -r requirements.txt
python run.py
```

Server sẽ chạy tại: http://localhost:8000/docs

