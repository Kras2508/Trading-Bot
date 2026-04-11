@echo off
chcp 65001 >nul
echo ========================================
echo   MIGRATE DU LIEU SQL SERVER -^> POSTGRESQL
echo   (TU DONG - KHONG CAN NHAP)
echo ========================================
echo.
echo Script nay se:
echo   1. Ket noi den SQL Server (DESKTOP-MDT6RKU\TGC)
echo   2. Ket noi den PostgreSQL (localhost)
echo   3. Copy toan bo du lieu tu SQL Server sang PostgreSQL
echo.
echo LUU Y: Du lieu cu trong PostgreSQL se bi xoa!
echo.
echo Nhan phim bat ky de tiep tuc...
pause >nul
echo.

python migrate_sqlserver_to_postgresql_auto.py

echo.
pause

