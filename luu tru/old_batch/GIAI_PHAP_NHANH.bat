@echo off
echo ========================================
echo GIAI PHAP NHANH - Fix Python Error
echo ========================================
echo.

echo Step 1: Clearing environment variables...
set PYTHONHOME=
set PYTHONPATH=

echo Step 2: Creating virtual environment...
if exist venv (
    echo Removing old venv...
    rmdir /s /q venv
)

python -m venv venv

if errorlevel 1 (
    echo.
    echo ERROR: Cannot create venv. Python may be corrupted.
    echo Please reinstall Python or use a different Python installation.
    echo.
    pause
    exit /b 1
)

echo.
echo Step 3: Activating venv and installing...
call venv\Scripts\activate.bat

python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed!
    pause
    exit /b 1
)

echo.
echo Step 4: Creating .env file...
if not exist .env (
    (
        echo SECRET_KEY=dev-secret-key-change-in-production-min-32-chars-12345
        echo ENCRYPTION_KEY=dev-encryption-key-32-bytes-long-12345678
        echo DATABASE_URL=sqlite:///./trading_bot.db
        echo DEBUG=False
        echo CORS_ORIGINS=["*"]
        echo ENABLE_IP_WHITELIST=False
        echo ENABLE_TELEGRAM=False
    ) > .env
)

echo.
echo ========================================
echo SUCCESS! Everything is ready!
echo ========================================
echo.
echo To start the server, run:
echo   CHAY_VENV.bat
echo.
echo Or manually:
echo   venv\Scripts\activate
echo   python run.py
echo.
pause

