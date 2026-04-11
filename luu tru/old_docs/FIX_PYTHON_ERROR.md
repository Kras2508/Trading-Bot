# Sửa lỗi Python Configuration

## Vấn đề
Lỗi: `Fatal Python error: init_fs_encoding: failed to get the Python codec`

Nguyên nhân: Python đang nhầm lẫn thư mục dự án với môi trường Python.

## Giải pháp

### Cách 1: Sử dụng Virtual Environment (Khuyến nghị)

**Bước 1: Tạo và cài đặt virtual environment**
```bash
TAO_VENV_VA_CAI_DAT.bat
```

**Bước 2: Chạy server với venv**
```bash
CHAY_VENV.bat
```

### Cách 2: Sửa thủ công

**1. Kiểm tra biến môi trường:**
```powershell
# Xóa các biến môi trường có thể gây xung đột
$env:PYTHONHOME = $null
$env:PYTHONPATH = $null
```

**2. Tạo virtual environment:**
```bash
python -m venv venv
```

**3. Kích hoạt venv:**
```bash
venv\Scripts\activate
```

**4. Cài đặt dependencies:**
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**5. Chạy server:**
```bash
python run.py
```

### Cách 3: Sửa cài đặt Python

Nếu vẫn lỗi, có thể Python installation bị lỗi:

1. **Kiểm tra Python installation:**
   ```bash
   python --version
   where python
   ```

2. **Thử cài đặt lại Python:**
   - Tải Python từ python.org
   - Chọn "Add Python to PATH" khi cài đặt
   - Cài đặt lại

3. **Hoặc sử dụng Python từ Microsoft Store:**
   - Mở Microsoft Store
   - Tìm "Python 3.11"
   - Cài đặt và sử dụng

### Cách 4: Sử dụng Docker (Nếu có)

Nếu bạn có Docker, có thể chạy trong container để tránh vấn đề môi trường.

## Kiểm tra sau khi sửa

Sau khi chạy thành công, mở trình duyệt:
- http://localhost:8000/docs
- http://localhost:8000/health

## Lưu ý

- **Luôn sử dụng virtual environment** để tránh xung đột
- **Không đặt tên thư mục là "Lib" hoặc "DLLs"** trong dự án
- **Kiểm tra biến môi trường** PYTHONHOME và PYTHONPATH

