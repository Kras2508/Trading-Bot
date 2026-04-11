@echo off
echo ========================================
echo Trading Bot Backend - Setup and Run
echo ========================================
echo.

echo Step 1: Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo.

echo Step 2: Checking .env file...
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env file and add your configuration!
    echo.
    pause
)

echo Step 3: Starting server...
echo Server will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause

