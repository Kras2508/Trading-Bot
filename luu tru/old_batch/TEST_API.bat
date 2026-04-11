@echo off
echo ========================================
echo Testing Trading Bot Backend API
echo ========================================
echo.

echo Make sure backend is running at http://127.0.0.1:8000
echo.
pause

python test_api.py

echo.
pause

