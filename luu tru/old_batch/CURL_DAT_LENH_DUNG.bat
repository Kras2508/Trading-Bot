@echo off
echo ========================================
echo Dat lenh bang curl (Day du)
echo ========================================
echo.

echo Buoc 1: Dang nhap...
curl -X POST "http://127.0.0.1:8000/api/auth/login?username=testuser&password=testpass123" -o token.json

echo.
echo Token da duoc luu trong token.json
echo Vui long copy access_token tu file token.json
echo.
pause

echo.
echo Buoc 2: Dat lenh...
echo.
echo Nhap token (access_token tu buoc 1):
set /p TOKEN="Token: "

echo.
echo Dang dat lenh...
echo.

curl -X POST "http://127.0.0.1:8000/api/trading/place-order" ^
  -H "accept: application/json" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -d "{\"bot_config_id\": 1, \"side\": \"buy\", \"order_type\": \"market\"}"

echo.
echo.
pause

