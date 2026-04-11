@echo off
chcp 65001 >nul
echo ========================================
echo   HUONG DAN CAI DAT TREN MAY MOI
echo ========================================
echo.
echo Ban co the xem huong dan chi tiet trong file:
echo   huong dan\CAI_DAT_MAY_MOI.md
echo.
echo Hoac xem huong dan nhanh ben duoi:
echo.
echo ========================================
echo   CAC BUOC CAI DAT
echo ========================================
echo.
echo 1. CAI DAT PYTHON 3.8+
echo    - Tai tu: https://www.python.org/downloads/
echo    - Nho tick "Add Python to PATH"
echo.
echo 2. CAI DAT POSTGRESQL
echo    - Tai tu: https://www.postgresql.org/download/windows/
echo    - Nho password cua user postgres
echo    - Tao database: CREATE DATABASE trading_bot;
echo.
echo 3. CAI DAT NODE.JS (cho frontend)
echo    - Tai tu: https://nodejs.org/
echo.
echo 4. CAI DAT DEPENDENCIES
echo    python -m venv venv
echo    venv\Scripts\activate
echo    pip install -r requirements.txt
echo.
echo 5. TAO FILE .ENV
echo    - Copy file .env.example (neu co)
echo    - Hoac tao file .env voi noi dung:
echo      DATABASE_URL=postgresql://postgres:password@localhost:5432/trading_bot
echo      SECRET_KEY=your-secret-key-min-32-chars
echo      ENCRYPTION_KEY=your-32-byte-key
echo.
echo 6. TAO DATABASE VA TABLES
echo    python doi_sang_postgresql_auto.py
echo.
echo 7. TAO USER DANG NHAP
echo    python tao_user_trong_db.py
echo.
echo 8. CHAY BACKEND
echo    python run.py
echo    Hoac: CHAY_SERVER.bat
echo.
echo 9. CAI FRONTEND (terminal khac)
echo    cd frontend
echo    npm install
echo    npm run dev
echo.
echo 10. DANG NHAP
echo     - Mo: http://localhost:3000
echo     - Username: admin
echo     - Password: admin123
echo.
echo ========================================
echo.
echo Xem huong dan chi tiet: huong dan\CAI_DAT_MAY_MOI.md
echo.
pause

