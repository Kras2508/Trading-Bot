@echo off
echo ========================================
echo   Kiem Tra Va Chay Lai
echo ========================================
echo.

REM Kiểm tra Frontend
echo [1/3] Kiem tra Frontend...
netstat -ano | findstr :3000 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo    [X] Frontend KHONG chay
    echo    Dang khoi dong Frontend...
    cd frontend
    start "Frontend" cmd /k "npm run dev"
    cd ..
    echo    Doi 5 giay...
    timeout /t 5 /nobreak >nul
) else (
    echo    [OK] Frontend dang chay
)

echo.

REM Kiểm tra Backend
echo [2/3] Kiem tra Backend...
curl -s http://127.0.0.1:8000/health >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo    [X] Backend KHONG chay
    echo    Dang khoi dong Backend...
    start "Backend" cmd /k "python run.py"
    echo    Doi 3 giay...
    timeout /t 3 /nobreak >nul
) else (
    echo    [OK] Backend dang chay
)

echo.

REM Kiểm tra Ngrok
echo [3/3] Kiem tra Ngrok...
tasklist | findstr ngrok.exe >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo    [X] Ngrok KHONG chay
    echo    Dang khoi dong Ngrok...
    call CHAY_NGROK_SAFE.bat
) else (
    echo    [OK] Ngrok dang chay
    echo.
    echo    Neu van bi loi, thu restart ngrok:
    echo    KILL_ALL_NGROK.bat
    echo    CHAY_NGROK_SAFE.bat
)

echo.
echo ========================================
echo   Hoan Thanh!
echo ========================================
echo.
echo Kiem tra:
echo - Frontend: http://localhost:3000
echo - Backend: http://127.0.0.1:8000/health
echo - Ngrok Dashboard: http://127.0.0.1:4040
echo.

pause

