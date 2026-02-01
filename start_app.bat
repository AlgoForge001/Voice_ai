@echo off
echo ===========================================
echo   Starting AI Voice Platform (SaaS)
echo ===========================================

echo 1. Starting Backend Server...
start "TTS Backend API" cmd /k "cd backend && ..\.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo 2. Starting Frontend Dashboard...
start "TTS Frontend UI" cmd /k "cd frontend && npm run dev"

echo.
echo ===========================================
echo   SUCCESS! The app is starting up.
echo ===========================================
echo.
echo   - Backend API:  http://localhost:8000/docs
echo   - Frontend UI:  http://localhost:3000
echo.
echo   (You can minimize this window, but don't close the pop-up terminals)
pause
