@echo off
REM Script dat lenh day du voi curl
echo ========================================
echo Dat lenh truc tiep len Binance
echo ========================================
echo.

REM Login va lay token
echo Dang nhap...
for /f "tokens=2 delims=:," %%a in ('curl -s -X POST "http://127.0.0.1:8000/api/auth/login?username=testuser^&password=testpass123"') do set TOKEN=%%a
set TOKEN=%TOKEN:"=%
set TOKEN=%TOKEN: =%

if "%TOKEN%"=="" (
    echo [ERROR] Khong the lay token!
    echo Vui long kiem tra username/password
    pause
    exit /b 1
)

echo [OK] Da lay token thanh cong!
echo.

REM Dat lenh
echo Dang dat lenh...
curl -X POST "http://127.0.0.1:8000/api/trading/place-order" ^
  -H "accept: application/json" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -d "{\"bot_config_id\": 1, \"side\": \"buy\", \"order_type\": \"market\"}"

echo.
echo.
pause

