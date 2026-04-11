@echo off
echo ========================================
echo Trading Bot Backend - Install Dependencies
echo ========================================
echo.

echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing dependencies from requirements.txt...
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed!
    echo.
    echo Please check:
    echo 1. Python is installed correctly
    echo 2. You have internet connection
    echo 3. Try running as Administrator
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Run CHAY_SERVER.bat to start the server
echo 2. Or run: python -m uvicorn app.main:app --reload
echo.
pause

