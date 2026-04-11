@echo off
echo ========================================
echo Dat lenh truc tiep len Binance (curl)
echo ========================================
echo.

echo Buoc 1: Dang nhap de lay token...
curl -X POST "http://127.0.0.1:8000/api/auth/login?username=testuser&password=testpass123" > token_response.json

echo.
echo Token da duoc luu trong token_response.json
echo.

echo Buoc 2: Dat lenh...
echo.
echo Nhap thong tin:
set /p bot_config_id="Bot Config ID (1): "
if "%bot_config_id%"=="" set bot_config_id=1

set /p side="Side (buy/sell) [buy]: "
if "%side%"=="" set side=buy

set /p order_type="Order type (market/limit) [market]: "
if "%order_type%"=="" set order_type=market

set /p amount="Amount (de trong de dung amount tu config): "

echo.
echo Dang dat lenh...
echo.

REM Read token from file (simplified - you may need to parse JSON)
curl -X POST "http://127.0.0.1:8000/api/trading/place-order" ^
  -H "accept: application/json" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer YOUR_TOKEN_HERE" ^
  -d "{\"bot_config_id\": %bot_config_id%, \"side\": \"%side%\", \"order_type\": \"%order_type%\"}"

echo.
echo.
echo LUU Y: Can thay YOUR_TOKEN_HERE bang token that!
echo Xem huong dan trong file: HUONG_DAN_DAT_LENH_CURL.md
echo.
pause

