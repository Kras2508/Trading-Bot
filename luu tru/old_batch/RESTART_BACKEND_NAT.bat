@echo off
echo ========================================
echo   Restart Backend cho NAT
echo ========================================
echo.

echo [1/3] Dang kill cac process backend cu...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *run.py*" >nul 2>&1
taskkill /F /IM python.exe /FI "COMMANDLINE eq *uvicorn*" >nul 2>&1
timeout /t 2 /nobreak >nul
echo    [OK] Da kill cac process cu

echo.
echo [2/3] Dang start backend tren 0.0.0.0:8000...
echo    Backend se chay trong cua so moi...
start "Backend API" cmd /k "cd /d %~dp0 && python run.py"
timeout /t 3 /nobreak >nul

echo.
echo [3/3] Kiem tra port 8000...
netstat -ano | findstr :8000
echo.

echo ========================================
echo   Kiem Tra
echo ========================================
echo.
echo Sau 5 giay, kiem tra lai:
timeout /t 5 /nobreak >nul
netstat -ano | findstr :8000
echo.

echo Neu thay "0.0.0.0:8000" thi OK!
echo Neu van thay "127.0.0.1:8000" thi can restart lai.
echo.
pause

