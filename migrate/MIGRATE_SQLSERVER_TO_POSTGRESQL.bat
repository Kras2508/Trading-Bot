@echo off
chcp 65001 >nul
echo ========================================
echo   MIGRATE DU LIEU SQL SERVER -^> POSTGRESQL
echo ========================================
echo.
echo Script nay se:
echo   1. Ket noi den SQL Server (nguon)
echo   2. Ket noi den PostgreSQL (dich)
echo   3. Copy toan bo du lieu tu SQL Server sang PostgreSQL
echo.
echo LUU Y: Du lieu cu trong PostgreSQL se bi xoa!
echo.
echo Nhan phim bat ky de tiep tuc...
pause >nul
echo.

python migrate_sqlserver_to_postgresql.py

echo.
pause

