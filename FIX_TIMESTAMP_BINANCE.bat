@echo off
echo ========================================
echo   Fix Timestamp Error - Binance
echo ========================================
echo.

echo Loi: "Timestamp for this request was 1000ms ahead"
echo.
echo Nguyen nhan: Thoi gian may tinh khong dong bo voi Binance server
echo.
echo ========================================
echo   Giai Phap
echo ========================================
echo.

echo [1/2] Dang sync thoi gian...
call SYNC_THOI_GIAN.bat

echo.
echo [2/2] Kiem tra lai thoi gian...
call KIEM_TRA_THOI_GIAN.bat

echo.
echo ========================================
echo   Sau Khi Sync
echo ========================================
echo.
echo 1. Restart backend:
echo    RESTART_BACKEND_NAT.bat
echo.
echo 2. Test dat lenh lai
echo.
pause

