@echo off
TITLE Launch TradingView Desktop in Debug Mode (Port 9222)
echo ===================================================
echo   TradingView Desktop Debug Launcher (Port 9222)
echo ===================================================

:: ── Load TRADINGVIEW_EXE_PATH from .env if present ──────────────────────────
set TV_PATH=
for /f "tokens=1,* delims==" %%A in ('findstr /i "TRADINGVIEW_EXE_PATH" "%~dp0..\\.env" 2^>nul') do (
    if /i "%%A"=="TRADINGVIEW_EXE_PATH" set TV_PATH=%%B
)
if defined TV_PATH set TV_PATH=%TV_PATH: =%

:: ── If not set in .env, auto-discover common install locations ──────────────
if not defined TV_PATH (
    if exist "%LOCALAPPDATA%\Programs\TradingView\TradingView.exe" (
        set TV_PATH=%LOCALAPPDATA%\Programs\TradingView\TradingView.exe
    ) else if exist "C:\Program Files\TradingView\TradingView.exe" (
        set TV_PATH=C:\Program Files\TradingView\TradingView.exe
    ) else if exist "D:\Study\TradingView\TradingView.exe" (
        set TV_PATH=D:\Study\TradingView\TradingView.exe
    )
)

if not defined TV_PATH (
    echo [ERROR] TradingView.exe not found!
    echo.
    echo Please set TRADINGVIEW_EXE_PATH in your .env file:
    echo   TRADINGVIEW_EXE_PATH=D:\Study\TradingView\TradingView.exe
    echo.
    pause
    exit /b 1
)

:: Kill any running instance first
taskkill /F /IM TradingView.exe >nul 2>&1
ping -n 3 127.0.0.1 >nul

echo Launching: %TV_PATH%
start "" "%TV_PATH%" --remote-debugging-port=9222

echo.
echo TradingView Desktop is starting with Debug Port 9222.
echo Verify: Open http://127.0.0.1:9222/json/version in your browser.
echo ===================================================
timeout /t 8
