@echo off
chcp 65001 >nul
echo ========================================
echo   KIEM TRA POSTGRESQL
echo ========================================
echo.
echo Script nay se:
echo   1. Test ket noi PostgreSQL server
echo   2. Hien thi danh sach databases
echo   3. Kiem tra database cu the (neu co)
echo.
echo Nhan phim bat ky de tiep tuc...
pause >nul
echo.

python kiem_tra_postgresql.py

echo.
pause

