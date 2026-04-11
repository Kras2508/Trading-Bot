@echo off
echo ========================================
echo Trading Bot Backend - Quick Start
echo ========================================
echo.

REM Clear Python environment variables
set PYTHONHOME=
set PYTHONPATH=

REM Check if PowerShell script exists and run it
if exist FIX_AND_RUN.ps1 (
    echo Running PowerShell script...
    powershell -ExecutionPolicy Bypass -File FIX_AND_RUN.ps1
    goto :end
)

REM Fallback: Try to create venv and run
echo Creating virtual environment...
python -m venv venv 2>nul

echo Activating venv...
call venv\Scripts\activate.bat 2>nul

echo Installing dependencies...
venv\Scripts\python.exe -m pip install --upgrade pip --quiet
venv\Scripts\python.exe -m pip install -r requirements.txt

if not exist .env (
    echo Creating .env file...
    (
        echo SECRET_KEY=dev-secret-key-change-in-production-min-32-chars-12345
        echo ENCRYPTION_KEY=dev-encryption-key-32-bytes-long-12345678
        echo DATABASE_URL=sqlite:///./trading_bot.db
        echo DEBUG=False
    ) > .env
)

echo.
echo Starting server...
venv\Scripts\python.exe run.py

:end
pause

