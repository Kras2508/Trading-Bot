@echo off
echo ========================================
echo Trading Bot Backend - Starting Server
echo ========================================
echo.

cd /d "%~dp0"

REM Check if .env exists
if not exist .env (
    echo Creating .env file...
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
    echo.
)

echo Starting server...
echo.
echo Server will be available at:
echo   - API Docs: http://localhost:8000/docs
echo   - Health: http://localhost:8000/health
echo   - Root: http://localhost:8000/
echo.
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

python run.py

pause

