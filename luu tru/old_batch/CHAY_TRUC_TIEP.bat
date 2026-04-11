@echo off
echo ========================================
echo Trading Bot Backend - Run Directly
echo ========================================
echo.

REM Change to a different directory to avoid Python confusion
cd /d "%~dp0"

REM Set Python path directly
set PYTHON_EXE=C:\Users\TGC\AppData\Local\Programs\Python\Python311\python.exe

REM Clear problematic env vars
set PYTHONHOME=
set PYTHONPATH=

REM Try to run with isolated mode
echo Trying to run with isolated Python...
%PYTHON_EXE% -I -c "import sys; print('Python OK:', sys.version)"

if errorlevel 1 (
    echo.
    echo ERROR: Python cannot run in this directory!
    echo.
    echo SOLUTION: Move project to a different location
    echo Example: C:\TradingBot
    echo.
    echo Or reinstall Python properly.
    echo.
    pause
    exit /b 1
)

echo.
echo Python is working! Installing packages...
echo.

REM Install packages using isolated mode
%PYTHON_EXE% -I -m pip install --user --upgrade pip

if errorlevel 1 (
    echo WARNING: pip upgrade failed, continuing anyway...
)

echo.
echo Installing dependencies...
%PYTHON_EXE% -I -m pip install --user -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies!
    echo.
    echo Try installing manually:
    echo   %PYTHON_EXE% -I -m pip install --user fastapi uvicorn sqlalchemy
    echo.
    pause
    exit /b 1
)

REM Create .env if not exists
if not exist .env (
    echo.
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
)

echo.
echo ========================================
echo Starting Server...
echo ========================================
echo.
echo Server will be available at:
echo   - API Docs: http://localhost:8000/docs
echo   - Health: http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run server with isolated mode
%PYTHON_EXE% -I run.py

pause

