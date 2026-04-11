@echo off
chcp 65001 >nul
echo ========================================
echo   DOI DATABASE SANG POSTGRESQL
echo ========================================
echo.
echo Script nay se:
echo   1. Test ket noi PostgreSQL
echo   2. Cap nhat file .env
echo   3. Tao tables trong PostgreSQL
echo.
echo Nhan phim bat ky de tiep tuc...
pause >nul
echo.

python doi_sang_postgresql_auto.py

echo.
pause

