@echo off
echo ========================================
echo Trading Bot - Bắt Đầu Nhanh
echo ========================================
echo.

echo Bước 1: Kiểm tra server đang chạy...
curl -s http://127.0.0.1:8000/health >nul 2>&1
if errorlevel 1 (
    echo Server chưa chạy! Đang khởi động...
    start "Backend Server" cmd /k "python run.py"
    echo Đợi 5 giây để server khởi động...
    timeout /t 5 /nobreak >nul
) else (
    echo [OK] Server đang chạy!
)

echo.
echo ========================================
echo Chọn hành động:
echo ========================================
echo 1. Tạo User Admin
echo 2. Test API
echo 3. Mở Swagger UI (trình duyệt)
echo 4. Chạy Frontend React
echo 5. Xem hướng dẫn
echo.
set /p choice="Chọn (1-5): "

if "%choice%"=="1" (
    python TAO_USER_ADMIN.py
    goto :end
)

if "%choice%"=="2" (
    python test_api.py
    goto :end
)

if "%choice%"=="3" (
    start http://127.0.0.1:8000/docs
    echo Đã mở Swagger UI trong trình duyệt
    goto :end
)

if "%choice%"=="4" (
    cd frontend
    if not exist node_modules (
        echo Installing dependencies...
        call npm install
    )
    echo Starting React frontend...
    npm run dev
    goto :end
)

if "%choice%"=="5" (
    start HUONG_DAN_SU_DUNG.md
    goto :end
)

echo Lựa chọn không hợp lệ!

:end
pause

