@echo off
echo ========================================
echo Trading Bot Backend - Simple Solution
echo ========================================
echo.
echo Installing to user site-packages (no venv needed)
echo.

REM Clear Python env vars
set PYTHONHOME=
set PYTHONPATH=

REM Install to user site-packages
python -m pip install --user --upgrade pip
python -m pip install --user -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed!
    echo.
    pause
    exit /b 1
)

REM Create .env if not exists
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
    echo .env file created!
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Starting server...
echo.
echo Server will be available at:
echo   - API Docs: http://localhost:8000/docs
echo   - Health: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo.

python run.py

pause

