@echo off
echo Starting Trading Bot Backend API...
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause

