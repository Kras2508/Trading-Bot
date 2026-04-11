@echo off
echo ========================================
echo Trading Bot Backend - Start Server (with venv)
echo ========================================
echo.

REM Check if venv exists
if not exist venv (
    echo Virtual environment not found!
    echo Please run TAO_VENV_VA_CAI_DAT.bat first
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist .env (
    echo Creating .env file...
    (
        echo # App Configuration
        echo DEBUG=False
        echo.
        echo # Database
        echo DATABASE_URL=sqlite:///./trading_bot.db
        echo.
        echo # Security - CHANGE THESE IN PRODUCTION!
        echo SECRET_KEY=dev-secret-key-change-in-production-min-32-chars-12345
        echo ENCRYPTION_KEY=dev-encryption-key-32-bytes-long-12345678
        echo.
        echo # CORS
        echo CORS_ORIGINS=["*"]
        echo.
        echo # IP Whitelist
        echo ENABLE_IP_WHITELIST=False
        echo.
        echo # Telegram (Optional)
        echo ENABLE_TELEGRAM=False
        echo TELEGRAM_BOT_TOKEN=
        echo TELEGRAM_CHAT_ID=
        echo.
        echo # Exchange
        echo DEFAULT_EXCHANGE=binance
    ) > .env
    echo .env file created!
    echo.
)

echo Starting server...
echo.
echo Server will be available at:
echo   - API Docs: http://localhost:8000/docs
echo   - Health: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run server
python run.py

if errorlevel 1 (
    echo.
    echo ERROR: Could not start server!
    echo.
    pause
)

