@echo off
echo ========================================
echo   Tắt Backend Server
echo ========================================
echo.

REM Kiểm tra quyền Administrator
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Cần quyền Administrator để tắt process!
    echo.
    echo Vui lòng:
    echo   1. Right-click file này
    echo   2. Select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo [1/3] Đang tìm process Python đang chạy...
for /f "tokens=2" %%a in ('netstat -ano ^| findstr :80 ^| findstr LISTENING') do (
    set PID=%%a
    goto :found
)

echo Không tìm thấy process nào đang chạy trên port 80.
pause
exit /b 0

:found
echo Tìm thấy process với PID: %PID%
echo.

echo [2/3] Đang tắt process...
taskkill /F /PID %PID% >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ Đã tắt process thành công!
) else (
    echo ✗ Không thể tắt process. Có thể đã được tắt hoặc cần quyền cao hơn.
)

echo.
echo [3/3] Kiểm tra lại...
timeout /t 1 /nobreak >nul
tasklist | findstr python
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Vẫn còn process Python đang chạy. Vui lòng tắt thủ công.
) else (
    echo.
    echo ✓ Không còn process Python nào đang chạy.
)

echo.
pause

