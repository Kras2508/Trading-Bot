@echo off
echo ========================================
echo Trading Bot Frontend - React
echo ========================================
echo.

cd frontend

echo Checking if node_modules exists...
if not exist node_modules (
    echo Installing dependencies...
    call npm install
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies!
        echo Please make sure Node.js is installed.
        echo.
        pause
        exit /b 1
    )
)

echo.
echo Starting React development server...
echo Frontend will be available at: http://localhost:3000
echo.
echo Make sure backend is running at: http://127.0.0.1:8000
echo.

npm run dev

pause

